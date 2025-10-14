import time
from gps3 import gps3

# Default coordinates (e.g., school, HQ, or safe fallback)
DEFAULT_LAT = 16.02131855757801
DEFAULT_LON = 120.3295448168829

def get_gps_coords(timeout=30):
    # """Return (latitude, longitude) as floats if available, or defaults if not."""
    # gps_socket = gps3.GPSDSocket()
    # data_stream = gps3.DataStream()

    # gps_socket.connect()
    # gps_socket.watch()

    # start_time = time.time()

    # for new_data in gps_socket:
    #     if time.time() - start_time > timeout:
    #         print("Timeout: GPS fix not acquired. Using default coordinates.")
    #         return DEFAULT_LAT, DEFAULT_LON

    #     if new_data:
    #         data_stream.unpack(new_data)
    #         lat = data_stream.TPV.get('lat', None)
    #         lon = data_stream.TPV.get('lon', None)

    #         if lat != 'n/a' and lon != 'n/a' and lat is not None and lon is not None:
    #             return float(lat), float(lon)

    # print("Could not get GPS coordinates. Using default coordinates.")
    return DEFAULT_LAT, DEFAULT_LON


if __name__ == "__main__":
    lat, lon = get_gps_coords()
    print(f"Latitude: {lat}, Longitude: {lon}")
