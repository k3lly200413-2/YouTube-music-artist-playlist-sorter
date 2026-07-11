from ytmusicapi import YTMusic
import os
import time
from state import *
from sync import add_song, remove_songs
from Setup import setup

yt = YTMusic("browser.json")

SKIP_IDS = {"LM", "SS"}
SKIP_PREFIXES = ("RD",)

playlists = yt.get_library_playlists(limit=None)
print(len(playlists))

if not os.path.isfile("PrimoSetup.txt"):
    setup()
    update_song_count(playlists)

library_song_count = update_dict()
previous_state = load_songs()

while True:
    playlists = yt.get_library_playlists(limit=None)
    for p in playlists:
        p["count"] = int(str(p.get("count", 0)).replace(",", ""))

    updated_playlists = [
        p["playlistId"] for p in playlists if
        (p["count"] != library_song_count.get(p["playlistId"], p["count"]))
        and (p["playlistId"] not in SKIP_IDS)
        and ("jody" not in p["title"].lower())
        and ("Recap" not in p["title"])
        and (not p["playlistId"].startswith(SKIP_PREFIXES))
    ]

    print(f"updated songs, playlists with different song are : {len(updated_playlists)}")

    for playlist_id in updated_playlists:
        current_ids = [t["videoId"] for t in yt.get_playlist(playlist_id, limit=None)["tracks"]]
        previous_ids = previous_state.get(playlist_id, current_ids)
        added, removed = diff_playlist(previous_ids, current_ids)

        if added:
            target_id = add_song(yt, playlist_id, playlists)
            if target_id:
                target_ids = [t["videoId"] for t in yt.get_playlist(target_id, limit=None)["tracks"]]
                previous_state[target_id] = target_ids
        if removed:
            target_id = remove_songs(yt, playlist_id, playlists, list(removed))
            if target_id:
                target_ids = [t["videoId"] for t in yt.get_playlist(target_id, limit=None)["tracks"]]
                previous_state[target_id] = target_ids
        previous_state[playlist_id] = current_ids

    save_songs(previous_state)
    update_song_count(playlists)
    library_song_count = update_dict()
    time.sleep(5)
