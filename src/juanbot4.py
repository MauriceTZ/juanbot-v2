import time
import threading
from math import sin, cos, radians
import pygame as pg
import numpy as np
from adafruit_servokit import ServoKit
import gpiozero
import readchar
import atexit
from IK import Pierna
from util import map_range, sin_ramp

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
Balanceo = 14  # grados
Altura = 10  # cm
Periodo = 1  # seg

Acel_Brazo = 90
Pot_Balanceo = 1

running = True

FPS = 30
dt = 0

brazo_der = [90, 0]
brazo_izq = [90, 0]

estado = "parado"

for i in range(16):
    kit.servo[i].set_pulse_width_range(MIN_IMP, MAX_IMP)


def chau(kit: ServoKit):
    global running
    running = False
    print("APAGANDO SERVOS...")
    pg.quit()


pierna_izq = Pierna(6.755, 6.361,
                    kit.servo[4], kit.servo[5], kit.servo[6], kit.servo[7], False, False, False, True,
                    o1=10, o3=0, o4=0, xoff=-2, yoff=0)
                    # o1=10, o3=5, o4=0, xoff=0, yoff=0)
pierna_der = Pierna(6.648, 6.268,
                    kit.servo[0], kit.servo[1], kit.servo[2], kit.servo[3], False, False, False, False,
                    o1=0, o3=0, o4=-10, xoff=-2, yoff=0)
                    # o1=10, o3=10, o4=-15, xoff=0, yoff=-0.41)

atexit.register(chau, kit)


def juan():
    global running, brazo_izq, brazo_der
    clock_local = pg.time.Clock()
    dt_local = 1 / FPS
    while running:
        for joystick in joysticks.values():
            axis1 = joystick.get_axis(0)
            axis2 = joystick.get_axis(1)
            axis3 = joystick.get_axis(3)
            axis4 = joystick.get_axis(4)

            brazo_izq[0] += axis1 * (abs(axis1) > 0.1) * dt_local * Acel_Brazo
            brazo_izq[1] += axis2 * (abs(axis2) > 0.1) * dt_local * Acel_Brazo
            brazo_der[0] += axis3 * (abs(axis3) > 0.1) * dt_local * Acel_Brazo
            brazo_der[1] += axis4 * (abs(axis4) > 0.1) * dt_local * Acel_Brazo

            brazo_der = np.clip(brazo_der, -90, 90)
            brazo_izq = np.clip(brazo_izq, -90, 90)

            kit.servo[9].angle = 90 + brazo_izq[1]
            kit.servo[8].angle = 90 + brazo_der[1]
            kit.servo[11].angle = 90 - brazo_izq[0]
            # dt_local = clock_local.tick(FPS) / 1000
            time.sleep(dt_local)


threading.Thread(target=juan).start()

# while True:
start_time = time.time()

pierna_der.angulos(0, Altura)
pierna_izq.angulos(0, Altura)
time.sleep(1)

while running:
    dt = clock.tick(FPS) / 1000
    pygane_event_handle()
    for joystick in joysticks.values():
        hat = joystick.get_hat(0)
        if hat[1] == 1:
            if estado == "parado":
                estado = "empieza_caminar"
                print(estado)
                for t in np.linspace(0, radians(180), int(FPS * Periodo)):
                    pierna_der.angulos(Zancada * sin(t/2),
                                       Altura,
                                       p=-sin_ramp(t, Pot_Balanceo) * Balanceo)
                    pierna_izq.angulos(Zancada * -sin(t/2),
                                       Altura,
                                       p=sin_ramp(t, Pot_Balanceo) * Balanceo)
                    dt = clock.tick(FPS) / 1000
            elif estado == "empieza_caminar" or estado == "caminando_izq":
                estado = "caminando_der"
                print(estado)
                for t, t2 in zip(np.linspace(radians(180), radians(360), int(FPS * Periodo)),
                                 np.linspace(radians(90), radians(270), int(FPS * Periodo))):
                    pierna_der.angulos(Zancada * sin(t2),
                                       Altura,
                                       p=-sin_ramp(t, Pot_Balanceo) * Balanceo)
                    pierna_izq.angulos(Zancada * -sin(t2),
                                       Altura,
                                       p=sin_ramp(t, Pot_Balanceo) * Balanceo)
                    dt = clock.tick(FPS) / 1000
            elif estado == "caminando_der":
                estado = "caminando_izq"
                print(estado)
                for t, t2 in zip(np.linspace(radians(360), radians(360+180), int(FPS * Periodo)),
                                 np.linspace(radians(270), radians(270+180), int(FPS * Periodo))):
                    pierna_der.angulos(Zancada * sin(t2),
                                       Altura,
                                       p=-sin_ramp(t, Pot_Balanceo) * Balanceo)
                    pierna_izq.angulos(Zancada * -sin(t2),
                                       Altura,
                                       p=sin_ramp(t, Pot_Balanceo) * Balanceo)
                    dt = clock.tick(FPS) / 1000
        elif hat[1] == 0:
            if estado == "empieza_caminar":
                estado = "parado"
                print(estado)
                for t in np.linspace(radians(180), radians(360), int(FPS * Periodo)):
                    pierna_der.angulos(Zancada * sin(t/2),
                                       Altura,
                                       p=-sin_ramp(t, Pot_Balanceo) * Balanceo)
                    pierna_izq.angulos(Zancada * -sin(t/2),
                                       Altura,
                                       p=sin_ramp(t, Pot_Balanceo) * Balanceo)
                    dt = clock.tick(FPS) / 1000
            elif estado == "caminando_der":
                estado = "parado"
                print(estado)
                for t in np.linspace(radians(360+180), radians(360), int(FPS * Periodo)):
                    pierna_der.angulos(Zancada * sin(t/2),
                                       Altura,
                                       p=-sin_ramp(t, Pot_Balanceo) * Balanceo)
                    pierna_izq.angulos(Zancada * -sin(t/2),
                                       Altura,
                                       p=sin_ramp(t, Pot_Balanceo) * Balanceo)
                    dt = clock.tick(FPS) / 1000
            elif estado == "caminando_izq":
                estado = "parado"
                print(estado)
                for t in np.linspace(radians(180), radians(360), int(FPS * Periodo)):
                    pierna_der.angulos(Zancada * sin(t/2),
                                       Altura,
                                       p=-sin_ramp(t, Pot_Balanceo) * Balanceo)
                    pierna_izq.angulos(Zancada * -sin(t/2),
                                       Altura,
                                       p=sin_ramp(t, Pot_Balanceo) * Balanceo)
                    dt = clock.tick(FPS) / 1000
