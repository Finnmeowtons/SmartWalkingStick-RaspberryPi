# mqtt_client.py
import json
import time
import threading
import paho.mqtt.client as mqtt
from datetime import datetime
from smartstick.utils.config import DEVICE_ID, MQTT_BROKER, MQTT_PORT

class MQTTClient:
    def __init__(self, device_id, broker, port, publish_interval=10):
        self.device_id = device_id
        self.broker = broker
        self.port = port
        self.publish_interval = publish_interval
        self.client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv5)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

        # Lock to make MQTT publish thread-safe
        self._lock = threading.Lock()

        # while True:
        #     time.sleep(1)

    # ----------------------
    # MQTT Callbacks
    # ----------------------
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            print("[MQTT] Connected successfully!")
        else:
            print(f"[MQTT] Failed to connect, reason: {reason_code}")

    def on_disconnect(self, client, userdata, rc, properties=None):
        print("[MQTT] Disconnected. Attempting reconnect...")
        self.reconnect()

    def on_publish(self, client, userdata, mid, properties=None, reason_code=None):
        print(f"[MQTT] Message published (mid={mid})")

    # ----------------------
    # Connect & Reconnect
    # ----------------------
    def connect(self):
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            print(f"[MQTT] Connection failed: {e}")
            time.sleep(3)
            self.reconnect()

    def reconnect(self):
        while True:
            try:
                self.client.reconnect()
                print("[MQTT] Reconnected successfully!")
                break
            except Exception as e:
                print(f"[MQTT] Reconnect failed: {e}")
                time.sleep(5)

    # ----------------------
    # Publish Helpers
    # ----------------------
    def publish(self, topic, data, qos=1):
        """Thread-safe MQTT publish"""
        payload = json.dumps(data)
        with self._lock:
            self.client.publish(topic, payload, qos=qos)
        print(f"[MQTT] Published to {topic}: {payload}")

    # ----------------------
    # GPS Background Loop
    # ----------------------
    def start_location_loop(self, get_coords_func):
        """Continuously publish location using provided get_coords_func()"""
        def loop():
            while True:
                lat, lon = get_coords_func()
                if lat is not None and lon is not None:
                    data = {
                        "deviceId": self.device_id,
                        "lat": lat,
                        "lon": lon,
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                    self.publish(f"stick/{self.device_id}/location", data)
                else:
                    print("[MQTT] Could not get GPS coordinates.")
                time.sleep(self.publish_interval)

        threading.Thread(target=loop, daemon=True).start()

    # ----------------------
    # SOS Publisher
    # ----------------------
    def send_sos(self, message="SOS button pressed!"):
        """Immediately publish an SOS alert in a separate thread"""
        def send():
            data = {
                "deviceId": self.device_id,
                "message": message,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self.publish(f"stick/{self.device_id}/sos", data)

        threading.Thread(target=send, daemon=True).start()
