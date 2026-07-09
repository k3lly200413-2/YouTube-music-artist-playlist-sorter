from Setup import setup
from ytmusicapi import YTMusic
import os

yt = YTMusic("browser.json")

setup()
playlists = yt.get_library_playlists(limit=None)


if not os.path.isfile("PrimoSetup"):
    with open("PrimoSetup", "w") as f:
        for p in playlists:
            f.write(f"{p["playlistId"]} {p["count"]}\n")


