# vision.py
import cv2
from ultralytics import YOLO
from collections import Counter
from smartstick.services.tts_engine import tts_piper

def detect_objects_and_speak():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        cv2.imwrite("../../image.jpg", frame)
    cam.release()

    model_yolo = YOLO('smartstick/models/yolov8n.pt')
    results = model_yolo('image.jpg')

    labels = [model_yolo.names[int(cls)] for cls in results[0].boxes.cls]
    label_counts = Counter(labels)

    description_parts = []
    for label, count in label_counts.items():
        if count == 1:
            description_parts.append(f"1 {label}")
        else:
            description_parts.append(f"{count} {label}s")

    description = "Nakikita ko: " + ", ".join(description_parts)
    tts_piper(description)

detect_objects_and_speak()