import time
from math import sin, cos, radians
import pygame as pg
import numpy as np
from adafruit_servokit import ServoKit
import gpiozero
import readchar
import atexit
from IK import Pierna
from util import map_range

pg.init()
# This dict can be left as-is, since pygame will generate a
# pygame.JOYDEVICEADDED event for every joystick connected
# at the start of the program.
joysticks = {}


def pygane_event_handle():
    global estado
    # Event processing step.
    # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
    for event in pg.event.get():
        if event.type == pg.JOYBUTTONDOWN:
            print("Joystick button pressed.")

        if event.type == pg.JOYBUTTONUP:
            print("Joystick button released.")

        # Handle hotplugging
        if event.type == pg.JOYDEVICEADDED:
            # This event will be generated when the program starts for every
            # joystick, filling up the list without needing to create them manually.
            joy = pg.joystick.Joystick(event.device_index)
            joysticks[joy.get_instance_id()] = joy
            print(f"Joystick {joy.get_instance_id()} connencted")

        if event.type == pg.JOYDEVICEREMOVED:
            del joysticks[event.instance_id]
            print(f"Joystick {event.instance_id} disconnected")


clock = pg.time.Clock()

kit = ServoKit(channels=16, address=0x40)

MIN_IMP = 500
MAX_IMP = 2500

Zancada = 2  # cm
Balanceo = 8  # grados
Altura = 12 # cm
Periodo = 1  # seg

FPS = 30
dt = 0

brazo_der = [0, 0]
brazo_izq = [0, 0]

estado = "parado"

for i in range(16):
    kit.servo[i].set_pulse_width_range(MIN_IMP, MAX_IMP)


def chau(kit: ServoKit):
    print("APAGANDO SERVOS...")
    pg.quit()


pierna_izq = Pierna(8, 6.4,
                    kit.servo[4], kit.servo[5], kit.servo[6], kit.servo[7], False, False, False, True,
                    o4=3, xoff=0.5, yoff=0)
pierna_der = Pierna(8, 6.4,
                    kit.servo[0], kit.servo[1], kit.servo[2], kit.servo[3], False, False, False, False,
                    o4=-12.5, xoff=1.5, yoff=-0.2)

atexit.register(chau, kit)


while True:
    start_time = time.time()

    pierna_der.angulos(0, Altura)
    pierna_izq.angulos(0, Altura)
    time.sleep(1)

    while True:
        pygane_event_handle()
        for joystick in joysticks.values():
            axis1 = joystick.get_axis(0)
            axis2 = joystick.get_axis(1)
            axis3 = joystick.get_axis(3)
            axis4 = joystick.get_axis(4)

            brazo_der[0] += axis1 * (abs(axis1) > 0.1) * dt * 10
            brazo_der[1] += axis2 * (abs(axis2) > 0.1) * dt * 10
            brazo_izq[0] += axis3 * (abs(axis3) > 0.1) * dt * 10
            brazo_izq[1] += axis4 * (abs(axis4) > 0.1) * dt * 10

            # brazo_der = [np.clip(a + 90, 0, 180) for a in brazo_der]
            # brazo_izq = [np.clip(a + 90, 0, 180) for a in brazo_izq]
            kit.servo[9].angle = 90 + brazo_der[0]

            print(f"{brazo_der}, {brazo_izq}")

            hat = joystick.get_hat(0)
            if hat[1] == 1:
                if estado == "parado":
                    estado = "empieza_caminar"
                    for t in np.linspace(0, radians(90), int(FPS * Periodo)):
                        pierna_der.angulos(Zancada * sin(t),
                                           Altura,
                                           p=Balanceo * -2)
                        pierna_izq.angulos(Zancada * -sin(t),
                                           Altura,
                                           p=Balanceo)
                        dt = clock.tick(FPS) / 1000
                elif estado == "empieza_caminar" or estado == "caminando_izq":
                    estado = "caminando_der"
                    for t in np.linspace(radians(90), radians(-90), int(FPS * Periodo)):
                        pierna_der.angulos(Zancada * sin(t),
                                           Altura,
                                           p=Balanceo)
                        pierna_izq.angulos(Zancada * -sin(t),
                                           Altura,
                                           p=Balanceo * -2)
                        dt = clock.tick(FPS) / 1000
                elif estado == "caminando_der":
                    estado = "caminando_izq"
                    for t in np.linspace(radians(-90), radians(90), int(FPS * Periodo)):
                        pierna_der.angulos(Zancada * sin(t),
                                           Altura,
                                           p=Balanceo * -2)
                        pierna_izq.angulos(Zancada * -sin(t),
                                           Altura,
                                           p=Balanceo)
                        dt = clock.tick(FPS) / 1000
            elif hat[1] == 0:
                if estado == "empieza_caminar":
                    estado = "parado"
                    for t in np.linspace(radians(90), 0, int(FPS * Periodo)):
                        pierna_der.angulos(Zancada * sin(t),
                                           Altura,
                                           p=Balanceo)
                        pierna_izq.angulos(Zancada * -sin(t),
                                           Altura,
                                           p=Balanceo * -2)
                        dt = clock.tick(FPS) / 1000
                    pierna_der.angulos(0, Altura)
                    pierna_izq.angulos(0, Altura)
                elif estado == "caminando_der":
                    estado = "parado"
                    for t in np.linspace(radians(90), 0, int(FPS * Periodo)):
                        pierna_der.angulos(-Zancada * sin(t),
                                           Altura,
                                           p=Balanceo * -2)
                        pierna_izq.angulos(Zancada * sin(t),
                                           Altura,
                                           p=Balanceo)
                        dt = clock.tick(FPS) / 1000
                    pierna_der.angulos(0, Altura)
                    pierna_izq.angulos(0, Altura)
                elif estado == "caminando_izq":
                    estado = "parado"
                    for t in np.linspace(radians(90), 0, int(FPS * Periodo)):
                        pierna_der.angulos(Zancada * sin(t),
                                           Altura,
                                           p=Balanceo)
                        pierna_izq.angulos(Zancada * -sin(t),
                                           Altura,
                                           p=Balanceo * -2)
                        dt = clock.tick(FPS) / 1000
                    pierna_der.angulos(0, Altura)
                    pierna_izq.angulos(0, Altura)

        # pierna_der.angulos(0, Altura)
        # pierna_izq.angulos(0, Altura)

        dt = clock.tick(FPS) / 1000
