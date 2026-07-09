from ytmusicapi import YTMusic
import time

yt = YTMusic("browser.json")

def sort_playlist(playlist_id):
    playlist = yt.get_playlist(playlist_id, limit=None)
    tracks = playlist["tracks"]

    sort_key = lambda t: t["artists"][0]["name"].lower() if t["artists"] else ""
    
    current_order = [t["setVideoId"] for t in tracks]
    target_order = [t["setVideoId"] for t in sorted(tracks, key=sort_key)]

    moves_made = 0
    for i in range(len(target_order) - 1):
        current_id = target_order[i]
        wanted_next_id = target_order[i + 1]

        idx = current_order.index(current_id)

        # already correctly positioned — skip, no API call needed
        if idx + 1 < len(current_order) and current_order[idx + 1] == wanted_next_id:
            continue

        yt.edit_playlist(playlist_id, moveItem=(current_id, wanted_next_id))
        moves_made += 1

        # update our local copy of the order to match the move we just made
        current_order.remove(current_id)
        insert_at = current_order.index(wanted_next_id)
        current_order.insert(insert_at, current_id)

        time.sleep(0.5)

    print(f"Sorted playlist: {moves_made} moves made out of {len(target_order) - 1} pairs checked")
