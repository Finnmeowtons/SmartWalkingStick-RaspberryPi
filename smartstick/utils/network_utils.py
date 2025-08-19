import socket
import threading
import time

ONLINE = True  # Global flag

def check_network(host="8.8.8.8", port=53, timeout=2, interval=5):

    global ONLINE
    while True:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            if ONLINE == False:
                print("Online")
            ONLINE = True
        except OSError:
            if ONLINE == True:
                print("offline")
            ONLINE = False
        time.sleep(interval) 

threading.Thread(target=check_network, daemon=True).start()
