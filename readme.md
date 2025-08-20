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
* Announces **song title via TTS** while starting playback.

* Uses **Google Gemini API** (if online) to **extract and clean user music commands**.

  * Only the music title is extracted; unnecessary words are removed.
  * Falls back to text replacement if **offline** or **Gemini fails**.

### 🔔 Sound Cues

* Plays **audio cues** when Jodi is **listening** or **idle**.
* Randomly selects from multiple `.wav` files.
* Volume adjustable to avoid overpowering TTS or music.

### 📏 Obstacle Detection (NEW)

* Uses **VL53L0X ToF (Time-of-Flight) sensor** for distance measurement.
* Provides **real-time vibration feedback** through a coin vibration motor.
* **Dynamic vibration strength**:

  * Stronger vibration when objects are **closer**.
  * Weaker vibration when objects are **farther**.
* Can be toggled **ON/OFF by voice command**

### 📡 Network Failover (Boot Script)

* On boot, a script checks **network availability**:
  * ✅ If **WiFi is ON**, it will automatically **turn OFF mobile data** (to save power and avoid conflicts).
  * ❌ If **WiFi is OFF**, it will automatically **turn ON mobile data** (ensuring continuous connectivity).
* Acts as a **failover system** so the SmartStick always has internet if at least one connection is available.
* Implemented as a **systemd service** for automatic startup.

### 📍 GPS Integration

* Retrieves **real-time GPS coordinates** using a GPS module.
* `get_gps_coords(timeout=30)`:
  * Returns `(latitude, longitude)` as floats.
  * Waits for a GPS fix up to 30 seconds.
  * Falls back with `"Walang GPS signal"` if no fix is acquired.
* Used by navigation services for **turn-by-turn guidance**.

### 🗺️ Walking Directions (OSRM Service)

* Integrates with **Open Source Routing Machine (OSRM)** to fetch walking directions.
* Workflow:
  1. Current location from **GPS**.
  2. Destination coordinates provided by user/voice command.
  3. Route requested via **OSRM public API**.
* **Gemini-powered summarization**:
  * Generates a **clear Tagalog route summary** (e.g., "Lumiko ka pakaliwa sa De Venecia Avenue").
  * Falls back to a **hardcoded JSON-to-route parser** if Gemini fails.
* Live navigation:
  * Tracks current GPS against route steps.
  * Speaks turn-by-turn instructions.
  * Announces arrival with **context** (e.g., “Nakarating ka na, nasa kanan side”).

### ⚡ Hybrid Preload System (memo)

* **Fast startup**: loads essentials like Piper immediately.
* **Lazy loading**: heavy models (YOLO, Gemini) are loaded in background threads.
