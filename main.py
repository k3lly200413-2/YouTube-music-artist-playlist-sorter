from ytmusicapi import YTMusic
import os
import time
from state import *
from sync import add_song, remove_songs
from Setup import setup

yt = YTMusic("browser.json")

SKIP_IDS = {"LM", "SS"}
SKIP_PREFIXES = ("RD",)

# all library info
playlists = yt.get_library_playlists(limit=None)
# currently for debugging reasons
# for future will be useful to check if request headers are expireds
print(len(playlists))

if not os.path.isfile("PrimoSetup.txt"):
    setup()
    update_song_count(playlists)

library_song_count = update_dict()
previous_state = load_songs()

while True:
    setup()
    update_song_count(playlists)
    # constantly check for a new playlist to be created
    playlists = yt.get_library_playlists(limit=None)
    # transforms all counts to ints
    for p in playlists:
        p["count"] = int(str(p.get("count", 0)).replace(",", ""))

    # we only want certain playlists
    updated_playlists = [
        p["playlistId"] for p in playlists if
        (p["count"] != library_song_count.get(p["playlistId"], p["count"]))
        and (p["playlistId"] not in SKIP_IDS)
        and ("recap" not in p["title"].lower())
        and (not p["playlistId"].startswith(SKIP_PREFIXES))
    ]

    for playlist_id in updated_playlists:
        # fetch every track's videoId currently in this playlist, in its current order
        current_ids = [t["videoId"] for t in yt.get_playlist(playlist_id, limit=None)["tracks"]]

        # fall back to current_ids if we've never seen this playlist before (e.g. new playlist),
        # so the diff below comes back empty instead of flagging everything as "added"
        previous_ids = previous_state.get(playlist_id, current_ids)

        # compare current vs. last-known state to find exactly what changed
        added, removed = diff_playlist(previous_ids, current_ids)

        if added:
            # sync the new track(s) into the counterpart (_ordinata <-> non-_ordinata) playlist
            target_id = add_song(yt, playlist_id, playlists)

            if target_id:
                # the target playlist's contents just changed too (it received the new track),
                # so refresh its state now — otherwise next loop pass would see this addition
                # as "new" from the target's own perspective and could re-sync it back, causing a duplicate
                target_ids = [t["videoId"] for t in yt.get_playlist(target_id, limit=None)["tracks"]]
                previous_state[target_id] = target_ids

        if removed:
            # mirror the removal into the counterpart playlist
            target_id = remove_songs(yt, playlist_id, playlists, list(removed))

            if target_id:
                # same reasoning as above: the target's state changed too, keep it in sync
                # to avoid re-detecting this removal (or a false "addition") next pass
                target_ids = [t["videoId"] for t in yt.get_playlist(target_id, limit=None)["tracks"]]
                previous_state[target_id] = target_ids

        # record this playlist's current state as the new baseline for the next comparison
        previous_state[playlist_id] = current_ids

    save_songs(previous_state)
    update_song_count(playlists)
    library_song_count = update_dict()
    time.sleep(5)
