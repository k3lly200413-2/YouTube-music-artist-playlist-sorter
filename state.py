import json
import os



def get_playlist_id_from_name(playlist_name, playlists):
    return next((p["playlistId"] for p in playlists if p["title"] == playlist_name), None)

def update_song_count(playlists):
    """Updates the count of songs in a PrimoSteup.txt file"""
    print("updating song count")
    with open("PrimoSetup.txt", "w") as f:
        for p in playlists:
            f.write(f"{p['playlistId']} {p.get('count', 0)}\n")

def update_dict():
    """Takes the values from PrimoSetup.txt and updates the dictionary
    
    Return:
    
    library_song_count -- the new dictionarry contaning the values inside of PrimoSetup.txt
    """
    with open("PrimoSetup.txt", "r") as f:
        lines = [line.strip() for line in f]

    library_song_count = {}
    for entry in lines:
        playlist_id, count = entry.rsplit(" ", 1)
        library_song_count[playlist_id] = int(count.replace(",", ""))
    return library_song_count

def save_songs(playlist_data):
    with open("playlists.json", "w") as f:
        json.dump(playlist_data, f, indent=2)

def load_songs():
    """loads song into a playlist.json file
    
    Return:
    
    empty dict -- if .json file is not already created
    
    loaded json -- if .json already exists
    """
    if not os.path.isfile("playlists.json"):
        return {}
    with open("playlists.json") as f:
        return json.load(f)
    
def build_current_state(yt, playlists):
    state = {}
    for p in playlists:
        full_playlist = yt.get_playlist(p["playlistId"], limit=None)
        state[p["playlistId"]] = [t["videoId"] for t in full_playlist["tracks"]]
    return state

def diff_playlist(previous_ids, current_ids):
    """returns the difference between two playlists"""
    previous_set = set(previous_ids)
    current_set = set(current_ids)
    added = [vid for vid in current_ids if vid not in previous_ids]
    removed = previous_set - current_set
    return added, removed
