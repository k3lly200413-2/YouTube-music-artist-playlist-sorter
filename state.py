def get_playlist_id_from_name(playlist_name, playlists):
    return next((p["playlistId"] for p in playlists if p["title"] == playlist_name), None)

def update_song_count(playlists):
    print("updating song count")
    with open("PrimoSetup.txt", "w") as f:
        for p in playlists:
            f.write(f"{p['playlistId']} {p.get('count', 0)}\n")

def update_dict():
    with open("PrimoSetup.txt", "r") as f:
        lines = [line.strip() for line in f]

    library_song_count = {}
    for entry in lines:
        playlist_id, count = entry.rsplit(" ", 1)
        library_song_count[playlist_id] = int(count.replace(",", ""))
    return library_song_count