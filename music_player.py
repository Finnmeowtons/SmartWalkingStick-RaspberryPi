# music_player.py
import subprocess
from yt_dlp import YoutubeDL

current_music = None

def play_song_youtube(song_name):
    global current_music
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
        print(f"Playing: {title}")
        current_music = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', audio_url])

def stop_music():
    global current_music
    if current_music:
        current_music.terminate()
        current_music = None
        print("Music stopped")
