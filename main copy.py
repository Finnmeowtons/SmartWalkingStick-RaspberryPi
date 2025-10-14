import json
import sys
import time
import asyncio
import re
import os
import concurrent.futures

from smartstick.utils.config import WAKEWORDS, DEVICE_ID, MQTT_BROKER, MQTT_PORT
from smartstick.interfaces.gemini import ask_gemini, polish_music_command
from smartstick.services.stt_engine import stream
from smartstick.services.tts_engine import tts_speak, stop_tts
from smartstick.services.music_player import (
    play_song_youtube, stop_music,
    current_volume, decrease_volume, increase_volume
)
from smartstick.hardware.vision import detect_objects_and_speak
from smartstick.hardware import time_of_flight, vibrator
from smartstick.services.sound_cues import play_sound
from smartstick.services.places_service import search_place
from smartstick.services.osrm_service import get_walking_directions, json_to_route, navigate_osrm
from smartstick.hardware.sim_module import read_sms
from smartstick.core import preload
from smartstick.services import porcupine_engine
from smartstick.hardware.get_gps import get_gps_coords
from smartstick.services.mqtt_client import MQTTClient
from smartstick.hardware.sos_button import SOSButton

preload.preload_all()

# ==============================
# ThreadPoolExecutor for heavy tasks
# ==============================
# num_workers = max(1, os.cpu_count() - 1)
# executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_workers)

def run_tts(text, lang="tl"):
    executor.submit(tts_speak, text, lang)

def run_object_detection():
    executor.submit(asyncio.run, detect_objects_and_speak())

# def run_navigation(dest_lat, dest_lon):
#     executor.submit(navigate_osrm, dest_lat, dest_lon)

# def run_read_sms(unread_only=False):
#     return executor.submit(read_sms, unread_only)

# ==============================
# SMS MODE
# ==============================
vibration_obstacle = True
sms_messages = []
current_sms_index = 0
sms_mode_active = False

def start_sms_mode():
    global sms_messages, current_sms_index, sms_mode_active
    future = run_read_sms(unread_only=False)
    sms_messages = future.result()  # wait for SMS fetch
    current_sms_index = 0
    sms_mode_active = True

    if sms_messages:
        read_current_sms()
    else:
        run_tts("Walang bagong mensahe")

def read_current_sms():
    global current_sms_index, sms_messages
    if not sms_messages:
        run_tts("Walang mensahe")
        return

    idx, status, sender, content = sms_messages[current_sms_index]
    run_tts(f"Mensahe mula kay {sender}: {content}")

def next_sms():
    global current_sms_index, sms_messages
    if current_sms_index < len(sms_messages) - 1:
        current_sms_index += 1
        read_current_sms()
    else:
        run_tts("Wala nang natitirang mensahe")

def repeat_sms():
    read_current_sms()

def stop_sms_mode():
    global sms_mode_active
    sms_mode_active = False
    run_tts("SMS mode off")

# ==============================
# OBSTACLE DETECTION
# ==============================
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

# ==============================
# Wakeword Mode
# ==============================
def on_wakeword():
    global isChatActive, last_sound_time
    # porcupine_engine.stop_porcupine()
    play_sound("listening")
    print("\n🎤 Speak now...")
    isChatActive = True
    last_sound_time = time.time()
    stream.start_stream()

# ==============================
# MAIN LOOP
# ==============================
print("\nWaiting for WakeWord...")
isChatActive = False
last_sound_time = time.time()

while True:
    handle_obstacle()

    # Check if there is recognized text from Vosk server
    text = stream.final_text.strip()
    if text:
        stream.final_text = ""  # clear after reading
        print(f"Recognized: {text}")
        last_sound_time = time.time()
        text_lower = text.lower()

        # === SMS Mode Commands ===
        if sms_mode_active:
            if "sunod" in text_lower:
                next_sms()
                continue
            elif "ulitin" in text_lower:
                repeat_sms()
                continue
            elif "stop" in text_lower or "tapos" in text_lower:
                stop_sms_mode()
                continue

        # === Volume Controls ===
        if any(kw in text_lower for kw in ["volume increase", "increase volume", "volume up", "up volume", "lakasan"]):
            executor.submit(increase_volume)
            continue
        elif any(kw in text_lower for kw in ["volume decrease", "decrease volume", "volume down", "bawasan", "hinaan"]):
            executor.submit(decrease_volume)
            continue
        elif "stop" in text_lower:
            executor.submit(stop_music)
            executor.submit(stop_tts)
            continue

        # === Chat Mode ===
        if isChatActive:
            if "kumare" in text_lower or "kumpare" in text_lower:
                prompt = text_lower.replace("kumare", "").replace("kumpare", "").strip()
                reply = ask_gemini(prompt)
                run_tts(reply, lang="tl")

            elif "tulong" in text_lower or "sos" in text_lower:
                sos_button.send_sos()
                run_tts("Help Sent.")

            elif "mensahe" in text_lower or "basahin" in text_lower:
                start_sms_mode()

            elif "music" in text_lower:
                executor.submit(play_song_youtube, polish_music_command(text_lower))

            elif any(kw in text_lower for kw in ["vibration on", "on vibration", "vibrate on", "on vibrate"]):
                toggle_obstacle_detection(True)
                run_tts("Obstacle detection enabled.")

            elif any(kw in text_lower for kw in ["vibration off", "off vibration", "vibrate off", "off vibrate"]):
                toggle_obstacle_detection(False)
                run_tts("Obstacle detection disabled.")

            elif "nasa harap" in text_lower:
                run_object_detection()

            elif "gabay papunta" in text_lower:
                destination = text_lower.split("gabay papunta")[-1].strip()
                destination = re.sub(r"[^a-zA-Z0-9\s]", "", destination).strip()
                if destination:
                    nearest = search_place(destination)
                    dest_lat = nearest["lat"]
                    dest_lon = nearest["lon"]
                    if dest_lat:
                        navigate_osrm(dest_lat, dest_lon)
                    else:
                        run_tts(nearest["advice"], lang="tl")
                else:
                    run_tts("Anong destinasyon ang gusto mong puntahan?", lang="tl")

            elif "turo papunta" in text_lower:
                destination = text_lower.split("turo papunta sa")[-1].strip()
                destination = re.sub(r"[^a-zA-Z0-9\s]", "", destination).strip()
                if destination:
                    nearest = search_place(destination)
                    dest_lat = nearest["lat"]
                    dest_lon = nearest["lon"]

                    if dest_lat:
                        steps, summary, error = get_walking_directions(dest_lat, dest_lon)
                        if error:
                            run_tts(error, lang="tl")
                        else:
                            run_tts(summary, lang="tl")
                    else:
                        run_tts(nearest["advice"], lang="tl")
                else:
                    run_tts("Anong destinasyon ang gusto mong puntahan?", lang="tl")

            else:
                run_tts("Hindi kita gets bes.")

        # === Wakeword ===
        if any(w in text_lower for w in WAKEWORDS):
            play_sound("listening")
            print("\n🎤 Speak now...")
            isChatActive = True

    # Reset chat if no input for 7s
    if time.time() - last_sound_time > 7 and isChatActive:
        isChatActive = False
        play_sound("idle")
        print("\nWaiting for WakeWord...")

