# wifi_monitor.py
import subprocess
import re
import time

PHONE_NUMBER = "+639270734452"
CHECK_INTERVAL = 5  # seconds

last_ip = None
print("📡 Monitoring Wi-Fi...")

while True:
    try:
        # Get current IP
        output = subprocess.check_output("hostname -I", shell=True).decode().strip()
        ips = re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", output)
        ip = ips[0] if ips else None

        if ip and ip != last_ip:
            print(f"✅ Wi-Fi connected. New IP: {ip}")
            message = f"My Smart Stick connected to Wi-Fi.\nIP Address: {ip}"
            print("📤 Sending SMS via standalone script...")
            subprocess.run(
                ["python3", "/home/cj/Desktop/smartstick/SmartStick/script/ip_sms_service.py", PHONE_NUMBER, message],
                check=False
            )
            last_ip = ip

        elif not ip and last_ip:
            print("⚠️ Wi-Fi disconnected.")
            last_ip = None

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print(f"⚠️ Monitor error: {e}")
        time.sleep(CHECK_INTERVAL)
