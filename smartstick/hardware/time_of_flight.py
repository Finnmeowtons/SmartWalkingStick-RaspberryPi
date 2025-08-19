import board
import busio
import adafruit_vl53l0x

_sensor = None
_enabled = False

def init_sensor():
    global _sensor
    i2c = busio.I2C(board.SCL, board.SDA)
    _sensor = adafruit_vl53l0x.VL53L0X(i2c)
    return _sensor

def enable():
    global _enabled
    if _sensor is None:
        init_sensor()
    _enabled = True

def disable():
    global _enabled
    _enabled = False

def get_distance():
    if _enabled and _sensor:
        return _sensor.range
    return None
