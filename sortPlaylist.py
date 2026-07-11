import time
from ytmusicapi.exceptions import YTMusicServerError

def sort_playlist(yt, playlist_id):
    """Sorts the playlists"""
    
    playlist = yt.get_playlist(playlist_id, limit=None)
    tracks = playlist["tracks"]    

    sort_key = lambda t: t["artists"][0]["name"].lower() if t["artists"] else ""

    current_order = [t["setVideoId"] for t in tracks]
    target_order = [t["setVideoId"] for t in sorted(tracks, key=sort_key)]
    count = 0
    for i in range(len(target_order) - 2, -1, -1):
        count+=1
        current_id = target_order[i]
        wanted_next_id = target_order[i + 1]

        idx = current_order.index(current_id)
        if idx + 1 < len(current_order) and current_order[idx + 1] == wanted_next_id:
            continue

        try:
            yt.edit_playlist(playlist_id, moveItem=(current_id, wanted_next_id))
        except YTMusicServerError as e:
            print(f"Move failed, skipping: {e}")
            continue

        current_order.remove(current_id)
        insert_at = current_order.index(wanted_next_id)
        current_order.insert(insert_at, current_id)

        print(f"We did this {count}")
        time.sleep(1)
    print(f"Done sorting '{playlist['title']}' — {count} moves made")
