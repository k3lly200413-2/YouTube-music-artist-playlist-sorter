from ytmusicapi import YTMusic
import time

yt = YTMusic("browser.json")

# youtube generated playlists
SKIP_IDS = {"LM", "SS"}
SKIP_PREFIXES = ("RD",)

def add_items_with_retry(playlist_id, video_ids, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            yt.add_playlist_items(playlist_id, video_ids)
            return True
        except Exception as e:
            print(f"    Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                wait = 3 * attempt  # backoff: 3s, 6s, 9s...
                print(f"    Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"    Giving up on this chunk after {max_retries} attempts.")
                return False

def check_new_playlist(playlists, playlist_id, title):
    new_title = f"{title}_ordinata"
    if playlist_id in SKIP_IDS or playlist_id.startswith(SKIP_PREFIXES):
        # print(f"Skipping auto/radio playlist: {title}")
        return False
        
    if "_ordinata" in title:
        # print(f"Skipping already-sorted playlist: {title}")
        return False
        
    if "recap" in title.lower():
        # print(f"Skipping, recap playlist, we don't want it: {title}")
        return False
                    
    if any(existing['title'] == new_title for existing in playlists):
        # print(f"'{new_title}' already exists, skipping.")
        return False
    
    return True

def create_new_playlist(title):
    return yt.create_playlist(
            f"{title}_ordinata",
            description=f"Ordinata per artista da '{title}'",
            privacy_status="PRIVATE"
        )

def populate_playlist(video_ids, new_playlist_id, title):
    chunk_size = 50
    for i in range(0, len(video_ids), chunk_size):
        chunk = video_ids[i:i + chunk_size]
        success = add_items_with_retry(new_playlist_id, chunk)
        if success:
            print(f"  Added {len(chunk)} tracks ({i + len(chunk)}/{len(video_ids)}) for {title}")
        else:
            print(f"  FAILED chunk {i}-{i+len(chunk)} for '{title}', continuing anyway.")
        time.sleep(1.5)

def setup():
    """Meant to be run only the first time a program is run.
    This method will create new sorted playlists of all playlists
    which still don't have a sorted version.
    
    """
    playlists = yt.get_library_playlists()

    for p in playlists:
        playlist_id = p['playlistId']
        title = p['title']
        
        if(not check_new_playlist(playlists, playlist_id, title)):
            continue

        print(f"Processing '{title}' -> '{title}_ordinata'")

        playlist_data = yt.get_playlist(playlist_id, limit=None)
        tracks = playlist_data.get("tracks", [])

        valid_tracks = [t for t in tracks if t.get("artists") and t.get("videoId")]
        sorted_tracks = sorted(valid_tracks, key=lambda t: t["artists"][0]["name"].lower())

        if not sorted_tracks:
            print(f"  No valid tracks in '{title}', skipping playlist creation.")
            continue

        # Dedupe while preserving sorted order
        seen = set()
        video_ids = []
        for t in sorted_tracks:
            vid = t["videoId"]
            if vid not in seen:
                seen.add(vid)
                video_ids.append(vid)

        new_playlist_id = create_new_playlist(title)

        # give YouTube a moment to fully register the new playlist
        time.sleep(2)

        # divide into chunks to avoid too many api calls in quick succession
        populate_playlist(video_ids, new_playlist_id, title)

        print(f"  Done: '{title}_ordinata' processed.\n")

    print("All playlists processed.")

if __name__ == "__main__":
    setup()
