from ytmusicapi import YTMusic
import os
import time
from state import update_song_count, update_dict
from sync import sync
from Setup import setup

yt = YTMusic("browser.json")

SKIP_IDS = {"LM", "SS"}
SKIP_PREFIXES = ("RD",)

playlists = yt.get_library_playlists(limit=None)

if not os.path.isfile("PrimoSetup.txt"):
    setup()
    update_song_count(playlists)

library_song_count = update_dict()

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
    
    for playlist in updated_playlists:
        sync(yt, playlist, playlists)

    update_song_count(playlists)
    library_song_count = update_dict()
    time.sleep(15)