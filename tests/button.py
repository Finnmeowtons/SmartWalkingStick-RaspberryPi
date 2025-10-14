import RPi.GPIO as GPIO
import time

BUTTON_PIN = 4   # GPIO4 (pin 7)
COOLDOWN = 30    # seconds
HOLD_TIME = 5    # seconds

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_pressed = 0

print("Waiting for button press...")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # button pressed
            press_start = time.time()
            
            # keep checking if still held down
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                if time.time() - press_start >= HOLD_TIME:
                    now = time.time()
                    if now - last_pressed >= COOLDOWN:
                        print("✅ SOS Triggered! Sending SMS...")
                        # TODO: Call your SMS function here
                        last_pressed = now
                    else:
                        print("⏳ Button cooling down. Please wait...")
                    break
                time.sleep(0.1)  # debounce / reduce CPU use
            time.sleep(0.5)  # debounce
        else:
            time.sleep(0.1)  # idle wait

except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
