import json
import sys
import time
import asyncio
from smartstick.utils.config import WAKEWORDS
from smartstick.interfaces.gemini import ask_gemini
from smartstick.services.stt_engine import stream, recognizer
from smartstick.services.tts_engine import tts_speak
from smartstick.services.music_player import play_song_youtube, stop_music
from smartstick.hardware.vision import detect_objects_and_speak
# from smartstick.hardware.gps import
from smartstick.core import preload

preload.preload_all()

def trigger_object_detection():
    asyncio.run(detect_objects_and_speak())

print("\nWaiting for WakeWord...")

isChatActive = False
last_sound_time = time.time()

while True:
    data = stream.read(8192)
    if recognizer.AcceptWaveform(data):
        result_json = json.loads(recognizer.Result())
        text = result_json.get('text', '')
        if text:
            print(text)
            last_sound_time = time.time()

            if isChatActive:
                stream.stop_stream()
                text_lower = text.lower()

                if "kumare" in text_lower or "kumpare" in text_lower:
                    prompt = text_lower.replace("kumare", "").replace("kumpare", "").strip()
                    reply = ask_gemini(prompt)
                    tts_speak(reply, lang="tl")  # Online TTS for Tagalog
                elif "music" in text_lower:
                    play_song_youtube(
                        text_lower.replace("makinig ng music", "")
                                  .replace("listen to music", "")
                                  .replace("tugtug", "")
                                  .replace("tugtog", "")
                                  .strip()
                    )
                elif "stop" in text_lower:
                    stop_music()
                elif "nasa harap" in text_lower:
                    trigger_object_detection()
                else:
                    tts_speak("Hindi kita gets bes.")

                stream.start_stream()
                continue

            if any(w in text.lower() for w in WAKEWORDS):
                print("\n🎤 Speak now...")
                isChatActive = True
    else:
        partial = json.loads(recognizer.PartialResult()).get('partial', '')
        sys.stdout.write('\r' + partial)
        sys.stdout.flush()

    if time.time() - last_sound_time > 7 and isChatActive:
        isChatActive = False
        print("\nWaiting for WakeWord...")