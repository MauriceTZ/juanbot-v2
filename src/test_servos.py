import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16, address=0x41)
for i in range(16):
    kit.servo[i].set_pulse_width_range(500, 2500)
    kit.servo[i].angle = None

pin = 11
kit.servo[pin].angle = 90-90
time.sleep(2)
kit.servo[pin].angle = 90+90
time.sleep(2)
kit.servo[pin].angle = 90
time.sleep(2)
kit.servo[pin].angle = None