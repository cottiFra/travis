import os
import sys
import json
import time
import queue
import tempfile
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import pyttsx3
import ollama

class TravisCore:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.whisper_model = None
        self.modello_vosk = None
        self.recognizer = None
        self.engine = None
        self.memoria = []
        self.parlando = False
        self.tts_queue = queue.Queue()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Errore nel caricamento del file di configurazione: {e}")
        
        return {
            "spotify": {
                "client_id": "6c35df482c2c4040bf8a0e4bcc52840f",
                "client_secret": "27a4ac34c87b4a4fb1e790828b9835e1",
                "redirect_uri": "http://127.0.0.1:8888/callback"
            },
            "whisper": {
                "model_size": "large-v3",
                "device": "cuda",
                "compute_type": "float16"
            },
            "audio": {
                "silence_threshold": 500,
                "silence_duration_seconds": 1.5,
                "max_duration_seconds": 10
            },
            "tts": {
                "rate": 150
            }
        }

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Errore nel salvataggio del file di configurazione: {e}")

    def init_models(self, status_callback=None):
        if status_callback:
            status_callback("Carico Whisper...")
        
        w_cfg = self.config.get("whisper", {})
        from faster_whisper import WhisperModel
        self.whisper_model = WhisperModel(
            w_cfg.get("model_size", "large-v3"),
            device=w_cfg.get("device", "cuda"),
            compute_type=w_cfg.get("compute_type", "float16")
        )

        if status_callback:
            status_callback("Carico wake word...")
            
        from vosk import Model, KaldiRecognizer
        self.modello_vosk = Model("vosk-model-small-it-0.22")
        self.recognizer = KaldiRecognizer(self.modello_vosk, 16000)

        if status_callback:
            status_callback("Carico TTS...")
            
        import threading
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()
        time.sleep(0.5)
        
        if status_callback:
            status_callback("Modelli pronti!")

    def _tts_worker(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.config.get("tts", {}).get("rate", 150))
        except Exception as e:
            print(f"Errore inizializzazione TTS: {e}")
            self.engine = None

        while True:
            item = self.tts_queue.get()
            if item is None:
                break
            testo, on_start, on_end, event = item
            
            self.parlando = True
            if on_start:
                try:
                    on_start()
                except Exception as e:
                    print(f"Errore on_start callback: {e}")
                    
            if self.engine:
                try:
                    self.engine.say(testo)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"Errore durante pyttsx3 speaking: {e}")
                    
            self.parlando = False
            if on_end:
                try:
                    on_end()
                except Exception as e:
                    print(f"Errore on_end callback: {e}")
                    
            if event:
                event.set()
                
            self.tts_queue.task_done()

    def parla(self, testo, on_start=None, on_end=None, wait=True):
        print(f"Travis: {testo}")
        import threading
        event = threading.Event() if wait else None
        self.tts_queue.put((testo, on_start, on_end, event))
        if wait:
            event.wait()

    def ascolta_con_silenzio(self, status_callback=None):
        soglia_silenzio = self.config.get("audio", {}).get("silence_threshold", 500)
        durata_silenzio_max = self.config.get("audio", {}).get("silence_duration_seconds", 1.5)
        durata_max = self.config.get("audio", {}).get("max_duration_seconds", 10)
        fs = 16000
        
        q_audio = queue.Queue()
        
        def callback(indata, frames, time_info, status):
            q_audio.put(indata.copy())
            
        if status_callback:
            status_callback("In ascolto...")
            
        audio_registrato = []
        silence_samples = 0
        soglia_campioni_silenzio = int(durata_silenzio_max * fs)
        max_campioni = int(durata_max * fs)
        campioni_totali = 0
        
        with sd.InputStream(samplerate=fs, channels=1, dtype='int16', callback=callback):
            start_time = time.time()
            while True:
                try:
                    chunk = q_audio.get(timeout=0.1)
                    audio_registrato.append(chunk)
                    campioni_totali += len(chunk)
                    
                    rms = np.sqrt(np.mean(chunk.astype(np.float64)**2)) if len(chunk) > 0 else 0
                    
                    if rms < soglia_silenzio:
                        silence_samples += len(chunk)
                    else:
                        silence_samples = 0
                        
                    if silence_samples >= soglia_campioni_silenzio:
                        if status_callback:
                            status_callback("Silenzio rilevato...")
                        break
                        
                    if campioni_totali >= max_campioni:
                        if status_callback:
                            status_callback("Tempo massimo raggiunto...")
                        break
                except queue.Empty:
                    if time.time() - start_time > durata_max:
                        break
                        
        if not audio_registrato:
            return ""
            
        audio_data = np.concatenate(audio_registrato, axis=0)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            nome_file = f.name
            
        try:
            wav.write(nome_file, fs, audio_data)
            if status_callback:
                status_callback("Elaboro audio...")
            segmenti, _ = self.whisper_model.transcribe(nome_file, language="it", beam_size=5)
            testo = " ".join([s.text for s in segmenti]).strip()
        finally:
            if os.path.exists(nome_file):
                os.unlink(nome_file)
                
        return testo

    def aspetta_wake_word(self, active_check_callback=None, on_detect_callback=None, stop_event=None):
        q = queue.Queue()

        def callback(indata, frames, time_info, status):
            q.put(bytes(indata))

        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            while True:
                if stop_event and stop_event.is_set():
                    break
                if active_check_callback and not active_check_callback():
                    time.sleep(0.2)
                    while not q.empty():
                        try:
                            q.get_nowait()
                        except queue.Empty:
                            break
                    continue
                try:
                    data = q.get(timeout=0.2)
                except queue.Empty:
                    continue
                if self.recognizer.AcceptWaveform(data):
                    risultato = json.loads(self.recognizer.Result())
                    testo = risultato.get("text", "").lower()
                    if on_detect_callback:
                        on_detect_callback()
                    return True
        return False

    def chiedi_ai(self, comando):
        self.memoria.append({"role": "user", "content": comando})

        if len(self.memoria) > 20:
            self.memoria = self.memoria[-20:]

        messaggi = [
            {
                "role": "system",
                "content": """Sei Travis, un assistente AI che controlla il PC.
Quando ricevi un comando, rispondi SOLO con codice Python eseguibile, nient'altro.
Niente spiegazioni, niente testo, solo codice Python puro.
Usa librerie standard come webbrowser, os, subprocess, shutil.
Il Desktop dell'utente si trova in C:\\Users\\fraco\\OneDrive\\Desktop"""
            }
        ] + self.memoria

        try:
            risposta = ollama.chat(model="qwen2.5:7b", messages=messaggi)
            testo = risposta["message"]["content"]
            self.memoria.append({"role": "assistant", "content": testo})
            return testo
        except Exception as e:
            print(f"Errore chiamata Ollama: {e}")
            return f"print('Errore di comunicazione con Ollama: {e}')"

    def pulisci_codice(self, testo):
        testo = testo.replace("```python", "").replace("```", "")
        return testo.strip()

    def esegui_codice_sicuro(self, codice):
        import os, sys, webbrowser, subprocess, shutil, datetime, time
        globals_dict = {
            "__builtins__": __builtins__,
            "os": os,
            "sys": sys,
            "webbrowser": webbrowser,
            "subprocess": subprocess,
            "shutil": shutil,
            "datetime": datetime,
            "time": time
        }
        exec(codice, globals_dict)

    def gestisci_spotify(self, comando):
        import spotify_control
        import re
        c = comando.lower()
        if "pausa" in c or "stop" in c:
            return spotify_control.pausa()
        elif "riprendi" in c or "play" in c:
            return spotify_control.riprendi()
        elif "prossima" in c or "avanti" in c:
            return spotify_control.prossima()
        elif "precedente" in c or "indietro" in c:
            return spotify_control.precedente()
        elif any(p in c for p in ["metti", "ascolta", "canzone", "musica", "mettimi"]):
            # Rimuove le parole con spazi: " di ", " da ", ecc.
            c = c.replace("metti", "").replace("ascolta", "").replace("canzone", "").replace("musica", "").replace("mettimi", "")
            return spotify_control.play_canzone(c.strip())
        return None
