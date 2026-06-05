# Travis
Local AI assistant with voice control, wake word detection and PC automation

## Description

**Travis** is a local AI voice assistant that listens to your PC and responds to your commands. It doesn't require internet (offline-first) and is completely open source.

### Key Features:
- **Speech Recognition** - Converts your voice to text with Whisper
- **Wake Word Detection** - Activates when you say "Travis"
- **Local AI** - Runs Ollama locally without sending data online
- **Spotify Control** - Play songs, pause, skip tracks
- **Voice Synthesis** - Responds with natural voice
- **PC Automation** - Can execute Python scripts to control your computer
- **GUI Interface** - Modern UI with CustomTkinter

---

## How It Works

### Execution Flow:

1. **Startup**: Travis loads the models (Whisper, Vosk, TTS)
2. **Listening**: Waits for the magic word **"Travis"**
3. **Recording**: Once detected, starts recording your command
4. **Transcription**: Converts audio to text with Whisper
5. **Action**: 
   - If it's a Spotify command → controls Spotify
   - Otherwise → passes the command to Ollama (local AI)
6. **Response**: Executes the action and responds with synthesized voice

### Module Architecture:

| File | Function |
|------|----------|
| `travis.py` | Main entry point (CLI) |
| `travis_core.py` | System core (manages audio, AI, Spotify) |
| `ui.py` | Graphical interface (GUI) |
| `spotify_control.py` | Spotify control module |

---

## Installation

### Prerequisites:
- Python 3.8+
- Working microphone
- CUDA/GPU (optional, but recommended for Whisper)

### Setup:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/travis.git
cd travis

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download Ollama
# https://ollama.ai - and install a model (e.g.: ollama run mistral)

# 5. Configure Spotify credentials (optional)
# Modify config.json with your Spotify data
```

---

## Configuration

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

## Usage

### CLI (Command Line):
```bash
python travis.py
```
- Wait for the "Travis" word
- Say your command
- Wait for the response

### Example Commands:
- "Travis, play Bohemian Rhapsody"
- "Travis, play a random song"
- "Travis, pause"
- "Travis, what time is it?"
- "Travis, tell me a joke"
- "Travis, quit" (to exit)

### GUI:
```bash
python ui.py
```

---

## Security

IMPORTANT: Before pushing to GitHub:
- Don't commit `config.json` with real credentials
- Add `config.json` to `.gitignore`
- The `.gitignore` automatically excludes `venv/` and sensitive files

---

## Dependencies

See [requirements.txt](requirements.txt) for the complete list:
- **Whisper** - Speech recognition (OpenAI)
- **Vosk** - Offline wake word detection
- **Ollama** - Local AI
- **Spotipy** - Spotify API
- **pyttsx3** - Offline voice synthesis
- **CustomTkinter** - Modern UI
- **NumPy, SciPy, SoundDevice** - Audio processing

---

## Contributing

Feel free to fork, open issues, or submit pull requests!

---

## License

See [LICENSE](LICENSE)

---

## Support

If you like this project, leave a star!
