import time
from smartstick.services.stt_engine import stream

print("Starting STT stream...")
stream.start_stream()
print("🎤 STT stream started. Speak now...")

try:
    while True:
        # small delay to allow async consumer to update final_text
        time.sleep(0.1)

        # check final text
        text = stream.final_text.strip()
        if text:
            stream.final_text = ""  # clear after reading
            print(f"Recognized: {text}")

except KeyboardInterrupt:
    print("Stopping STT stream...")
    stream.stop_stream()
