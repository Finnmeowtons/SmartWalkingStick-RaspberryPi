import serial, time

ser = serial.Serial("/dev/serial0", baudrate=115200, timeout=2)

def send_at(cmd, delay=1):
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    resp = ser.read(ser.in_waiting or 1024).decode(errors="ignore")
    print(resp)
    return resp

# Test basic AT
send_at("AT")
send_at("AT+CMGF=1")  # Text mode
send_at('AT+CMGS="+639270734452"')  # Use +63!
ser.write(b"Hello from Pi\x1A")  # CTRL+Z
time.sleep(5)
print(ser.read(9999).decode(errors="ignore"))
