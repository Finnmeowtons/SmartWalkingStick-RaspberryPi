import time
from gps3 import gps3

def get_gps_coords(timeout=30):
    """Return (latitude, longitude) as floats if available."""
    gps_socket = gps3.GPSDSocket()
    data_stream = gps3.DataStream()
    
    gps_socket.connect()
    gps_socket.watch()

    start_time = time.time()

    for new_data in gps_socket:
        if time.time() - start_time > timeout:
            print("Timeout: GPS fix not acquired.")
            return None, None

        if new_data:
            data_stream.unpack(new_data)
            lat = data_stream.TPV.get('lat', None)
            lon = data_stream.TPV.get('lon', None)
            
            if lat != 'n/a' and lon != 'n/a' and lat is not None and lon is not None:
                return float(lat), float(lon)

    return None, None

if __name__ == "__main__":
    lat, lon = get_gps_coords()
    if lat and lon:
        print(f"Latitude: {lat}, Longitude: {lon}")
    else:
        print("Could not get GPS coordinates.")
