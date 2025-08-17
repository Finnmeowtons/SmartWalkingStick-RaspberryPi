import os
import pyaudio
from vosk import Model, KaldiRecognizer
from smartstick.utils.config import VOSK_MODEL_PATH

if not os.path.exists(VOSK_MODEL_PATH):
    raise FileNotFoundError(f"Vosk model not found at {VOSK_MODEL_PATH}")

model_vosk = Model(VOSK_MODEL_PATH)
p = pyaudio.PyAudio()
chunk_size = 8192
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=chunk_size)
recognizer = KaldiRecognizer(model_vosk, 16000)