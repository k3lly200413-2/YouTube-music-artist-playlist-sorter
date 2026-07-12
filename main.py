from ytmusicapi import YTMusic
import os
import time
import random
import logging
from state import *
from sync import add_song, remove_songs
from Setup import setup
from paho.mqtt import client as mqtt_client
import requests
from dotenv import load_dotenv
import os


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "Not_Set")
CHAT_ID = os.getenv("CHAT_ID", "Not_Set")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(os.getenv("BROKER", "None_Set"))
broker = os.getenv("BROKER", "None_Set")
port = 8883
client_id = f"python-mqtt-{random.randint(0, 1000)}"
username = os.getenv("BROKER_USER", "None_Set")
password = os.getenv("BROKER_PASSWORD", "None_Set")

SKIP_IDS = {"LM", "SS"}
SKIP_PREFIXES = ("RD",)


def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    logger.info("Disconnected with reason code: %s", reason_code)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logger.info("Connected to MQTT Broker!")
    else:
        logger.error(f"Failed to connect, return code {reason_code}")


def connect_mqtt():
    client = mqtt_client.Client(
        client_id=client_id,
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
    )

    client.username_pw_set(username, password)
    client.tls_set()  # required for port 8883

    # LWT must be set BEFORE connect() — it's part of the initial CONNECT packet
    client.will_set("ytmusic/Sasha/status", payload="offline", qos=1, retain=True)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.connect(broker, port)
    return client


def sync_loop(client):
    yt = YTMusic("browser.json")

    playlists = yt.get_library_playlists(limit=None)

    if not os.path.isfile("PrimoSetup.txt"):
        setup()
        update_song_count(playlists)

    library_song_count = update_dict()
    previous_state = load_songs()

    while True:
        playlists = yt.get_library_playlists(limit=None)
        playlists = {}
        print(len(playlists))

        if len(playlists) == 0:
            send_telegram_alert("⚠️ YT Music sync: playlist list is empty — browser.json likely expired.")
            return

        client.publish("ytmusic/Sasha/status", payload="online", qos=1, retain=True)

        for p in playlists:
            p["count"] = int(str(p.get("count", 0)).replace(",", ""))

        updated_playlists = [
            p["playlistId"] for p in playlists if
            (p["count"] != library_song_count.get(p["playlistId"], p["count"]))
            and (p["playlistId"] not in SKIP_IDS)
            and ("recap" not in p["title"].lower())
            and (not p["playlistId"].startswith(SKIP_PREFIXES))
        ]

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


if __name__ == "__main__":
    client = connect_mqtt()
    client.loop_start()  # background thread handles MQTT networking

    try:
        sync_loop(client)  # main thread runs the actual sync work
    except Exception as e:
        send_telegram_alert(f"🔴 YT Music sync crashed: {e}")
        raise
    finally:
        client.loop_stop()
        client.disconnect()