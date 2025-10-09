import time
import numpy as np
from math import sin, cos
from adafruit_servokit import ServoKit
import gpiozero
import readchar
import atexit
from pprint import pp

from IK import Pierna

kit = ServoKit(channels=16)

MIN_IMP = 500
MAX_IMP = 2500

for i in range(16):
    kit.servo[i].set_pulse_width_range(MIN_IMP, MAX_IMP)


pierna_izq = Pierna(8, 6.4,
                    kit.servo[3], kit.servo[2], kit.servo[1], kit.servo[0])
pierna_der = Pierna(8, 6.4,
                    kit.servo[0], kit.servo[1], kit.servo[2], kit.servo[3], False, False, False, False)

servos = {
    # Nombre: (Pin, Angulo medio (+ -> sentido horario, - -> sentido antihorario) )
    "cadera_derecha": (0, 90),
    "rodilla_derecha": (1, 90),
    "tobillo_derecha": (2, -90),
    "pie_derecha": (3, -80),

    "cadera_izquierda": (4, 90),
    "rodilla_izquierda": (5, 90),
    "tobillo_izquierda": (6, -90),
    "pie_izquierda": (7, 93),

    "hombro_derecha": (8, 90),
    "hombro_izquierda": (9, 90),
}


def chau(kit: ServoKit):
    print("APAGANDO SERVOS...")
    for i in range(16):
        kit.servo[i].angle = None


atexit.register(chau, kit)

button = gpiozero.Button(25, pull_up=True, bounce_time=0.01)

print("JUANBOT INICIALIZADO")
while True:

    print("ESPERANDO BOTON...")
    # button.wait_for_active(timeout=None)
    # button.wait_for_inactive(timeout=None)
    print("EJECUTANDO!!")

    Y = {k: 0 for k in servos.keys()}
    start = time.time()
    t = 0
    freq = 0.4  # 1.2
    BALANCEO = 0.115  # 0.105
    ZANCADA = 0.1  # 0.09
    BRACEO = 0.3  # 0.3

    INCLINACION = 0.1
    while not button.value:
        # char = readchar.readkey()
        # t += (1/40) * (char == readchar.key.RIGHT)
        # t -= (1/40) * (char == readchar.key.LEFT)
        # if char: print(t)
        t = time.time() - start
        print(t)
        # Y[:] = 0

        fase = t*freq*2*np.pi

        Y["cadera_derecha"] = sin(fase) * BALANCEO
        Y["cadera_izquierda"] = -sin(fase) * BALANCEO

        # Cálculos...
        # fase = t*freq*2*np.pi
        # Y[3] += -np.sin(fase)*(BALANCEO)
        # Y[7] += np.sin(fase)*(BALANCEO*1.05)

        # Y[0] -= np.cos(fase)*(ZANCADA)
        # Y[4] += np.cos(fase)*(ZANCADA)
        # Y[0] += INCLINACION
        # Y[4] += INCLINACION

        # Y[1] += np.cos(fase)*(ZANCADA)
        # Y[5] -= np.cos(fase)*(ZANCADA)

        # Y[9] = Y[11] = -0.7
        # Y[8] -= np.sin(fase)*(BRACEO)
        # Y[10] -= np.sin(fase)*(BRACEO)

        # Y[2] = None
        # Y[6] = None
        pp(Y)

        for k, v in Y.items():
            if v == None:
                kit.servo[servos[k][0]].angle = None
            else:
                sentido = 1 if servos[k][1] >= 0 else -1
                angle = (v * sentido + 1) * 90 + (abs(servos[k][1]) - 90)
                kit.servo[servos[k][0]].angle = angle

            # elif i < 3 or i == 7 or i == 11:  # Sentido inverso
            #     s.angle = (-y+1) * 90
            # else:
            #     s.angle = (y+1) * 90
        time.sleep(1/50)
    time.sleep(0.5)
