import pvporcupine
import sounddevice as sd
import numpy as np
# from smartstick.utils.config import WAKEWORD_PATH

ACCESS_KEY = "krzPRzjo0OeeBarXT6j7WvgDB2uV04z84VVIUruq848U0/ySrwW/Ow=="

# Initialize Porcupine with a built-in wake word (e.g., "picovoice")
porcupine = pvporcupine.create(access_key=ACCESS_KEY, keyword_paths=["./smartstick/models/wakeword.ppn"])

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    pcm = np.frombuffer(indata, dtype=np.int16)
    result = porcupine.process(pcm)
    if result >= 0:
        print("Wake word detected!")

with sd.InputStream(channels=1, samplerate=porcupine.sample_rate,
                    blocksize=porcupine.frame_length, dtype='int16',
                    callback=audio_callback):
    print("Listening for wake word... (say 'picovoice')")
    sd.sleep(10000) 
