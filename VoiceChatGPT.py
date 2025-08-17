import os
import sys
import json
import time
import contextlib
import pyaudio
import io
import cv2

from vosk import Model, KaldiRecognizer
import google.generativeai as genai
from piper import PiperVoice
import numpy as np
from ultralytics import YOLO
from collections import Counter
import subprocess
from yt_dlp import YoutubeDL

WAKEWORDS = ["jodi", "joe de"]
# Global variable to hold the process
current_music = None
# ──────────────────────────────────────────────
# Gemini API Configuration
# ──────────────────────────────────────────────
genai.configure(api_key="AIzaSyBWEi7EeLKC38WGY47O_KTz3Tp_H0EdNQ8")
model_gemini = genai.GenerativeModel('gemini-2.5-flash-lite')

def askGemini(prompt):
    try:
        response = model_gemini.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# ──────────────────────────────────────────────
# TTS Configuration
# ──────────────────────────────────────────────
voice = PiperVoice.load(
    "smartstick/models/piper/en/amy/en_US-amy-medium.onnx",
    "smartstick/models/piper/en/amy/en_US-amy-medium.onnx.json"
)

# ──────────────────────────────────────────────
# Vosk Speech Recognition Configuration
# ──────────────────────────────────────────────
model_path = "smartstick/models/vosk-model-tl-ph-generic-0.6/"
if not os.path.exists(model_path):
    print(f"Model '{model_path}' was not found. Please check the path.")
    exit(1)
model_vosk = Model(model_path)

p = pyaudio.PyAudio()
chunk_size = 8192
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=chunk_size)
recognizer = KaldiRecognizer(model_vosk, 16000)


def text_to_speech(voice, text):
    print("🔊 Speaking...")
    audio_stream = voice.synthesize(text)
    # audio_data_all = b""

    # # Collect all chunks first
    # for chunk in audio_stream:
    #     audio_data_all += (chunk.audio_float_array * 32767).astype(np.int16).tobytes()

    pTTS = pyaudio.PyAudio()
    stream = pTTS.open(
        format=pTTS.get_format_from_width(width=2),
        channels=1,
        rate=22050,
        output=True,
        frames_per_buffer=8192
    )

    # # Small silence before speech
    # silence_duration = 0.6
    # silence_samples = int(silence_duration * 22050)
    # stream.write((np.zeros(silence_samples, dtype=np.int16)).tobytes())

    # # Play entire audio at once
    # stream.write(audio_data_all)
    silence_duration = 0.6
    silence_samples = int(silence_duration * 22050)
    silence_data = (np.zeros(silence_samples, dtype=np.int16)).tobytes()
    stream.write(silence_data)

    for chunk in audio_stream:
        audio_data = (chunk.audio_float_array * 32767).astype(np.int16).tobytes()
        stream.write(audio_data)
    time.sleep(1) 

    stream.stop_stream()
    stream.close()
    pTTS.terminate()

def play_song_youtube(song_name):
    global current_music

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(song_name, download=False)
        video = info['entries'][0] if 'entries' in info else info
        audio_url = video['url']
        title = video.get('title', 'Unknown')
        print(f"Playing: {title}")

        # Start ffplay as a subprocess
        current_music = subprocess.Popen([
            'ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', audio_url
        ])

def stop_music():
    global current_music
    if current_music:
        current_music.terminate()  # stops the music
        current_music = None
        print("Music stopped")


def detect_objects_and_speak():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        cv2.imwrite("image.jpg", frame)
    cam.release()

    model_yolo = YOLO('yolov8n.pt')
    results = model_yolo('image.jpg')

    labels = [model_yolo.names[int(cls)] for cls in results[0].boxes.cls]
    label_counts = Counter(labels)

    description_parts = []
    for label, count in label_counts.items():
        if count == 1:
            description_parts.append(f"1 {label}")
        else:
            description_parts.append(f"{count} {label}s")

    description = "I see: " + ", ".join(description_parts)
    text_to_speech(voice, description)


print("\nWaiting for WakeWord...")
isChatActive = False
last_sound_time = time.time()

while True:
    data = stream.read(chunk_size)
    if recognizer.AcceptWaveform(data):
        result_json = json.loads(recognizer.Result())
        text = result_json.get('text', '')
        if text:
            print("\r" + text, end='\n')
            last_sound_time = time.time()

            if isChatActive:
                stream.stop_stream()
                text_lower = text.lower()

                if "kumare" in text_lower or "kumpare" in text_lower:
                    prompt = (text_lower.replace("kumare", "").replace("kumpare", "").strip() +
          " in English; respond as if replying to a friend, following my instruction, not a question. Keep it conversational and concise. Dont use symbols other than dot and question-mark, if currency just put the whole word")

                    if prompt:
                        reply = askGemini(prompt)
                        print("Gemini:", reply)
                        text_to_speech(voice, reply)
                    else:
                        text_to_speech(voice, "Anong gusto mong itanong?")

                else:
                    if "saan ako" in text_lower or "where am i" in text_lower or "nasaan ako" in text_lower:
                        text_to_speech(voice, '''
                        Pagmulat ng mata, paggising sa umaga
                        Iunat ang kamay, bumangon na sa kama
                        Kung inaantok pa, lumundag-lundag ka, ah-ha-ha (ah-ha-ha)
                        Kung wala pa rin, 'wag mo nang pilitin
                        Buksan na lang ang TV o sa radyo ay hanapin
                        Tunog at bagong step na nakakagising, i-hi-hing (i-hi-hing)
                        One plus one equals two (really, ah)
                        Two plus two equals four (you're right)
                        Four plus four equals eight (perfect)
                        Doblehin ang eight
                        ''')
                    elif "makinig ng music" in text_lower or "listen to music" in text_lower or ("tugtug" in text_lower or "tugtog" in text_lower and "ng" in text_lower):
                        play_song_youtube(text_lower.replace("makinig ng music", "").replace("listen to music", "").replace("tugtug", "").replace("tugtog", "").strip())
                    elif "stop" in text_lower or "music" in text_lower or ("tugtug" in text_lower or "tugtog" in text_lower and "ng" in text_lower):
                        stop_music()
                    elif "nasa harap" in text_lower or "ahead" in text_lower:
                        detect_objects_and_speak()
                    else:
                        text_to_speech(voice, "Hindi kita gets bes.")

                print("\n")
                stream.start_stream()
                last_sound_time = time.time()
                continue

            if any(w in text.lower() for w in WAKEWORDS):
                print("\n🎤 Speak now...")
                isChatActive = True

    else:
        partial_json = json.loads(recognizer.PartialResult())
        partial = partial_json.get('partial', '')
        sys.stdout.write('\r' + partial)
        sys.stdout.flush()

    if time.time() - last_sound_time > 7 and isChatActive:
        isChatActive = False
        print("\nWaiting for WakeWord...")
