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
pause = False


def pygane_event_handle():
    global pause, start_time
    # Event processing step.
    # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
    for event in pg.event.get():
        if event.type == pg.JOYBUTTONDOWN:
            print("Joystick button pressed.")
            pause = not pause
            if pause == False:
                pause = True
            else:
                start_time = time.time()
                pause = False
            if event.button == 0:
                joystick = joysticks[event.instance_id]
                if joystick.rumble(0, 0.7, 500):
                    print(
                        f"Rumble effect played on joystick {event.instance_id}")

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

for i in range(16):
    kit.servo[i].set_pulse_width_range(MIN_IMP, MAX_IMP)


def chau(kit: ServoKit):
    print("APAGANDO SERVOS...")
    kit.servo[0].angle = 90
    kit.servo[4].angle = 90
    pg.quit()
    # for i in range(16):
    #     kit.servo[i].angle = 90
    # time.sleep(0.5)
    # for i in range(16):
    #     kit.servo[i].angle = None


pierna_izq = Pierna(8, 6.4,
                    kit.servo[3], kit.servo[2], kit.servo[1], kit.servo[0])
pierna_der = Pierna(8, 6.4,
                    kit.servo[7], kit.servo[6], kit.servo[5], kit.servo[4], False, False, False, False)
atexit.register(chau, kit)

while True:
    # kit.servo[3].angle = 80  # cadera izq
    # kit.servo[2].angle = 90  # rodilla izq
    # kit.servo[1].angle = 90  # tobillo izq
    # kit.servo[0].angle = 90  # pie izq

    # kit.servo[7].angle = 100  # cadera der
    # kit.servo[6].angle = 90  # rodilla der
    # kit.servo[5].angle = 90  # tobillo der
    # kit.servo[4].angle = 90  # pie der

    # kit.servo[13].angle = 90  # hombro izq
    # kit.servo[12].angle = 40  # brazo izq

    # kit.servo[14].angle = 90  # hombro der
    # kit.servo[11].angle = 180-40  # brazo der

    # servos = [
    #     kit.servo[3],  # cadera izq  (0)
    #     kit.servo[2],  # rodilla izq (1)
    #     kit.servo[1],  # tobillo izq (2)
    #     kit.servo[0],  # pie izq     (3)

    #     kit.servo[7],  # cadera der  (4)
    #     kit.servo[6],  # rodilla der (5)
    #     kit.servo[5],  # tobillo der (6)
    #     kit.servo[4],  # pie der     (7)

    #     kit.servo[13],  # hombro izq (8)
    #     kit.servo[12],  # brazo izq  (9)

    #     kit.servo[14],  # hombro der (10)
    #     kit.servo[11],  # brazo der  (11)
    # ]

    # Y = np.zeros(shape=len(servos))
    start_time = time.time()
    t = 0
    freq = 0.3  # 1.2
    BALANCEO = 17  # 0.2  # 0.105
    ZANCADA = 4  # 0.2  # 0.09
    # SENTADILLA = 0.4
    # RESORTE = 0.1

    # INCLINACION = 0.1
    dt = 0

    while True:
        if not pause:
            t = time.time() - start_time
        fase = t*freq*2*np.pi
        # print(f"{t = }")

        # pierna_izq.angulos(ZANCADA * np.cos(fase),
        #                    12 + np.sin(fase),
        #                    a=8,
        #                    p=(BALANCEO*1.3)*np.sin(fase) - 30*np.sin(fase/2)**10)
        # pierna_der.angulos(-ZANCADA * np.cos(fase),
        #                    12 - np.sin(fase),
        #                    a=8,
        #                    p=-BALANCEO*np.sin(fase) - 30*np.cos(fase/2)**10)

        pygane_event_handle()
        for joystick in joysticks.values():
            # Eje 0:1 joystick izquierdo
            # Eje 2:3 joystick derecho
            kit.servo[8].angle = 90 + joystick.get_axis(1) * 80
            kit.servo[9].angle = 90 + joystick.get_axis(0) * 80
            kit.servo[10].angle = 90 - joystick.get_axis(4) * 80
            kit.servo[11].angle = 90 + joystick.get_axis(3) * 80
            for i in range(joystick.get_numaxes()):
                axis = joystick.get_axis(i)
                print(f"Eje {i}: {axis:.2f}", end="\t")
            print()
        dt = clock.tick(60) / 1000
        # char = readchar.readkey()
        # t += (1/40) * (char == readchar.key.RIGHT)
        # t -= (1/40) * (char == readchar.key.LEFT)
        # if char: print(t)
        # Y[:] = 0

        # Cálculos...
        # fase = t*freq*2*np.pi
        # kit.servo[0].angle = 90+20
        # kit.servo[4].angle = 90+16
        # for x in np.linspace(0, -2, 50):
        #     pierna_izq.angulos(-2, 13)
        #     pierna_der.angulos(-2, 13+x)
        #     clock.tick(50)
        # for x in np.linspace(0, ZANCADA, 50):
        #     pierna_izq.angulos(-2, 13)
        #     pierna_der.angulos(-2+x, 11)
        #     clock.tick(50)
        # for x in np.linspace(0, 2, 50):
        #     pierna_izq.angulos(-2, 13)
        #     pierna_der.angulos(-2+ZANCADA, 11+x)
        #     clock.tick(50)
        # kit.servo[0].angle = 90
        # kit.servo[4].angle = 90
        # for x in np.linspace(0, -ZANCADA, 50):
        #     pierna_izq.angulos(-2, 13)
        #     pierna_der.angulos(-2+ZANCADA+x, 13)
        #     clock.tick(50)

        # kit.servo[0].angle = 90-20
        # kit.servo[4].angle = 90-16
        # for x in np.linspace(0, -2, 50):
        #     pierna_der.angulos(-2, 13)
        #     pierna_izq.angulos(-2, 13+x)
        #     clock.tick(50)
        # for x in np.linspace(0, ZANCADA, 50):
        #     pierna_der.angulos(-2, 13)
        #     pierna_izq.angulos(-2+x, 11)
        #     clock.tick(50)
        # for x in np.linspace(0, 2, 50):
        #     pierna_der.angulos(-2, 13)
        #     pierna_izq.angulos(-2+ZANCADA, 11+x)
        #     clock.tick(50)
        # kit.servo[0].angle = 90
        # kit.servo[4].angle = 90
        # for x in np.linspace(0, -ZANCADA, 50):
        #     pierna_der.angulos(-2, 13)
        #     pierna_izq.angulos(-2+ZANCADA+x, 13)
        #     clock.tick(50)
