# Travis
Local AI assistant with voice control, wake word detection and PC automation

## Descrizione

**Travis** è un assistente vocale AI locale che ascolta il tuo pc e risponde ai tuoi comandi. Non richiede internet (offline-first) ed è completamente open source.

### Funzionalità principali:
- **Riconoscimento vocale** - Converte la tua voce in testo con Whisper
- **Wake word detection** - Si attiva quando dici "Travis"
- **AI locale** - Esegue Ollama localmente senza inviare dati online
- **Controllo Spotify** - Riproduci canzoni, pausa, salta tracce
- **Sintesi vocale** - Risponde con voce naturale
- **Automazione PC** - Può eseguire script Python per controllare il tuo computer
- **Interfaccia GUI** - UI moderna con CustomTkinter

---

## Come funziona

### Flusso di esecuzione:

1. **Avvio**: Travis carica i modelli (Whisper, Vosk, TTS)
2. **Ascolto**: Rimane in ascolto della parola magica **"Travis"**
3. **Registrazione**: Una volta rilevata, inizia a registrare il tuo comando
4. **Trascrizione**: Converte l'audio in testo con Whisper
5. **Azione**: 
   - Se è un comando Spotify → controlla Spotify
   - Altrimenti → passa il comando a Ollama (AI locale)
6. **Risposta**: Esegue l'azione e ti risponde con voce sintetizzata

### Architettura moduli:

| File | Funzione |
|------|----------|
| `travis.py` | Punto di ingresso principale (CLI) |
| `travis_core.py` | Core del sistema (gestisce audio, AI, Spotify) |
| `ui.py` | Interfaccia grafica (GUI) |
| `spotify_control.py` | Modulo dedicato al controllo Spotify |
| `primoscript.py` | Script per azioni iniziali |

---

## Installazione

### Prerequisiti:
- Python 3.8+
- Microfono funzionante
- CUDA/GPU (opzionale, ma consigliato per Whisper)

### Setup:

```bash
# 1. Clona il repository
git clone https://github.com/tuousername/travis.git
cd travis

# 2. Crea un virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. Scarica Ollama
# https://ollama.ai - e installa un modello (es: ollama run mistral)

# 5. Configura le credenziali Spotify (opzionale)
# Modifica config.json con i tuoi dati Spotify
```

---

## Configurazione

### File `config.json`:
```json
{
  "spotify": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
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
  }
}
```

---

## Utilizzo

### CLI (Command Line):
```bash
python travis.py
```
- Aspetta la parola "Travis"
- Dì il tuo comando
- Aspetta la risposta

### Comandi di esempio:
- "Travis, riproduci Bohemian Rhapsody"
- "Travis, metti una canzone random"
- "Travis, pausa"
- "Travis, che ora è?"
- "Travis, dimmi una barzelletta"
- "Travis, spegniti" (per chiudere)

### GUI:
```bash
python ui.py
```

---

## Sicurezza

IMPORTANTE: Prima di pushare su GitHub:
- Non commitare `config.json` con credenziali reali
- Aggiungi `config.json` al `.gitignore`
- Il `.gitignore` esclude automaticamente `venv/` e file sensibili

---

## Dipendenze

Vedi [requirements.txt](requirements.txt) per la lista completa:
- **Whisper** - Riconoscimento vocale (OpenAI)
- **Vosk** - Wake word detection offline
- **Ollama** - AI locale
- **Spotipy** - API Spotify
- **pyttsx3** - Sintesi vocale offline
- **CustomTkinter** - UI moderna
- **NumPy, SciPy, SoundDevice** - Elaborazione audio

---

## Contribuire

Sei libero di fare fork, aprire issues o inviare pull requests!

---

## Licenza

Vedi [LICENSE](LICENSE)

---

## Supporto

Se ti piace questo progetto, lascia una stella!
