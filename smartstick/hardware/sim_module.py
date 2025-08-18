import serial
import time
import re

ser = serial.Serial("/dev/serial0", baudrate=115200, timeout=1)

def send_at(command, delay=1):
    """Send AT command and return response"""
    ser.write((command + "\r\n").encode())
    time.sleep(delay)
    resp = ser.read(ser.in_waiting).decode(errors="ignore")
    return resp.strip()

def get_operator():
    resp = send_at("AT+COPS?")
    # Example: +COPS: 0,0,"Globe Telecom",2
    if "+COPS" in resp:
        parts = resp.split(",")
        operator = parts[2].replace('"', '') if len(parts) > 2 else "Unknown"
        return operator
    return "Unknown"

def get_cell_info():
    send_at("AT+CREG=2")  # enable extended +CREG responses with LAC/CellID
    resp = send_at("AT+CREG?")
    # Example: +CREG: 2,1,"1A2B","3456"
    lac, cellid = None, None

    match = re.search(r'\+CREG: \d,\d,"([0-9A-F]+)","([0-9A-F]+)"', resp)

    print(resp)

    if match:
        try:
            lac = match.group(1).strip()
            cellid = match.group(2).strip()

            print("LAC:", lac, "CellID:", cellid)

            # Convert HEX → decimal
            lac_dec = int(lac, 16)
            cellid_dec = int(cellid, 16)

            print("LAC (dec):", lac_dec, "CellID (dec):", cellid_dec)            
        except Exception as e:
            print("Parse error:", e)

    return lac, cellid

