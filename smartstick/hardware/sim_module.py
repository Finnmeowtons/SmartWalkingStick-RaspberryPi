import serial
import time
import re
from smartstick.services.tts_engine import tts_speak

ser = serial.Serial("/dev/serial0", baudrate=115200, timeout=1)
sms_messages = []   # list of tuples: (index, sender, content)
current_pointer = 0

def send_at(command, delay=1):
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

def send_sms(number, message):
    print(send_at("AT+CMGF=1"))  # Set text mode
    print(send_at(f'AT+CMGS="{number}"'))  # Set recipient
    ser.write((message + "\x1A").encode())  # \x1A = CTRL+Z to send
    time.sleep(3)
    resp = ser.read(ser.in_waiting).decode(errors="ignore")
    print(resp)
    return resp

def call_number(number, duration=40):
    print(send_at(f"ATD{number};"))  # Dial the number
    time.sleep(duration)  # Wait for the call duration
    print(send_at("ATH"))  # Hang up
    return "Call ended"

def read_sms(unread_only=True):
    send_at("AT+CMGF=1")  # Text mode
    cmd = 'AT+CMGL="REC UNREAD"' if unread_only else 'AT+CMGL="ALL"'
    resp = send_at(cmd, delay=5)
    time.sleep(3)
    print(resp)
    messages = []
    print(messages)
    for block in resp.split("+CMGL:")[1:]:
        lines = block.strip().split("\n")
        header = lines[0].split(",")
        index = int(header[0])
        status = header[1].replace('"','')
        sender = header[2].replace('"','')
        content = "\n".join(lines[1:])
        messages.append((index, status, sender, content))

    return messages




if __name__ == "__main__":
    start_reading_sms()
    time.sleep(10)
    next_message()
    time.sleep(10)
    next_message()
    time.sleep(10)
    repeat_message()
    # send_sms("+639270734452", "Warrup")
    # call_number("+639270734452")
    # print(send_at("AT"))          # should return OK
    # print(send_at("AT+CPIN?"))    # should return READY
    # print(send_at("AT+CSQ"))      # signal strength (0–31, >10 is usable)
    # print(send_at("AT+CREG?"))    # should return ,1 (registered to home network)
    # print(send_at("AT+CGATT?"))   # check GPRS attach status, 1 = attached
    # # print(send_at("AT+CGATT=1"))  # force attach if needed
    # print(send_at("AT+CIPSHUT", delay=5))   # shuts down previous IP session
    # print(send_at('AT+CSTT="internet","",""'))
    # print(send_at("AT+CIICR", delay=2))  # bring up wireless connection
    # print(send_at("AT+CIFSR"))  # should return an IP like 10.x.x.x
    # print(send_at('AT+CIPSTART="TCP","google.com","80"', delay=5))
    # send_at("AT+CIPSEND")
    # time.sleep(1)
    # ser.write(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n\x1A")
    # resp = ser.read(9999).decode(errors="ignore")
    # print(resp)
