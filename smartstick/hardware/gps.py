import serial
import requests
import time
from smartstick.utils.config import GPS_PORT, GPS_BAUD, MLS_URL

# --- Helper: Parse GPS NMEA for lat/lon ---
def parse_gpgga(line):
    try:
        parts = line.split(",")
        if parts[0].endswith("GGA") and parts[2] and parts[4]:
            lat = float(parts[2])
            lon = float(parts[4])
            # Convert from NMEA to decimal degrees
            lat = (lat // 100) + (lat % 100) / 60
            lon = (lon // 100) + (lon % 100) / 60
            if parts[3] == "S":
                lat = -lat
            if parts[5] == "W":
                lon = -lon
            return lat, lon
    except:
        return None
    return None

# --- Try GPS ---
def get_gps_location(timeout=10):
    try:
        ser = serial.Serial(GPS_PORT, GPS_BAUD, timeout=1)
        start = time.time()
        while time.time() - start < timeout:
            line = ser.readline().decode(errors="ignore").strip()
            if line.startswith("$GPGGA"):
                coords = parse_gpgga(line)
                if coords:
                    return {"source": "GPS", "lat": coords[0], "lon": coords[1]}
    except Exception as e:
        print("GPS Error:", e)
    return None

# --- Mozilla Wi-Fi/Cell positioning ---
def get_mozilla_location(wifi=[], cells=[]):
    payload = {}
    if wifi:
        payload["wifiAccessPoints"] = wifi
    if cells:
        payload["cellTowers"] = cells

    try:
        r = requests.post(MLS_URL, json=payload)
        data = r.json()
        return {
            "source": "Mozilla",
            "lat": data["location"]["lat"],
            "lon": data["location"]["lng"],
            "accuracy": data.get("accuracy", None)
        }
    except Exception as e:
        print("Mozilla Error:", e)
        return None

# --- Unified location function ---
def get_location():
    # 1. Try GPS
    gps_loc = get_gps_location()
    if gps_loc:
        return gps_loc

    # 2. Fallback: Mozilla (dummy Wi-Fi + Cell here, replace with real data)
    wifi = [
        {"macAddress": "01:23:45:67:89:AB", "signalStrength": -65},
        {"macAddress": "01:23:45:67:89:AC", "signalStrength": -70}
    ]
    cells = [
        {
        "radioType": "gsm",
        "mobileCountryCode": 515,   # MCC = 515 (Philippines)
        "mobileNetworkCode": 3,    # Smart
        "locationAreaCode": 5123,   # from your modem
        "cellId": 21532831          # from your modem
        }
    ]
    return get_mozilla_location(wifi, cells)

# --- Example run ---
if __name__ == "__main__":
    loc = get_location()
    if loc:
        print(f"Source: {loc['source']} | Lat: {loc['lat']} | Lon: {loc['lon']}")
    else:
        print("No location available.")
