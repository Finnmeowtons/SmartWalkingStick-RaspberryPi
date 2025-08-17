import requests

API_KEY = "pk.beb8003c5cfb9d5cb74ae8beb0b7cecf"  # Replace with your key

# Example LAC and Cell ID from your earlier test
mcc = 515  # Philippines MCC
mnc = 2    # Smart Telecom MNC (example, adjust as needed)
lac = 21068
cid = 35447

url = f"http://opencellid.org/cell/get?key={API_KEY}&mcc={mcc}&mnc={mnc}&lac={lac}&cellid={cid}&format=json"

print("Requesting:", url)
response = requests.get(url)

print("Status Code:", response.status_code)
print("Response:", response.text)

if response.status_code == 200:
    data = response.json()
    if "lat" in data and "lon" in data:
        print(f"Location found: {data['lat']}, {data['lon']}")
    else:
        print("No location data found for this cell.")
else:
    print("Failed to fetch data from OpenCellID.")
