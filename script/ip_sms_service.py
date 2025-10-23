import serial
import time
import subprocess
import re

# --- CONFIG ---
PHONE_NUMBER = "+639270734452"
CHECK_INTERVAL = 5  # seconds
SERIAL_PORT = "/dev/serial0"
BAUDRATE = 115200

def send_at(ser, cmd, delay=2):
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    resp = ser.read(ser.in_waiting or 4096).decode(errors="ignore")
    return resp

def send_sms(number: str, message: str) -> bool:
    """Send SMS via GSM. Returns True if success. Serial closes after sending."""
    try:
        ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=5)

        send_at(ser, "AT")
        send_at(ser, "AT+CMGF=1")
        time.sleep(1)

        ser.write(f'AT+CMGS="{number}"\r'.encode())
        time.sleep(1)
        ser.write((message + "\x1A").encode())  # CTRL+Z
        time.sleep(6)

        resp = ser.read(9999).decode(errors="ignore")
        print(resp)

        if "+CMGS:" in resp and "OK" in resp:
            print("✅ SMS sent successfully")
            return True
        else:
            print("❌ Failed to send SMS")
            return False

    except Exception as e:
        print(f"❌ GSM send failed: {e}")
        return False

    finally:
        try:
            ser.close()
        except:
            pass

def get_wifi_ip():
    """Return current Wi-Fi IP, or None if disconnected."""
    try:
        output = subprocess.check_output("hostname -I", shell=True).decode().strip()
        ips = re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", output)
        return ips[0] if ips else None
    except Exception:
        return None

def monitor_wifi_and_send_ip():
    """Monitor Wi-Fi and send IP SMS whenever it connects (dots replaced with spaces)."""
    last_ip = None
    last_ssid = None
    print("📡 Monitoring Wi-Fi connection...")

    while True:
        # Get current Wi-Fi SSID
        ssid = subprocess.getoutput("iwgetid -r").strip()

        # Retry a few times to get a valid IP
        ip = None
        for _ in range(5):
            ip = get_wifi_ip()
            if ip:
                break
            time.sleep(1)

        if ssid and ip:
            # Replace dots with spaces for SMS
            ip_msg = ip.replace(".", " ")

            # Send SMS if SSID changed or IP changed
            if ssid != last_ssid or ip != last_ip:
                print(f"✅ Connected to Wi-Fi '{ssid}'. IP: {ip}")
                message = f"My Smart Stick connected to Wi-Fi\nIP Address: {ip_msg}"
                print(f"📤 Sending SMS to {PHONE_NUMBER}...")
                send_sms(PHONE_NUMBER, message)

                last_ip = ip
                last_ssid = ssid

        else:
            # Wi-Fi disconnected
            if last_ssid:
                print("⚠️ Wi-Fi disconnected.")
            last_ip = None
            last_ssid = None

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_wifi_and_send_ip()
