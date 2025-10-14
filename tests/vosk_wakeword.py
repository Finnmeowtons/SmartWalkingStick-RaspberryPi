from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json

MODEL_PATH = "./smartstick/models/vosk-model-small-en-us-0.15"

# Phonetic approximations for Vosk
KEYWORDS = ["luck as an", "ba wa san", "su nod", "uu lit in", "stop"]

# Map what Vosk hears -> intended command
ALIASES = {
    "luck as an": "lakasan",
    "ba wa san": "hinaan",
    "su nod": "sunod",
    "uu lit in": "ulitin",
    "stop": "tapos"
}

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    q.put(bytes(indata))

# Load model
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, 16000, json.dumps(KEYWORDS))

# Start listening
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("Listening for keywords:", KEYWORDS)
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").strip()
            if text:
                # Normalize
                command = ALIASES.get(text, text)
                print("Heard:", text, "-> Command:", command)

                if command == "lakasan":
                    print("👉 Volume UP")
                elif command == "hinaan":
                    print("👉 Volume DOWN")
                elif command == "sunod":
                    print("👉 Next SMS")
                elif command == "ulitin":
                    print("👉 Repeat SMS")
                elif command == "tapos":
                    print("👉 Stop SMS Mode")
        else:
            partial = json.loads(rec.PartialResult()).get("partial", "")
            if partial:
                print("...", partial)
