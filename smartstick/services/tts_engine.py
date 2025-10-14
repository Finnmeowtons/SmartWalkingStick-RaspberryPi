import numpy as np
import subprocess
import tempfile
import asyncio
import io
import os
import wave
import time
from piper import PiperVoice
from gtts import gTTS
from smartstick.utils.config import PIPER_MODEL
from smartstick.utils.network_utils import ONLINE


# Load Piper model (offline fallback)
voice = PiperVoice.load(PIPER_MODEL)

current_playback = None

def stop_tts():
    global current_playback
    if current_playback and current_playback.poll() is None:
        try:
            current_playback.terminate()
            current_playback.kill()
        except Exception:
            pass
        current_playback = None
        print("🛑 Speech stopped.")

def tts_piper(text: str):
    global current_playback
    print("🔊 Speaking (Offline - Piper)...")
    audio_stream = voice.synthesize(text)

    all_audio = np.concatenate([chunk.audio_float_array for chunk in audio_stream])
    audio_int16 = (all_audio * 32767).astype(np.int16)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        with wave.open(f.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(22050)
            wf.writeframes(audio_int16.tobytes())

        # Non-blocking playback
        stop_tts()
        current_playback = subprocess.Popen(["aplay", "-q", f.name])

        def cleanup():
            try:
                os.unlink(f.name)
            except FileNotFoundError:
                pass
        # spawn cleanup thread
        subprocess.Popen(["/bin/sh", "-c", f"sleep 2; rm -f {f.name}"])

def tts_google(text: str, lang="tl"):
    global current_playback
    print("🔊 Speaking (Online - Google TTS)...")
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)

            # stop_tts()
            current_playback = subprocess.Popen([
                "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
                "-af", "atempo=1.1", tmp.name
            ])

            subprocess.Popen(["/bin/sh", "-c", f"sleep 2; rm -f {tmp.name}"])
    except Exception as e:
        print(f"[TTS] gTTS failed, falling back to Piper. Error: {e}")
        tts_piper(text)

def tts_speak(text: str, lang="tl"):
    """Unified entrypoint: Use Google if online, else Piper fallback."""
    # stop_tts() 
    if ONLINE:
        print("ONLINE TTS")
        tts_google(text, lang=lang)
    else:
        tts_piper(text)

if __name__ == "__main__":
    tts_speak("Hello Dagupan! Shout-out kay Ma'am Angelica.", lang="tl")
