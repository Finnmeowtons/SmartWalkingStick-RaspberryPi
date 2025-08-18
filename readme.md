## 🦯 SmartStick Features

### 🔍 Object Detection

* **Offline (default)**:

  * Uses **OpenCV + pre-trained model** (runs fully on the Raspberry Pi).
  * Saves detected image to `smartstick/images/detect.jpg`.
  * Provides a short spoken description.
* **Online (optional)**:

  * Uses **Google Gemini API** for detailed scene analysis.
  * Falls back to offline detection automatically if **no network** is detected.

### 🌐 Network Checking

* Modular function to check if internet is available.
* Automatically decides between **offline CV2 detection** and **online Gemini detection**.

### 🔊 Text-to-Speech (TTS)

* **Offline**: Uses **Piper TTS** with `aplay` for real-time speech output.

  * Supports **custom playback speed control** for faster/slower speech.
* **Online**: Supports **Google TTS** (with Tagalog support).

  * Falls back to Piper if online TTS fails.
* Supports **stop command** mid-speech using `stop_tts()`.
* Cleanly separated into `speech.py` for modularity.

### 🎵 Music Player

* Uses **mpv** with IPC socket for real-time playback control.
* **Voice-controlled volume**:

  * Increase/decrease volume in real-time without restarting music.
* **Voice-controlled playback**:

  * Play specific songs using YouTube search.
  * Stop playback or TTS using voice commands.
* Optionally announces **song title via TTS** while starting playback.

### 🧩 Modular Design

* `base_dir` is defined globally so all modules can access paths consistently.
* `vision.py` → object detection logic.
* `speech.py` → TTS logic (offline + online).
* `music_player.py` → YouTube playback, real-time volume, TTS integration.
* `network.py` → connectivity checks.
* `main.py` → orchestrates everything.

---

## ⚡ Hybrid Preload System (memo)

* **Fast startup**: loads essentials like Piper immediately.
* **Lazy loading**: heavy models (YOLO, Gemini) are loaded in background threads.

