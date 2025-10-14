import pvporcupine
import sounddevice as sd
import numpy as np
from smartstick.utils.config import WAKEWORD_PATH, PORCUPINE_ACCESS_KEY

porcupine = None
stream = None

def init_porcupine():
    global porcupine, stream
    porcupine = pvporcupine.create(
        access_key=PORCUPINE_ACCESS_KEY,
        keyword_paths=[WAKEWORD_PATH]
    )

    stream = sd.InputStream(
        channels=1,
        samplerate=porcupine.sample_rate,
        blocksize=porcupine.frame_length,
        dtype="int16",
        callback=_callback
    )

def _callback(indata, frames, time, status):
    if status:
        print("Audio status:", status)
    pcm = np.frombuffer(indata, dtype=np.int16)
    result = porcupine.process(pcm)
    if result >= 0:
        _on_wakeword_detected()

wakeword_handler = None  # user-provided function

def set_handler(handler_fn):
    global wakeword_handler
    wakeword_handler = handler_fn

def _on_wakeword_detected():
    if wakeword_handler:
        wakeword_handler()

def start_porcupine():
    if not stream:
        init_porcupine()
    stream.start()
    print("🔊 Listening for wakeword...")

def stop_porcupine():
    if stream:
        stream.stop()

if __name__ == "__main__":
    print("Starting Porcupine...")

    def test_handler():
        print("Wake word detected!")

    set_handler(test_handler)
    start_porcupine()

    try:
        while True:
            sd.sleep(1000)  # keep alive efficiently
    except KeyboardInterrupt:
        print("\nStopping...")
        stop_porcupine()
