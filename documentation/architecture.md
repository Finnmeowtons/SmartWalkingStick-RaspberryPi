# Smart Walking Stick – System Architecture

## Overview

The Smart Walking Stick is designed to assist visually impaired users by combining voice activation, object detection, distance sensing, GPS tracking, and real-time feedback through audio. The system leverages a Raspberry Pi 4 Model B as the central processing unit, integrating various sensors and communication modules.

---

## Hardware Components

* **Raspberry Pi 4 Model B (4GB RAM)** – Main controller for AI, speech, and device coordination.
* **Web Camera** – Captures images for object detection (YOLOv8).
* **Time-of-Flight (ToF) Sensor (VL53L0X)** – Measures distance to nearby obstacles.
* **GPS(NEO-M6N) + SIM Module(SIM800L V2)** – Provides real-time location tracking and emergency communication.
* **Headphones with Microphone** – Used for voice activation (wake word) and text-to-speech feedback.
* **Powerbank** – Portable power supply.

---

## Software Stack

* **Operating System:** Raspberry Pi OS (Bookworm)
* **Voice Recognition:** Vosk (Tagalog-English model)
* **Wake Word Detection:** Custom trigger (“sabihin mo kay Kumare/Kumpare…”)
* **Object Detection:** YOLOv8 (with future custom training for crosswalks, potholes, etc.)
* **Text-to-Speech:** Piper (offline) and Google TTS (online fallback, with Tagalog support)
* **GPS Parsing:** NMEA sentence decoding over UART
* **Networking:** MQTT/HTTP for optional cloud features (future)

---

## System Workflow

1. **Idle Mode** – The system continuously listens for the wake word via the microphone.
2. **Voice Activation** – Once triggered, user commands are transcribed by Vosk (Tagalog-English).
3. **Processing**

   * Commands may query ChatGPT, request navigation info, or ask for surroundings.
   * The camera captures frames → YOLOv8 detects objects → system announces obstacles (left/right).
   * The ToF sensor provides real-time distance alerts.
   * GPS reports location; SIM module allows emergency SMS or cloud reporting.
4. **Output** – Responses are converted to speech via TTS and played through headphones.
5. **Fallback Modes** – If no internet, the system relies entirely on offline Vosk + Piper TTS.

---

## Data Flow Diagram

```
[Microphone] --> [Wake Word Detection] --> [Speech-to-Text (Vosk)] 
        |                               
        v                               
   [Command Processor] --> [Object Detection (YOLOv8)]
        |                  [ToF Sensor Input]
        |                  [GPS/SIM Data]
        v
 [Response Generator] --> [TTS (Piper/Google)] --> [Headphones]
```

---

## Modes of Operation

* **Offline Mode** – Full local processing using Vosk + Piper.
* **Online Mode** – Uses Google TTS and optional cloud integration.
* **Emergency Mode** – Sends GPS location via SMS through SIM module.

---

## Future Enhancements

* Train YOLOv8 model for blind-specific classes (crosswalks, potholes).
* Add haptic feedback via vibration motor.
* Integrate cloud-based analytics and navigation assistance.

---

