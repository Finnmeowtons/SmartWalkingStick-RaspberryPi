#!/usr/bin/env python3
import serial
import subprocess
import time
import os
import logging

LOG_FILE = "/home/cj/Desktop/smartstick/SmartStick/logs/net_failover.log"
SIM800L_PORT = "/dev/serial0"   # or "/dev/ttyAMA0" depending on your wiring
SIM800L_BAUD = 115200

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def check_internet(interface="wlan0"):
    """Check if interface has internet (ping Google DNS)"""
    try:
        subprocess.check_output(
            ["ping", "-I", interface, "-c", "2", "8.8.8.8"],
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False

def enable_mobile():
    print("➡️ Enabling SIM800L mobile connection...")
    logging.info("Enabling SIM800L mobile connection...")
    try:
        subprocess.Popen([
            "sudo", "pppd", "/dev/serial0", "115200",
            "connect", 'chat -v -f /etc/chatscripts/gprs',
            "noauth", "defaultroute", "usepeerdns"
        ])
        print("✅ PPP connection attempt started.")
    except Exception as e:
        logging.error(f"Failed to start PPP: {e}")
        print(f"❌ Failed to start PPP: {e}")

def disable_mobile():
    print("⬅️ Disabling SIM800L mobile connection...")
    logging.info("Disabling SIM800L mobile connection...")
    try:
        subprocess.run(["sudo", "poff"], check=True)
        print("✅ PPP connection stopped.")
    except Exception as e:
        logging.error(f"Failed to stop PPP: {e}")
        print(f"❌ Failed to stop PPP: {e}")

def main():
    mobile_enabled = False

    while True:
        if check_internet("wlan0"):
            print("Wi-Fi is up ✅")
            logging.info("WiFi is working.")
            if mobile_enabled:
                disable_mobile()
                mobile_enabled = False
        else:
            print("Wi-Fi down ❌, switching to SIM800L...")
            print("Checking mobile connection...")
            if check_internet("ppp0"):
                print("Connected!")
            else:
                print("Not Connected :(")
            logging.warning("WiFi down!")
            if not mobile_enabled:
                enable_mobile()
                mobile_enabled = True

        time.sleep(15)  # check every 10s

if __name__ == "__main__":
    main()
