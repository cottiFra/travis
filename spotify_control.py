import os
import json
import spotipy
import webbrowser
import time
from spotipy.oauth2 import SpotifyOAuth

def carica_credenziali():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                s = data.get("spotify", {})
                return s.get("client_id"), s.get("client_secret"), s.get("redirect_uri")
        except Exception as e:
            print(f"Errore caricamento credenziali Spotify: {e}")
    return "6c35df482c2c4040bf8a0e4bcc52840f", "27a4ac34c87b4a4fb1e790828b9835e1", "http://127.0.0.1:8888/callback"

CLIENT_ID, CLIENT_SECRET, REDIRECT_URI = carica_credenziali()
#mettere qui client id e client secret dati da spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    CLIENT_ID = "your_client_id_here"
    CLIENT_SECRET = "your_client_secret_here"
    redirect_uri=REDIRECT_URI,
    scope="user-modify-playback-state user-read-playback-state"
))

def get_device_id():
    dispositivi = sp.devices()["devices"]
    if not dispositivi:
        webbrowser.open("https://open.spotify.com")
        time.sleep(5)
        dispositivi = sp.devices()["devices"]
    if not dispositivi:
        return None
    return dispositivi[0]["id"]

def play_canzone(query):
    device_id = get_device_id()
    if not device_id:
        return "Nessun dispositivo Spotify trovato. Apri Spotify nel browser."
    risultati = sp.search(q=query, limit=1, type="track")
    tracce = risultati["tracks"]["items"]
    if not tracce:
        return "Canzone non trovata."
    uri = tracce[0]["uri"]
    nome = tracce[0]["name"]
    artista = tracce[0]["artists"][0]["name"]
    sp.start_playback(device_id=device_id, uris=[uri])
    return f"Metto {nome} di {artista}"

def pausa():
    device_id = get_device_id()
    if not device_id:
        return "Nessun dispositivo attivo."
    sp.pause_playback(device_id=device_id)
    return "In pausa."

def riprendi():
    device_id = get_device_id()
    if not device_id:
        return "Nessun dispositivo attivo."
    sp.start_playback(device_id=device_id)
    return "Riprendo."

def prossima():
    device_id = get_device_id()
    if not device_id:
        return "Nessun dispositivo attivo."
    sp.next_track(device_id=device_id)
    return "Prossima canzone."

def precedente():
    device_id = get_device_id()
    if not device_id:
        return "Nessun dispositivo attivo."
    sp.previous_track(device_id=device_id)
    return "Canzone precedente."