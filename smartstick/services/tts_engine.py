import numpy as np
import subprocess
import tempfile
import os
import wave
from piper import PiperVoice
from gtts import gTTS
from smartstick.utils.config import PIPER_MODEL
from smartstick.utils.network_utils import ONLINE

# Load Piper model (offline fallback)
voice = PiperVoice.load(PIPER_MODEL)

def tts_piper(text: str):
    print("🔊 Speaking (Offline - Piper)...")
    audio_stream = voice.synthesize(text)

    # Convert to numpy
    all_audio = np.concatenate([chunk.audio_float_array for chunk in audio_stream])
    audio_int16 = (all_audio * 32767).astype(np.int16)

    # Save temporary WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
        with wave.open(f.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(22050)
            wf.writeframes(audio_int16.tobytes())

        subprocess.run(["aplay", "-q", f.name])

def tts_google(text: str, lang="tl"):
    print("🔊 Speaking (Online - Google TTS)...")
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            subprocess.run([
                "ffplay", "-nodisp", "-autoexit",
                "-af", "atempo=1.5", tmp.name
            ])
        os.unlink(tmp.name)
    except Exception as e:
        print(f"[TTS] gTTS failed, falling back to Piper. Error: {e}")
        tts_piper(text)

def tts_speak(text: str, lang="tl"):
    """Unified entrypoint: Use Google if online, else Piper fallback."""
    if ONLINE:
        tts_google(text, lang=lang)
    else:
        tts_piper(text)

if __name__ == "__main__":
    tts_speak("Hello Dagupan! Testing hybrid TTS.", lang="tl")
