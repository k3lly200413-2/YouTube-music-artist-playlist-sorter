from state import get_playlist_id_from_name
from sortPlaylist import sort_playlist
from ytmusicapi.exceptions import YTMusicServerError
import time

def add_song(yt, playlist, playlists):
    """Syncs a playlist to another when a song has been added to one of the two"""
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
    return target_id
    
def remove_songs(yt, up_to_date_playlist_id, playlists, removed_songs):
    up_to_date_playlist = yt.get_playlist(up_to_date_playlist_id)

    if "ordinata" in up_to_date_playlist["title"]:
        playlist_to_update = up_to_date_playlist["title"].replace("_ordinata", "")
    else:
        playlist_to_update = f"{up_to_date_playlist['title']}_ordinata"

    target_id = get_playlist_id_from_name(playlist_to_update, playlists)

    if target_id is None:
        print(f"Skipping: no matching playlist found for '{playlist_to_update}'")
        return

    target_playlist = yt.get_playlist(target_id, limit=None)
    tracks_to_remove = [t for t in target_playlist["tracks"] if t["videoId"] in removed_songs]

    if not tracks_to_remove:
        print(f"No matching tracks found in '{playlist_to_update}' to remove")
        return

    try:
        yt.remove_playlist_items(target_id, tracks_to_remove)
    except YTMusicServerError as e:
        print(f"Skipping removal because of error: {e}")
        return

    print("sleeping 2 seconds")
    time.sleep(2)
    
