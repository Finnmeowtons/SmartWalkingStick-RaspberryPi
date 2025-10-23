import json
import sys
import time
import re
import signal
import os
from threading import Thread
from multiprocessing import Process, Pipe

import asyncio
import sounddevice as sd
import numpy as np

from smartstick.utils.config import WAKEWORDS, DEVICE_ID, MQTT_BROKER, MQTT_PORT, VOSK_SERVER_URI
from smartstick.interfaces.gemini import ask_gemini, polish_music_command
from smartstick.services.tts_engine import tts_speak, stop_tts
from smartstick.services.music_player import (
    play_song_youtube, stop_music,
    current_volume, decrease_volume, increase_volume
)
from smartstick.hardware.vision import detect_objects_and_speak
from smartstick.hardware import time_of_flight, vibrator
from smartstick.services.sound_cues import play_sound
from smartstick.services.places_service import search_place
from smartstick.services.osrm_service import get_walking_directions, navigate_osrm
from smartstick.hardware.sim_module import read_sms, delete_sms
from smartstick.core import preload
from smartstick.hardware.get_gps import get_gps_coords
from smartstick.services.mqtt_client import MQTTClient
from smartstick.hardware.sos_button import SOSButton
preload.preload_all()

# -----------------------------
# Global State
# -----------------------------
isChatActive = False

shutdown_flag = False
last_sound_time = time.time()
sms_mode_active = False
sms_messages = []
current_sms_index = 0
vibration_obstacle = True

# -----------------------------
# Import STT Process
# -----------------------------
from smartstick.process.stt_engine_process import STTStreamProcess

# -----------------------------
# Helper Functions
# -----------------------------
def run_tts(text, lang="tl"):
    Thread(target=tts_speak, args=(text, lang), daemon=True).start()

def run_object_detection_async():
    Thread(target=lambda: asyncio.run(detect_objects_and_speak()), daemon=True).start()


# -----------------------------
# SMS Functions
# -----------------------------
def start_sms_mode():
    global sms_messages, current_sms_index, sms_mode_active
    sms_messages = read_sms(unread_only=False)
    sms_messages.reverse()
    current_sms_index = 0
    sms_mode_active = True
    if sms_messages:
        run_tts("Reading messages")

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
    global current_sms_index
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

# -----------------------------
# Obstacle Functions
# -----------------------------
def toggle_obstacle_detection(state: bool):
    global vibration_obstacle
    vibration_obstacle = state
    if state:
        time_of_flight.enable()
        vibrator.enable()
    else:
        time_of_flight.disable()
        vibrator.disable()

def handle_obstacle():
    if not vibration_obstacle:
        return
    distance = time_of_flight.get_distance()
    duty = vibrator.distance_to_duty(distance)
    vibrator.set_strength(duty)

# -----------------------------
# Music
# -----------------------------
def play_music_polished(text_lower):
    play_song_youtube(text_lower)


def shutdown_handler(sig, frame):
    global shutdown_flag
    if not shutdown_flag:
        shutdown_flag = True
        stop_music()
        print("\n🛑 Shutting down gracefully...")

        try:
            # Stop audio stream
            if stream.active:
                stream.stop()
                stream.close()
                print("🎙️ Microphone stopped.")
        except Exception as e:
            print(f"Error stopping mic: {e}")

        try:
            # Stop MQTT safely
            mqtt_client.disconnect()
            print("📡 MQTT disconnected.")
        except Exception as e:
            print(f"Error disconnecting MQTT: {e}")

        try:
            # Stop obstacle detection & vibrator
            toggle_obstacle_detection(False)
            print("🚫 Obstacle detection disabled.")
        except Exception as e:
            print(f"Error disabling obstacle detection: {e}")

        try:
            # Terminate STT process
            if stt_process.is_alive():
                stt_process.terminate()
                stt_process.join(timeout=2)
                print("🧠 STT process terminated.")
        except Exception as e:
            print(f"Error terminating STT process: {e}")

        print("✅ Clean exit complete.")
        os._exit(0)

