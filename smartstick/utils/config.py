import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def get_path(*paths):
    """
    Join BASE_DIR with subpaths.
    Example: get_path("models", "piper", "en", "amy", "file.json")
    """
    return os.path.join(BASE_DIR, *paths)

WAKEWORDS = ["jodi", "joe de", "joey"]
VOSK_SERVER_URI = "ws://192.168.68.114:2700"
DEVICE_ID = "639270734452"

MQTT_BROKER = "192.168.68.114"
MQTT_PORT = 1884

GEMINI_API_KEY = "AIzaSyBWEi7EeLKC38WGY47O_KTz3Tp_H0EdNQ8"
BUTTON_PIN = 4


PORCUPINE_ACCESS_KEY = "krzPRzjo0OeeBarXT6j7WvgDB2uV04z84VVIUruq848U0/ySrwW/Ow=="
WAKEWORD_PATH = get_path("models", "wakeword.ppn")

# Models
# VOSK_MODEL_PATH = "../models/vosk-model-tl-ph-generic-0.6/"
VOSK_MODEL_PATH = get_path("models", "vosk-model-tl-ph-generic-0.6")

PIPER_MODEL = get_path("models", "piper", "en", "amy", "en_US-amy-medium.onnx")
# PIPER_MODEL = (
#     "../models/piper/en/amy/en_US-amy-medium.onnx",
#     "../models/piper/en/amy/en_US-amy-medium.onnx.json"
# )

# GPS
GPS_PORT = "/dev/ttyUSB0" 
GPS_BAUD = 9600
