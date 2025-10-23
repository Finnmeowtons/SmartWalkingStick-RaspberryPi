import time
from datetime import datetime
from smartstick.hardware.get_gps import get_gps_coords
from smartstick.utils.config import BUTTON_PIN
import threading
from smartstick.services.tts_engine import tts_speak

class SOSButton:
    """
    Handles SOS events triggered by a physical button (long press)
    """
    def __init__(self, mqtt_client, device_id, button_pin=BUTTON_PIN, poll_interval=0.1, hold_time=5):
        """
        mqtt_client: instance of MQTTClient
        device_id: unique ID of the stick
        button_pin: GPIO pin number for SOS button (optional)
        poll_interval: how often to check the button state in seconds
        hold_time: seconds the button must be held to trigger SOS
        """
        self.mqtt_client = mqtt_client
        self.device_id = device_id
        self.button_pin = button_pin
        self.poll_interval = poll_interval
        self.hold_time = hold_time
        self._running = False

        if button_pin is not None:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def send_sos(self):
        """Send a single SOS message with GPS data"""
        lat, lon = get_gps_coords()
        data = {
            "deviceId": self.device_id,
            "sos": True,
            "lat": lat,
            "lon": lon,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        topic = f"stick/{self.device_id}/sos"
        self.mqtt_client.publish(topic, data)
        print("🚨 SOS sent:", data)

    def _button_loop(self):
        """Internal loop to check long-press button state"""
        while self._running:
            if self.GPIO.input(self.button_pin) == self.GPIO.LOW:  # button pressed
                press_start = time.time()
                while self.GPIO.input(self.button_pin) == self.GPIO.LOW:
                    time.sleep(0.05)
                    if time.time() - press_start >= self.hold_time:
                        print("[SOS] Button held for 5 seconds!")
                        tts_speak("Help Sent")
                        self.send_sos()
                        # wait until released to prevent repeat
                        while self.GPIO.input(self.button_pin) == self.GPIO.LOW:
                            time.sleep(0.05)
                        break
            time.sleep(self.poll_interval)

    def start_button_listener(self):
        """Start background thread to listen to physical button"""
        if self.button_pin is None:
            print("[SOS] No button pin configured!")
            return
        self._running = True
        threading.Thread(target=self._button_loop, daemon=True).start()

    def stop_button_listener(self):
        self._running = False