# -----------------------------
# Main Loop
# -----------------------------
def main_loop(pipe_conn):
    global isChatActive, last_sound_time

    toggle_obstacle_detection(True)
    print("\nWaiting for WakeWord...")

    while True:
        handle_obstacle()

        if pipe_conn.poll():
            text = pipe_conn.recv()
            print(f"Recognized: {text}")
            last_sound_time = time.time()
            text_lower = text.lower()

            if "tulong" in text_lower or "sos" in text_lower:
                print("Tulong!")
                sos_button.send_sos()
                run_tts("Help Sent.")

            # === SMS Mode ===
            if sms_mode_active:
                if "sunod" in text_lower or "next" in text_lower:
                    next_sms()
                    continue
                elif "ulitin" in text_lower or "again" in text_lower:
                    repeat_sms()
                    continue
                elif "stop" in text_lower or "tapos" in text_lower or "top" in text_lower or "pop" in text_lower or "stuffed" in text_lower:
                    stop_sms_mode()
                    continue

            # === Volume Control ===
            if any(kw in text_lower for kw in ["volume increase", "increase volume", "volume up", "up volume", "lakasan"]):
                increase_volume()
                continue
            elif any(kw in text_lower for kw in ["volume decrease", "decrease volume", "volume down", "bawasan", "hinaan"]):
                decrease_volume()
                continue
            elif "stop" in text_lower or "top" in text_lower or "pop" in text_lower or "tama na" in text_lower or "stuffed" in text_lower:
                stop_music()
                print("stopped")
                stop_tts()
                continue

            # === Chat Mode ===
            if isChatActive:
                if "kumare" in text_lower or "kumpare" in text_lower:
                    prompt = text_lower.replace("kumare", "").replace("kumpare", "").strip()
                    reply = ask_gemini(prompt)
                    run_tts(reply, lang="tl")

                elif "mensahe" in text_lower or "basahin" in text_lower:
                    run_tts("Checking messages. Please wait")
                    start_sms_mode()

                elif "music" in text_lower:
                    
                    run_tts("Searching Music")
                    play_music_polished(text_lower)

                elif any(kw in text_lower for kw in ["vibration on", "on vibration", "vibrate on", "on vibrate"]):
                    toggle_obstacle_detection(True)
                    run_tts("Obstacle detection enabled.")

                elif any(kw in text_lower for kw in ["vibration off", "off vibration", "vibrate off", "off vibrate"]):
                    toggle_obstacle_detection(False)
                    run_tts("Obstacle detection disabled.")

                elif "nasa harap" in text_lower:
                    run_tts("Taking a picture!")
                    run_object_detection_async()

                else:
                    # Match "gabay papunta" or "gabay papuntang sa"
                    match_gabay = re.search(r"gabay papunt(a|ang)?( sa)? (.+)", text_lower)
                    # Match "turo papunta sa"
                    match_turo = re.search(r"turo papunt(a|ang)?( sa)? (.+)", text_lower)

                    if match_gabay:
                        destination = re.sub(r"[^a-zA-Z0-9\s]", "", match_gabay.group(3)).strip()
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

                    elif match_turo:
                        destination = re.sub(r"[^a-zA-Z0-9\s]", "", match_turo.group(3)).strip()
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
                            run_tts("Anong destinasyon ang gusto mong puntahan?", lang="tl")

                    else:
                        # run_tts("Hindi kita gets bes.")
                        print("no")


            # === Wakeword Detection ===
            if any(w in text_lower for w in WAKEWORDS):
                play_sound("listening")
                print("\n🎤 Speak now...")
                isChatActive = True

        if time.time() - last_sound_time > 7 and isChatActive:
            isChatActive = False
            play_sound("idle")
            print("\nWaiting for WakeWord...")

        time.sleep(0.05)

