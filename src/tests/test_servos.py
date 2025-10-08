import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16, address=0x40)
for i in range(16):
    kit.servo[i].set_pulse_width_range(500, 2500)
    kit.servo[i].angle = None

while True:
    pin, angulo = input("(pin, angulo): ").split(",")
    pin = int(pin.strip())
    angulo = int(angulo.strip())
    if angulo < 0: angulo = None
    print(f"Pin = {pin}, Ángulo = {angulo}")
    kit.servo[pin].angle = angulo