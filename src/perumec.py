import time
import numpy as np
from adafruit_servokit import ServoKit
import gpiozero
import readchar

kit = ServoKit(channels=16, address=0x41)
for i in range(16):
    kit.servo[i].set_pulse_width_range(500, 2500)
    kit.servo[i].angle = None

button = gpiozero.Button(25, pull_up=True, bounce_time=0.01)
print("JUANBOT INICIALIZADO")
while True:
    kit.servo[3].angle = 90  # cadera izq
    kit.servo[2].angle = 90  # rodilla izq
    kit.servo[1].angle = 90  # tobillo izq
    kit.servo[0].angle = 90  # pie izq

    kit.servo[7].angle = 90  # cadera der
    kit.servo[6].angle = 90  # rodilla der
    kit.servo[5].angle = 90  # tobillo der
    kit.servo[4].angle = 90  # pie der

    kit.servo[13].angle = 90  # hombro izq
    kit.servo[12].angle = 30  # brazo izq

    kit.servo[14].angle = 90  # hombro der
    kit.servo[11].angle = 180-30  # brazo der

    servos = [
        kit.servo[3],  # cadera izq  (0)
        kit.servo[2],  # rodilla izq (1)
        kit.servo[1],  # tobillo izq (2)
        kit.servo[0],  # pie izq     (3)

        kit.servo[7],  # cadera der  (4)
        kit.servo[6],  # rodilla der (5)
        kit.servo[5],  # tobillo der (6)
        kit.servo[4],  # pie der     (7)

        kit.servo[13],  # hombro izq (8)
        kit.servo[12],  # brazo izq  (9)

        kit.servo[14],  # hombro der (10)
        kit.servo[11],  # brazo der  (11)
    ]

    print("ESPERANDO BOTON...")
    print(button.wait_for_active(timeout=None))
    time.sleep(2)

    Y = np.zeros(shape=len(servos))
    start = time.time()
    t = 0
    freq = 1.2
    BALANCEO = 0.105
    ZANCADA = 0.09
    BRACEO = 0.3
    while not button.value:
        # char = readchar.readkey()
        # t += (1/40) * (char == readchar.key.RIGHT)
        # t -= (1/40) * (char == readchar.key.LEFT)
        # if char: print(t)
        t = time.time() - start
        Y[:] = 0
        
        # Cálculos...
        fase = t*freq*2*np.pi
        Y[3] += -np.sin(fase)*(BALANCEO*1.325)
        Y[7] += np.sin(fase)*(BALANCEO)

        Y[0] -= np.cos(fase)*(ZANCADA)
        Y[4] += np.cos(fase)*(ZANCADA)

        Y[1] += np.cos(fase)*(ZANCADA)
        Y[5] -= np.cos(fase)*(ZANCADA)

        Y[9] = Y[11] = -0.7
        Y[8] -= np.sin(fase)*(BRACEO)
        Y[10] -= np.sin(fase)*(BRACEO)

        for i, (s, y) in enumerate(zip(servos, Y)):
            if i < 3 or i == 7 or i == 11:  # Sentido inverso
                s.angle = (-y+1) * 90
            else:
                s.angle = (y+1) * 90
        time.sleep(1/50)
    time.sleep(0.5)
