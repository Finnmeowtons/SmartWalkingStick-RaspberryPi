import pyaudio
import websocket
import threading
import json
import numpy as np
import resampy

URL = "ws://localhost:2700"
CHUNK = 8192
TARGET_RATE = 16000

# def get_default_input_rate():
#     p = pyaudio.PyAudio()
#     default_device = p.get_default_input_device_info()
#     rate = int(default_device["defaultSampleRate"])
#     p.terminate()
#     return rate

MIC_RATE = 16000
# print(f"🎤 Using mic rate {MIC_RATE}Hz, resampling -> {TARGET_RATE}Hz")

def audio_stream(ws):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=MIC_RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("🎤 Start streaming audio...")
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_np = np.frombuffer(data, dtype=np.int16)

            # ✅ Resample if mic rate != 16k
            # if MIC_RATE != TARGET_RATE:
            #     audio_np = resampy.resample(audio_np, MIC_RATE, TARGET_RATE)

            ws.send(audio_np.astype(np.int16).tobytes(),
                    websocket.ABNF.OPCODE_BINARY)
    except KeyboardInterrupt:
        print("Stopping stream...")
        ws.close()
        stream.stop_stream()
        stream.close()
        p.terminate()

def on_message(ws, message):
    result = json.loads(message)
    if "partial" in result and result["partial"]:
        print("⏳ Partial:", result["partial"])
    if "text" in result and result["text"]:
        print("✅ Final:", result["text"])

def on_error(ws, error):
    print("❌ WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 Connection closed")

def on_open(ws):
    threading.Thread(target=audio_stream,
                     args=(ws,),
                     daemon=True).start()

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    ws.run_forever()
