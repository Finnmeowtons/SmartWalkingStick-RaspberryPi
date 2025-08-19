import os
import random
import subprocess
from smartstick.utils.config import get_path

# Path to the sounds folder
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "sounds")

# Define cues with corresponding WAV files
SOUND_CUES = {
    "listening": ["listen.wav", "listen2.wav"],
    "idle": ["idle.wav", "idle2.wav"]
}

def play_sound(cue: str, volume: float = 0.1):
    if cue not in SOUND_CUES:
        print(f"[SoundCue] No sounds defined for cue '{cue}'")
        return

    sound_file = random.choice(SOUND_CUES[cue])
    path = os.path.join(get_path("sounds"), sound_file)

    if os.path.exists(path):
        # Use ffplay with volume adjustment, non-blocking
        subprocess.Popen([
            "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
            "-af", f"volume={volume}",
            path
        ])
    else:
        print(f"[SoundCue] Sound file not found: {path}")

if __name__ == "__main__":
    play_sound("idle")
