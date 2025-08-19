import board, busio, adafruit_vl53l0x
import RPi.GPIO as GPIO, time

# ToF init
i2c = busio.I2C(board.SCL, board.SDA)
tof = adafruit_vl53l0x.VL53L0X(i2c)

# Motor PWM
PIN = 18
GPIO.setmode(GPIO.BCM); GPIO.setup(PIN, GPIO.OUT)
pwm = GPIO.PWM(PIN, 150); pwm.start(0)

def map_mm_to_duty(mm, near=150, far=1000):
    # Clamp and invert: near -> 90%, far -> 0%
    mm = max(near, min(far, mm))
    frac = (far - mm) / float(far - near)
    return int(90 * frac)  # cap at 90% to reduce harshness

try:
    while True:
        print("Distance: {} mm".format(tof.range))
        d = tof.range  # mm
        duty = map_mm_to_duty(d)
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.05)
finally:
    pwm.stop(); GPIO.cleanup()
