import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16, address=0x40)
for i in range(16):
    kit.servo[i].set_pulse_width_range(500, 2500)
    kit.servo[i].angle = None

while True:
    pin, angulo = input("Pin y angulo: ").split()
    pin = int(pin)
    angulo = int(angulo)
    kit.servo[pin].angle = angulo