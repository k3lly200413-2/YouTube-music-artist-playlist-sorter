from Setup import setup
from ytmusicapi import YTMusic
import os
import time
from sortPlaylist import sort_playlist

yt = YTMusic("browser.json")

def get_playlist_id_from_name(playlist_name, playlists):
    return next((p["playlistId"] for p in playlists if p["title"] == playlist_name), None)

def update_song_count(playlists):
    with open("PrimoSetup.txt", "w") as f:
        for p in playlists:
            f.write(f"{p["playlistId"]} {p.get("count", 0)}\n")

def update_dict():
    with open("PrimoSetup.txt", "r") as f:
        lines = [line.strip() for line in f]
        
    library_song_count = {}
    for entry in lines:
        playlist_id, count = entry.rsplit(" ", 1)
        library_song_count[playlist_id] = int(count)
    return library_song_count

# setup()
playlists = yt.get_library_playlists(limit=None)


if not os.path.isfile("PrimoSetup.txt"):
    update_song_count(playlists)

library_song_count = update_dict()


while True:
    playlists = yt.get_library_playlists(limit=None)

    updated_playlists = [
        p["playlistId"] for p in playlists if 
        p.get("count", 0) != library_song_count.get(p["playlistId"], p.get("count", 0))
    ]
    
    for playlist in updated_playlists:
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
            continue

        yt.add_playlist_items(target_id, [last_track_id])
        sort_playlist(playlist)
        
    update_song_count(playlists)      # NOW persist current counts to disk
    library_song_count = update_dict()  # NOW refresh in-memory dict to match
    time.sleep(180)