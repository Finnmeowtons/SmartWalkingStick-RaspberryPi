# vision.py
import cv2
import requests
import asyncio
import concurrent.futures
import google.generativeai as genai
from ultralytics import YOLO
from collections import Counter
from smartstick.utils.config import GEMINI_API_KEY, get_path
from smartstick.services.tts_engine import tts_piper
from smartstick.utils.network_utils import ONLINE
from smartstick.interfaces.gemini import detect_online

executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)


# --- Offline YOLO ---
def detect_offline(image_path):
    model_yolo = YOLO("smartstick/models/yolov8n.pt")
    results = model_yolo(image_path)

    labels = [model_yolo.names[int(cls)] for cls in results[0].boxes.cls]
    label_counts = Counter(labels)

    description_parts = []
    for label, count in label_counts.items():
        description_parts.append(f"{count} {label}" if count > 1 else f"1 {label}")

    return "Nakikita ko: " + ", ".join(description_parts) if description_parts else "Walang nakita."

async def detect_objects_and_speak():
    loop = asyncio.get_event_loop()

    # --- Capture frame (fast, sync is fine) ---
    print("📷 Taking a pic")
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        img_path = get_path("images", "detect.jpg")
        cv2.imwrite(img_path, frame)
        print("Image saved on path:", img_path)
    cam.release()

    # --- Run detection in background thread ---
    if ONLINE:
        description = await loop.run_in_executor(executor, detect_online, img_path)
    else:
        description = await loop.run_in_executor(executor, detect_offline, img_path)

    # --- Run TTS in background too ---
    await loop.run_in_executor(executor, tts_piper, description)

async def main():
    await detect_objects_and_speak()

if __name__ == "__main__":
    asyncio.run(main())