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

### 🗺️ Walking Directions & Nearest Place Finder (OSRM Service)

* Integrates with **Open Source Routing Machine (OSRM)** for walking directions and navigation.
* Workflow:
  1. Current location retrieved from **GPS**.
  2. User gives a voice command like:
     * `"Gabay papunta sa SM"` 
     * `"Turo papunta sa Jollibee"`
     * Short and comfortable for Tagalog users: `"Punta sa [place]"`, `"Turo sa [place]"`.
  3. The system finds the **nearest matching place** using **Nominatim**.
  4. Coordinates are sent to OSRM for walking directions.
* **Turn-by-turn guidance**:
  * Instructions are spoken via **TTS**.
  * `json_to_route()` parses OSRM JSON into a human-friendly summary in Tagalog.
* **Live navigation with `osrm_navigate()`**:
  * Continuously tracks GPS location.
  * Announces **next step** until arrival.
  * Supports arrival context: `"Nakarating ka na sa [destination]"`.
* **Fallback**:
  * If no nearby match is found, the system uses **Gemini API** to give a rough guide.
  * If offline, provides a **hardcoded fallback message**.

### ✉️ SMS Reader

* Integrates with **SIM800L module** to read and manage SMS messages.
* Designed for **blind accessibility** with full **voice control**.
* Core functions:
  * `read_sms(unread_only=True)`: Fetches SMS messages (all or only unread).
  * `read_current_sms()`: Reads the currently selected message using TTS.
  * `next_sms()`: Moves to the next message and reads it aloud.
  * `repeat_sms()`: Repeats the current message for clarity.
  * `stop_sms_mode()`: Exits SMS reading mode.
* **Voice commands**:
  * `"basahin"` → Activates SMS mode and starts reading.
  * `"sunod"` → Moves to the next SMS.
  * `"ulitin"` → Repeats the last SMS.
  * `"stop"` / `"tapos"` → Exits SMS mode.
* Messages are spoken via **TTS engine** so blind users can hear both **sender** and **message content**.

### ⚡ Hybrid Preload System (memo)

* **Fast startup**: loads essentials like Piper immediately.
* **Lazy loading**: heavy models (YOLO, Gemini) are loaded in background threads.
