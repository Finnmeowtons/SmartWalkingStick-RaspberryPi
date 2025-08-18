import socket
import threading
import time

ONLINE = True  # Global flag

def check_network(host="8.8.8.8", port=53, timeout=2, interval=5):
    """
    Continuously check network status in the background.
    Updates the global ONLINE flag.
    """
    global ONLINE
    while True:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            ONLINE = True
        except OSError:
            ONLINE = False
        time.sleep(interval)  # check every `interval` seconds

# Start the network monitor in a separate thread
threading.Thread(target=check_network, daemon=True).start()
