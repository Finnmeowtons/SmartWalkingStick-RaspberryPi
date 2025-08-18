import requests

def query_beacondb(cell_towers=None, wifi_aps=None):
    """
    Fallback lookup via BeaconDB using cell tower or Wi-Fi data.
    """
    payload = {}
    if cell_towers:
        payload["cellTowers"] = cell_towers
    if wifi_aps:
        payload["wifiAccessPoints"] = wifi_aps

    headers = {"User-Agent": "SmartWalkingStick/1.0"}

    try:
        r = requests.post("https://api.beacondb.net/v1/geolocate", json=payload, headers=headers, timeout=5)
        print("BeaconDB HTTP:", r.status_code)
        print("Raw resp:", r.text)
        if r.status_code == 200 and r.text:
            data = r.json()
            loc = data.get("location", {})
            return {
                "lat": loc.get("lat"),
                "lon": loc.get("lng"),
                "accuracy": data.get("accuracy")
            }
    except Exception as e:
        print("BeaconDB error:", e)
    return None

query_beacondb()