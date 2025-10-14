# smartstick/process/stt_engine_process.py
import asyncio
import websockets
import json
import sys
import numpy as np

SAMPLE_RATE = 16000
CONF_THRESHOLD = 0.6  # confidence threshold

class STTStreamProcess:
    def __init__(self, conn, vosk_server_uri):
        self.parent_conn = conn
        self.vosk_server_uri = vosk_server_uri
        self.running = True

    async def _producer(self, ws):
        while self.running:
            if self.parent_conn.poll():
                audio_chunk = self.parent_conn.recv()
                pcm = (audio_chunk * 32767).astype(np.int16).tobytes()
                await ws.send(pcm)
            else:
                await asyncio.sleep(0.001)

    async def _consumer(self, ws):
        while self.running:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=0.01)
                result = json.loads(message)
                if "text" in result and result["text"].strip():
                    text = result["text"].strip()
                    conf = result.get("conf", 1.0)
                    if conf >= CONF_THRESHOLD:
                        self.parent_conn.send(text)
            except asyncio.TimeoutError:
                pass

    async def _stream_task(self):
        async with websockets.connect(self.vosk_server_uri) as ws:
            await ws.send(json.dumps({"config": {"sample_rate": SAMPLE_RATE}}))
            print("🎤 Connected to Vosk server. Waiting for audio...")
            await asyncio.gather(self._producer(ws), self._consumer(ws))

    def run(self):
        asyncio.run(self._stream_task())
