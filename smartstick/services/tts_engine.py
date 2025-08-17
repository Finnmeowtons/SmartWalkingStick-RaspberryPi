import pyaudio
import numpy as np
import time
from piper import PiperVoice
from gtts import gTTS
import tempfile
import os
import playsound
from smartstick.utils.config import PIPER_MODEL

# Load Piper model (offline)
voice = PiperVoice.load(*PIPER_MODEL)

def tts_piper(text):
    print("🔊 Speaking (Offline)...")
    audio_stream = voice.synthesize(text)

    pTTS = pyaudio.PyAudio()
    stream = pTTS.open(format=pTTS.get_format_from_width(2),
                       channels=1,
                       rate=22050,
                       output=True)

    silence_duration = 0.6
    silence_samples = int(silence_duration * 22050)
    stream.write((np.zeros(silence_samples, dtype=np.int16)).tobytes())

    for chunk in audio_stream:
        audio_data = (chunk.audio_float_array * 32767).astype(np.int16).tobytes()
        stream.write(audio_data)

    time.sleep(1)
    stream.stop_stream()
    stream.close()
    pTTS.terminate()

def tts_gtts(text, lang="tl"):
    print("🔊 Speaking (Online - gTTS)...")
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        playsound.playsound(tmp.name)
    os.unlink(tmp.name)
