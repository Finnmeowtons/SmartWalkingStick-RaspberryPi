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
from smartstick.hardware import time_of_flight, vibrator
from smartstick.services.sound_cues import play_sound
# from smartstick.hardware.gps import
from smartstick.core import preload

preload.preload_all()

vibration_obstacle = True

def toggle_obstacle_detection(state: bool):
    global vibration_obstacle
    vibration_obstacle = state
    if state:
        time_of_flight.enable()
        vibrator.enable()
    else:
        time_of_flight.disable()
        vibrator.disable()

toggle_obstacle_detection(True)


def handle_obstacle():
    if not vibration_obstacle:
        return
    distance = time_of_flight.get_distance()
    duty = vibrator.distance_to_duty(distance)
    vibrator.set_strength(duty)

def trigger_object_detection():
    asyncio.run(detect_objects_and_speak())


print("\nWaiting for WakeWord...")
isChatActive = False
last_sound_time = time.time()

while True:
    handle_obstacle()
    data = stream.read(8192)
    if recognizer.AcceptWaveform(data):
        result_json = json.loads(recognizer.Result())
        text = result_json.get('text', '')
        if text:
            print(text)
            last_sound_time = time.time()
            text_lower = text.lower()

            
            if any(kw in text_lower for kw in ["volume increase", "increase volume", "volume up", "up volume", "lakasan"]):
                increase_volume()
                continue
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
                    tts_speak(reply, lang="tl")

                elif "music" in text_lower:
                    play_song_youtube(polish_music_command(text_lower))

                elif any(kw in text_lower for kw in ["vibration on", "on vibration", "vibrate on", "on vibrate"]):
                    toggle_obstacle_detection(True)
                    tts_speak("Obstacle detection enabled.")

                elif any(kw in text_lower for kw in ["vibration off", "off vibration", "vibrate off", "off vibrate"]):
                    toggle_obstacle_detection(False)
                    tts_speak("Obstacle detection disabled.")
            
                elif "nasa harap" in text_lower:
                    trigger_object_detection()

                else:
                    tts_speak("Hindi kita gets bes.")

                stream.start_stream()
                continue

            if any(w in text.lower() for w in WAKEWORDS):
                play_sound("listening")
                print("\n🎤 Speak now...")
                isChatActive = True
    else:
        partial = json.loads(recognizer.PartialResult()).get('partial', '')
        sys.stdout.write('\r' + partial)
        sys.stdout.flush()

    if time.time() - last_sound_time > 7 and isChatActive:
        isChatActive = False
        play_sound("idle")
        print("\nWaiting for WakeWord...")