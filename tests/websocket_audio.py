import asyncio, sounddevice as sd, numpy as np, websockets, json

async def main():
    uri = "ws://192.168.68.114:2700"
    queue = asyncio.Queue(maxsize=100)

    async def sender(ws):
        while True:
            pcm = await queue.get()
            await ws.send(pcm)

    async def receiver(ws):
        while True:
            msg = await ws.recv()
            print(msg)

    def callback(indata, frames, time, status):
        pcm = (indata * 32767).astype(np.int16).tobytes()
        try:
            queue.put_nowait(pcm)
        except asyncio.QueueFull:
            pass  # drop if full

    async with websockets.connect(uri) as ws:
        asyncio.create_task(sender(ws))
        with sd.InputStream(samplerate=16000, channels=1, dtype='float32', callback=callback):
            await receiver(ws)

asyncio.run(main())