# -----------------------------
# Manual Input Listener
# -----------------------------
def input_listener():
    while True:
        print("\n[Manual Mode] Commands:")
        print("1 - SOS / Send Help")
        print("2 - Run Object Detection")
        print("3 - Disable Obstacle Detection")
        print("4 - Enable Obstacle Detection")
        print("5 - Start SMS Mode")
        print("6 - Play Music (YouTube)")
        print("7 - Stop Music")
        print("8 - Volume Up")
        print("9 - Volume Down")
        print("10 - Kumare / ChatGPT prompt")
        print("11 - Gabay Papunta (Set destination)")
        print("12 - Turo Papunta (Get directions)")
        print("exit - Exit manual mode")

        user_input = input("\nEnter command: ").strip()

        if user_input == "1":
            sos_button.send_sos()
            run_tts("Help sent.")

        elif user_input == "2":
            run_object_detection_async()

        elif user_input == "3":
            toggle_obstacle_detection(False)
            run_tts("Obstacle detection disabled.")

        elif user_input == "4":
            toggle_obstacle_detection(True)
            run_tts("Obstacle detection enabled.")

        elif user_input == "5":
            start_sms_mode()

        elif user_input == "6":
            prompt = input("Enter song name or command: ")
            play_music_polished(prompt)

        elif user_input == "7":
            stop_music()
            stop_tts()
            run_tts("Music stopped.")

        elif user_input == "8":
            increase_volume()
            # run_tts(f"Volume increased to {current_volume()}")

        elif user_input == "9":
            decrease_volume()
            # run_tts(f"Volume decreased to {current_volume()}")

        elif user_input == "10":
            prompt = input("Enter prompt for Kumare / ChatGPT: ")
            reply = ask_gemini(prompt)
            run_tts(reply, lang="tl")

        elif user_input == "11":
            prompt = input("Enter destination for Gabay Papunta: ")
            prompt_clean = re.sub(r"[^a-zA-Z0-9\s]", "", prompt).strip()
            if prompt_clean:
                nearest = search_place(prompt_clean)
                dest_lat = nearest["lat"]
                dest_lon = nearest["lon"]
                if dest_lat:
                    navigate_osrm(dest_lat, dest_lon)
                else:
                    run_tts(nearest["advice"], lang="tl")
            else:
                run_tts("Anong destinasyon ang gusto mong puntahan?")

        elif user_input == "12":
            prompt = input("Enter destination for Turo Papunta: ")
            prompt_clean = re.sub(r"[^a-zA-Z0-9\s]", "", prompt).strip()
            if prompt_clean:
                nearest = search_place(prompt_clean)
                dest_lat = nearest["lat"]
                dest_lon = nearest["lon"]
                if dest_lat:
                    steps, summary, error = get_walking_directions(dest_lat, dest_lon)
                    if error:
                        run_tts(error, lang="tl")
                    else:
                        run_tts(summary, lang="tl")
                else:
                    run_tts("Hindi mahanap ang destinasyon.")
            else:
                run_tts("Anong destinasyon ang gusto mong puntahan?")

        elif user_input == "13":
            delete_sms(delete_all=True)

        elif user_input.lower() == "exit":
            print("👋 Exiting manual mode...")
            os._exit(0)

        else:
            print("❓ Unknown command. Try 1–12 or 'exit'.")
        time.sleep(0.1)

# -----------------------------
# Initialize Devices
# -----------------------------
mqtt_client = MQTTClient(device_id=DEVICE_ID, broker=MQTT_BROKER, port=MQTT_PORT)
mqtt_client.connect()
mqtt_client.start_location_loop(get_coords_func=get_gps_coords)

sos_button = SOSButton(mqtt_client, DEVICE_ID, hold_time=5)
sos_button.start_button_listener()

# -----------------------------
# Start STT Process + Microphone Stream
# -----------------------------
parent_conn, child_conn = Pipe()

# Audio callback sends chunks to STT process
def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)
    parent_conn.send(indata.copy())

# Start microphone
stream = sd.InputStream(samplerate=16000, channels=1, callback=audio_callback)
stream.start()
print("🎤 Microphone stream started. Speak now...")

# Start STT process
stt_process = Process(target=STTStreamProcess(child_conn, VOSK_SERVER_URI).run)
stt_process.start()

# -----------------------------
# Run Threads
# -----------------------------
Thread(target=main_loop, args=(parent_conn,), daemon=True).start()
Thread(target=input_listener, daemon=True).start()

# -----------------------------
# Keep main thread alive
# -----------------------------

# Bind Ctrl+C (SIGINT) to shutdown handler
signal.signal(signal.SIGINT, shutdown_handler)


while True:
    time.sleep(1)
