import subprocess
import socket
import json
from yt_dlp import YoutubeDL
from smartstick.services.tts_engine import tts_speak
import os
import threading
import time

current_music = None
mpv_socket_path = "/tmp/mpvsocket"
current_volume = 0.2  # 20%
current_audio_url = None

def send_mpv_command(command: dict):
    """Send a JSON command to mpv via UNIX socket."""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(mpv_socket_path)
        s.send((json.dumps(command) + "\n").encode("utf-8"))
        s.close()
    except Exception as e:
        print(f"[MPV] Failed to send command: {e}")

def set_volume(vol: float):
    """Set volume in real-time (0.0-1.0)."""
    global current_volume
    current_volume = max(0.0, min(vol, 1.0))
    send_mpv_command({"command": ["set_property", "volume", current_volume * 100]})
    print(f"Volume set to {int(current_volume*100)}%")

def increase_volume(step=0.1):
    set_volume(current_volume + step)

def decrease_volume(step=0.1):
    set_volume(current_volume - step)

def stop_music():
    global current_music, current_audio_url
    if current_music:
        send_mpv_command({"command": ["stop"]})
        current_music.terminate()
        current_music = None
        print("Music stopped")

def play_song_youtube(song_name):
    global current_music, current_audio_url
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(song_name, download=False)
        video = info['entries'][0] if 'entries' in info else info
        audio_url = video['url']
        title = video.get('title', 'Unknown')
        print(f"Music title: {title}")

        current_audio_url = audio_url

        def speak_and_play():
            tts_thread = threading.Thread(target=tts_speak, args=(f"Playing {title}", "tl"))
            tts_thread.start()

            time.sleep(1.0)

            if os.path.exists(mpv_socket_path):
                os.unlink(mpv_socket_path)
            global current_music
            current_music = subprocess.Popen([
                'mpv', '--no-video',
                '--msg-level=all=no',
                f'--input-ipc-server={mpv_socket_path}',
                f'--volume={current_volume*100}',
                audio_url
            ])

        threading.Thread(target=speak_and_play).start()

if __name__ == "__main__":
    play_song_youtube("eraserhead overdrive")
    import time
    time.sleep(5)
    increase_volume(0.2)
    time.sleep(5)
    decrease_volume(0.1)
    time.sleep(10)
    stop_music()
