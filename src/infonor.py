import time
import pygame as pg
import numpy as np
from adafruit_servokit import ServoKit
import gpiozero
import readchar
import atexit
from IK import Pierna

pg.init()
# This dict can be left as-is, since pygame will generate a
# pygame.JOYDEVICEADDED event for every joystick connected
# at the start of the program.
joysticks = {}


def pygane_event_handle():
    global start_time
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
FPS = 60

kit = ServoKit(channels=16, address=0x40)

MIN_IMP = 500
MAX_IMP = 2500

for i in range(16):
    kit.servo[i].set_pulse_width_range(MIN_IMP, MAX_IMP)


def chau(kit: ServoKit):
    print("APAGANDO SERVOS...")
    pg.quit()
    # for i in range(16):
    #     kit.servo[i].angle = 90
    # time.sleep(0.5)
    # for i in range(16):
    #     kit.servo[i].angle = None


pierna_izq = Pierna(8, 6.4,
                    kit.servo[4], kit.servo[5], kit.servo[6], kit.servo[7], False, False, False, True)
pierna_der = Pierna(8, 6.4,
                    kit.servo[0], kit.servo[1], kit.servo[2], kit.servo[3], False, False, False, False)
atexit.register(chau, kit)


def caminar(pierna_izq, pierna_der, BALANCEO, ZANCADA, fase):
    pierna_izq.angulos(ZANCADA * np.cos(fase),
                       12 + np.sin(fase),
                       a=4,
                       p=(BALANCEO)*np.sin(fase) - 30*np.sin(fase/2)**10 - 4)
    pierna_der.angulos(-ZANCADA * np.cos(fase),
                       12 - np.sin(fase),
                       a=4,
                       p=-BALANCEO*np.sin(fase) - 30*np.cos(fase/2)**10)


while True:
    start_time = time.time()
    t = 0
    freq = 0.3  # 1.2
    BALANCEO = 17  # 0.2  # 0.105
    ZANCADA = 2.5  # 0.2  # 0.09
    # SENTADILLA = 0.4
    # RESORTE = 0.1

    # INCLINACION = 0.1
    dt = 0

    while True:
        fase = t*freq*2*np.pi
        # print(f"{t = }")
        # caminar(pierna_izq, pierna_der, BALANCEO, ZANCADA, fase)

        pygane_event_handle()
        for joystick in joysticks.values():
            # # Eje 0:1 joystick izquierdo
            # # Eje 2:3 joystick derecho
            kit.servo[8].angle = 90 + joystick.get_axis(1) * 80
            kit.servo[9].angle = 90 + joystick.get_axis(0) * 80
            # kit.servo[10].angle = 90 - joystick.get_axis(4) * 80
            # kit.servo[11].angle = 90 + joystick.get_axis(3) * 80
            # for i in range(joystick.get_numaxes()):
            #     axis = joystick.get_axis(i)
            #     print(f"Eje {i}: {axis:.2f}", end="\t")
            # print()
            hat = joystick.get_hat(0)
            if hat[1] > 0:
                for t in np.arange(0, 1/freq, 1/FPS):
                    fase = t*freq*2*np.pi
                    caminar(pierna_izq, pierna_der, BALANCEO, ZANCADA, fase)
                    dt = clock.tick(FPS) / 1000
            elif hat[1] < 0:
                for t in np.arange(0, 1/freq, 1/FPS):
                    fase = -t*freq*2*np.pi
                    caminar(pierna_izq, pierna_der, BALANCEO, ZANCADA, fase)
                    dt = clock.tick(FPS) / 1000
            elif hat[0] > 0:  # Giro hacia la derecha
                pierna_der.s4.angle = 85
                time.sleep(0.5)
                pierna_izq.angulos(-ZANCADA, 12)
                pierna_der.angulos(ZANCADA, 12)
                time.sleep(0.5)
                for t in np.arange(0.5/freq, 0, -1/FPS):
                    fase = -t*freq*2*np.pi
                    caminar(pierna_izq, pierna_der, BALANCEO, ZANCADA, fase)
                    dt = clock.tick(FPS) / 1000

            elif hat[0] < 0:  # Giro hacia la izquierda
                for t in np.arange(0, 0.5/freq, 1/FPS):
                    fase = t*freq*2*np.pi
                    caminar(pierna_izq, pierna_der, BALANCEO, ZANCADA, fase)
                    dt = clock.tick(FPS) / 1000
                pierna_izq.angulos(-ZANCADA, 12)
                pierna_der.angulos(ZANCADA, 12)
                time.sleep(0.5)
                caminar(pierna_izq, pierna_der, BALANCEO, ZANCADA, 0)
                time.sleep(0.5)

        dt = clock.tick(FPS) / 1000
        # char = readchar.readkey()
        # t += (1/40) * (char == readchar.key.RIGHT)
        # t -= (1/40) * (char == readchar.key.LEFT)
        # if char: print(t)
