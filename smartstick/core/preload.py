"""
preload.py
----------
Hybrid preload system for SmartStick.

This module is responsible for preloading heavy models or starting threads
in a way that balances speed and memory safety. It loads only the essentials
at startup (fast preload) and lazily loads heavier components when first used.
"""

import threading
import asyncio
from smartstick.utils.config import get_path, PIPER_MODEL

# Globals for cached resources
_preloaded = {
    "cv2_model": None,
    "tts_engine": None,
    "gemini_client": None,
}

def preload_fast():
    """Load lightweight essentials immediately (fast startup)."""
    try:
        from piper import PiperVoice
        _preloaded["tts_engine"] = PiperVoice.load(PIPER_MODEL)  
        print("[Preload] Piper TTS engine loaded (fast).")
    except Exception as e:
        print(f"[Preload] Piper preload skipped: {e}")

def preload_lazy():
    """Kick off background threads to lazily load heavy models."""
    # def _load_cv2():
    #     try:
    #         from ultralytics import YOLO
    #         _preloaded["cv2_model"] = YOLO(get_path("models", "yolov8n.pt"))
    #         print("[Preload] YOLOv8 model loaded with Ultralytics (lazy).")
    #     except Exception as e:
    #         print(f"[Preload] Ultralytics preload failed: {e}")

    def _load_gemini():
        try:
            import google.generativeai as genai
            _preloaded["gemini_client"] = genai.configure(api_key="YOUR_KEY")
            print("[Preload] Gemini client loaded (lazy).")
        except Exception as e:
            print(f"[Preload] Gemini preload failed: {e}")

    # threading.Thread(target=_load_cv2, daemon=True).start()
    threading.Thread(target=_load_gemini, daemon=True).start()

def get_resource(name):
    """Fetch a preloaded resource (or None if not loaded)."""
    return _preloaded.get(name)

def preload_all():
    """Run both fast and lazy preloads."""
    preload_fast()
    preload_lazy()
