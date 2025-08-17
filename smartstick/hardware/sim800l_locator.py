import serial
import time
import requests

# Open serial connection to SIM800L
ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

def send_at(cmd, delay=0.5):
    ser.write((cmd + '\r\n').encode())
    time.sleep(delay)
    reply = ser.read_all().decode(errors="ignore")
    return reply.strip()

# Step 1: Check signal strength
csq = send_at("AT+CSQ")
print("Signal:", csq)

# Step 2: Enable extended CREG
send_at("AT+CREG=2")

# Step 3: Get LAC and CellID
creg = send_at("AT+CREG?")
print("CREG reply:", creg)

# Parse LAC and CellID
import re
match = re.search(r'\+CREG: \d,\d,"([0-9A-F]+)","([0-9A-F]+)"', creg)
if match:
    lac = match.group(1).strip()
    cellid = match.group(2).strip()

    print("LAC:", lac, "CellID:", cellid)

    # Convert HEX → decimal
    lac_dec = int(lac, 16)
    cellid_dec = int(cellid, 16)

    print("LAC (dec):", lac_dec, "CellID (dec):", cellid_dec)

    # Send to Mozilla Location Service
    url = "https://location.services.mozilla.com/v1/geolocate?key=test"
    payload = {
        "cellTowers": [
            {
                "radioType": "gsm",
                "mobileCountryCode": 515,   # PH MCC
                "mobileNetworkCode": 3,    # adjust for your SIM
                "locationAreaCode": lac_dec,
                "cellId": cellid_dec
            }
        ]
    }

    r = requests.post(url, json=payload)
    print("HTTP Status:", r.status_code)
    print("Raw response:", r.text)
else:
    print("Could not parse CREG response")