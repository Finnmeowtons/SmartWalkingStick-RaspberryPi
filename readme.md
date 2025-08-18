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
* Cleanly separated into `speech.py` for modularity.

### 🧩 Modular Design
* `base_dir` is defined globally so all modules can access paths consistently.
* `vision.py` → object detection logic.
* `speech.py` → TTS logic (offline + online).
* `network.py` → connectivity checks.
* `main.py` → orchestrates everything.

---

## ⚡ Hybrid Preload System (memo)
- **Fast startup**: loads essentials like Piper immediately.  
- **Lazy loading**: heavy models (YOLO, Gemini) are loaded in background threads.  
- Access them later with:
  ```python
  preload.get_resource("cv2_model")
