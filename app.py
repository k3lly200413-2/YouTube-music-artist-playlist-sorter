from ytmusicapi import YTMusic
import time

def get_playlist_id_by_name(name, playlist):
    #playlists = yt.get_library_playlists(limit=None)
    print(playlist)
    for playlists in playlist:
        print(playlists["title"].lower())
        print(name.lower())
        if playlists["title"].lower() == name.lower():
            print("DONE")
            return playlists["playlistId"]
    return None

yt = YTMusic("browser.json")

playlists = yt.get_library_playlists()

for p in playlists:
    print(p['playlistId'], '-', p['title'])

yt.create_playlist("OrdinataPerArtisti",
                   "Dovrebbe essere ordinata per artista", "PUBLIC")

tracks = yt.get_playlist("PLI5Ovv3GjXJ-lC7yTiahaHEMOKEL8wIxp", None)["tracks"]

print(tracks)

sorted_tracks = sorted(tracks, key=lambda t: t["artists"][0]["name"].lower())
sorted_tracks_new = []
for t in sorted_tracks:
    if t != None:
        sorted_tracks_new.append(t)

target_playlist_id = get_playlist_id_by_name("OrdinataPerArtisti", playlists)

for track in sorted_tracks_new:
    time.sleep(1)
    yt.add_playlist_items(target_playlist_id, [track["videoId"]])
    print(track["videoId"])