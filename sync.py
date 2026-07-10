from state import get_playlist_id_from_name
from sortPlaylist import sort_playlist
from ytmusicapi.exceptions import YTMusicServerError
import time

def sync(yt, playlist, playlists):
    print("We got to sync")
    current_playlist = yt.get_playlist(playlist)
    if "ordinata" in current_playlist["title"]:
        other_playlist = current_playlist["title"].replace("_ordinata", "")
    else:
        other_playlist = f"{current_playlist['title']}_ordinata"

    full_playlist = yt.get_playlist(playlist, limit=None)
    last_track_id = full_playlist["tracks"][-1]["videoId"]

    target_id = get_playlist_id_from_name(other_playlist, playlists)
    if target_id is None:
        print(f"Skipping: no matching playlist found for '{other_playlist}'")
        return

    try:
        yt.add_playlist_items(target_id, [last_track_id])
    except YTMusicServerError as e:
        print(f"Skipping track because of error: {e}")
        return
    
    print("Sleeping for 2s")
    time.sleep(2)
    sort_playlist(yt, playlist if "ordinata" in current_playlist["title"] else target_id)
    