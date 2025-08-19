import RPi.GPIO as GPIO
import time

_pwm = None
_enabled = False

def init_vibrator(pin=18, freq=150):
    global _pwm
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    _pwm = GPIO.PWM(pin, freq)
    _pwm.start(0)
    return _pwm

def enable():
    global _enabled
    if _pwm is None:
        init_vibrator()
    _enabled = True

def disable():
    global _enabled
    _enabled = False
    if _pwm:
        _pwm.ChangeDutyCycle(0)

def set_strength(duty):
    if _enabled and _pwm:
        _pwm.ChangeDutyCycle(duty)

def distance_to_duty(distance_mm):
    if distance_mm is None:
        return 0
    if distance_mm > 2000:
        distance_mm = 2000
    return 100 - int((distance_mm / 2000) * 100)

def buzz(duty=80, duration=0.3):
    set_strength(duty)
    time.sleep(duration)
    set_strength(0)

def cleanup():
    if _pwm:
        _pwm.stop()
    GPIO.cleanup()
