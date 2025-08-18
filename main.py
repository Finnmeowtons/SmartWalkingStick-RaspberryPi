import json
import sys
import time
import asyncio
from smartstick.utils.config import WAKEWORDS
from smartstick.interfaces.gemini import ask_gemini, polish_music_command
from smartstick.services.stt_engine import stream, recognizer
from smartstick.services.tts_engine import tts_speak, stop_tts
from smartstick.services.music_player import play_song_youtube, stop_music, current_volume, decrease_volume, increase_volume
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
            text_lower = text.lower()

            # --- Always-on commands ---
            if any(kw in text_lower for kw in ["volume increase", "increase volume", "volume up", "up volume", "lakasan"]):
                increase_volume()
                continue  # skip wake word check
            elif any(kw in text_lower for kw in ["volume decrease", "decrease volume", "volume down", "bawasan", "hinaan"]):
                decrease_volume()
                continue
            elif "stop" in text_lower:
                stop_music()
                stop_tts()
                continue

            if isChatActive:
                stream.stop_stream()

                if "kumare" in text_lower or "kumpare" in text_lower:
                    prompt = text_lower.replace("kumare", "").replace("kumpare", "").strip()
                    reply = ask_gemini(prompt)
                    tts_speak(reply, lang="tl")  # Online TTS for Tagalog
                elif "music" in text_lower:
                    play_song_youtube(polish_music_command(text_lower))
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