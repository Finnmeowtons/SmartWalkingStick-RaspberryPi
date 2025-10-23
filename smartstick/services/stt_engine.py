import asyncio
import websockets
import sounddevice as sd
import numpy as np
import json
import sys
import threading
from smartstick.utils.config import VOSK_SERVER_URI

# -----------------------------
# CONFIG
# -----------------------------
SAMPLE_RATE = 16000
CONF_THRESHOLD = 0.6  # confidence threshold

# -----------------------------
# STREAM OBJECT
# -----------------------------
class STTStream:
    def __init__(self):
        self.partial_text = ""
        self.final_text = ""
        self.running = False
        self.loop = None
        self.audio_queue = None
        self.ws_connection = None

    async def _producer(self):
        while self.running:
            pcm = await self.audio_queue.get()
            if self.ws_connection:
                try:
                    await self.ws_connection.send(pcm)
                except Exception:
                    pass

    async def _consumer(self):
        while self.running:
            try:
                message = await asyncio.wait_for(self.ws_connection.recv(), timeout=0.01)
                result = json.loads(message)

                # Partial results
                if "partial" in result and result["partial"]:
                    self.partial_text = result["partial"]
                    sys.stdout.write(f"\r🕓 {self.partial_text}")
                    sys.stdout.flush()

                # Final results
                elif "text" in result and result["text"].strip():
                    self.final_text += result["text"] + " "
                    print(f"\r🗣️ {result['text']}")
                    self.partial_text = ""

            except asyncio.TimeoutError:
                pass

    async def _stream_task(self):
        self.audio_queue = asyncio.Queue()
        async with websockets.connect(VOSK_SERVER_URI) as ws:
            self.ws_connection = ws
            # send config to server
            await ws.send(json.dumps({"config": {"sample_rate": SAMPLE_RATE}}))
            print("🎤 Connected to Vosk server. Speak now...")

            self.running = True
            producer_task = asyncio.create_task(self._producer())
            consumer_task = asyncio.create_task(self._consumer())
            await asyncio.gather(producer_task, consumer_task)

    def _mic_callback(self, indata, frames, time, status):
        if status:
            print(status)
        pcm = (indata * 32767).astype(np.int16).tobytes()
        asyncio.run_coroutine_threadsafe(self.audio_queue.put(pcm), self.loop)

    def start_stream(self):
        if self.running:
            return  # already streaming

        def start_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._stream_task())

        threading.Thread(target=start_loop, daemon=True).start()
        # start recording audio
        sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=self._mic_callback).start()
        self.running = True

    def stop_stream(self):
        self.running = False

# -----------------------------
# Export
# -----------------------------
stream = STTStream()
recognizer = None  # Keep for compatibility
