import os
from pocketsphinx import LiveSpeech

KEYWORDS_FILE = "tests/keywords.list"

def start_pocketsphinx():
    speech = LiveSpeech(
        kws=KEYWORDS_FILE,       # keyword spotting mode
        lm=False,                # disable full language model
        dic="/usr/share/pocketsphinx/model/en-us/cmudict-en-us.dict"  # default dictionary
    )

    print("🎤 Listening for keywords...")

    for phrase in speech:
        text = str(phrase).lower().strip()
        print("Heard:", text)

        if "lakasan" in text:
            print("👉 Volume UP")
        elif "hinaan" in text:
            print("👉 Volume DOWN")
        elif "sunod" in text:
            print("👉 Next SMS")
        elif "ulitin" in text:
            print("👉 Repeat SMS")
        elif "tapos" in text:
            print("👉 Stop SMS Mode")

if __name__ == "__main__":
    start_pocketsphinx()
