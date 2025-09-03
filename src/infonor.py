import time
import numpy as np
from adafruit_servokit import ServoKit
import gpiozero
import readchar
import atexit

kit = ServoKit(channels=16, address=0x40)

MIN_IMP = 500
MAX_IMP = 2500

for i in range(16):
    kit.servo[i].set_pulse_width_range(MIN_IMP, MAX_IMP)


def chau(kit: ServoKit):
    print("APAGANDO SERVOS...")
    # for i in range(16):
    #     kit.servo[i].angle = 90
    time.sleep(0.5)
    for i in range(16):
        kit.servo[i].angle = None


atexit.register(chau, kit)

while True:
    kit.servo[3].angle = 80  # cadera izq
    kit.servo[2].angle = 90  # rodilla izq
    kit.servo[1].angle = 90  # tobillo izq
    kit.servo[0].angle = 90  # pie izq

    kit.servo[7].angle = 100  # cadera der
    kit.servo[6].angle = 90  # rodilla der
    kit.servo[5].angle = 90  # tobillo der
    kit.servo[4].angle = 90  # pie der

    kit.servo[13].angle = 90  # hombro izq
    kit.servo[12].angle = 40  # brazo izq

    kit.servo[14].angle = 90  # hombro der
    kit.servo[11].angle = 180-40  # brazo der

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

    Y = np.zeros(shape=len(servos))
    start = time.time()
    t = 0
    freq = 0.25  # 1.2
    BALANCEO = 0.1  # 0.105
    ZANCADA = 0.1  # 0.09
    BRACEO = 0.3  # 0.3
    SENTADILLA = 0.3
    RESORTE = 0.1

    INCLINACION = 0.1
    while True:
        # char = readchar.readkey()
        # t += (1/40) * (char == readchar.key.RIGHT)
        # t -= (1/40) * (char == readchar.key.LEFT)
        # if char: print(t)
        t = time.time() - start
        print(t)
        Y[:] = 0

        # Cálculos...
        fase = t*freq*2*np.pi
        Y[0] -= SENTADILLA + 0.2 + np.sin(fase) * RESORTE
        Y[4] += SENTADILLA + 0.2 - np.sin(fase) * RESORTE

        Y[1] += SENTADILLA * 2 + np.sin(fase) * RESORTE * 2
        Y[5] -= SENTADILLA * 2 - np.sin(fase) * RESORTE * 2

        Y[2] += SENTADILLA + np.sin(fase) * RESORTE
        Y[6] -= SENTADILLA - np.sin(fase) * RESORTE

        Y[3] -= np.cos(fase)*(BALANCEO * 1.1)
        Y[7] -= np.cos(fase)*(BALANCEO)

        # Y[0] += np.sin(fase)*(ZANCADA)
        # Y[4] += np.sin(fase)*(ZANCADA)

        # Y[1] += np.cos(fase)*(ZANCADA)
        # Y[5] -= np.cos(fase)*(ZANCADA)

        # # Y[9] = Y[11] = -0.7
        # Y[8] -= np.sin(fase)*(BRACEO)
        # Y[10] -= np.sin(fase)*(BRACEO)

        print(Y)

        for i, (s, y) in enumerate(zip(servos, Y)):
            if np.isnan(y):
                s.angle = None
            else:
                s.angle = (y+1) * 90
        time.sleep(1/50)
    time.sleep(0.5)
