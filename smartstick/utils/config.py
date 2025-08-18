import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def get_path(*paths):
    """
    Join BASE_DIR with subpaths.
    Example: get_path("models", "piper", "en", "amy", "file.json")
    """
    return os.path.join(BASE_DIR, *paths)

WAKEWORDS = ["jodi", "joe de"]

GEMINI_API_KEY = "AIzaSyBWEi7EeLKC38WGY47O_KTz3Tp_H0EdNQ8"

OPENCELLID_API_KEY = "pk.beb8003c5cfb9d5cb74ae8beb0b7cecf"

# Models
# VOSK_MODEL_PATH = "../models/vosk-model-tl-ph-generic-0.6/"
VOSK_MODEL_PATH = get_path("models", "vosk-model-tl-ph-generic-0.6")

PIPER_MODEL = get_path("models", "piper", "en", "amy", "en_US-amy-medium.onnx")
# PIPER_MODEL = (
#     "../models/piper/en/amy/en_US-amy-medium.onnx",
#     "../models/piper/en/amy/en_US-amy-medium.onnx.json"
# )

# GPS
GPS_PORT = "/dev/ttyUSB0"   # change to your GPS serial port
GPS_BAUD = 9600
