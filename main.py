from ytmusicapi import YTMusic
import time
from Setup import setup
from fileinput import FileInput
import os

# def check

yt = YTMusic("browser.json")
library_song_count = {}
playlists = yt.get_library_playlists(limit=None)


if not os.path.isfile("firstSetup"):
    setup()
    with open("firstSetup", "w") as f:
        for playlist in playlists:
            f.write(f"{playlist['playlistId']} {playlist['trackCount']}\n")

with open("firstSetup", "r") as f:
    lines = [line.strip() for line in f]

library_song_count = {}
for entry in lines:
    playlist_id, count = entry.rsplit(" ", 1)
    library_song_count[playlist_id] = int(count)
    
