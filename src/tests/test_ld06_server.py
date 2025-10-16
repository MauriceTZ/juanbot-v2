import socket
import serial
import numpy as np

SOCKET_ADDRESS = ("0.0.0.0", 6969)
START_CHARACTER = bytes((0x54,))

ld06 = serial.Serial(port='/dev/ttyUSB0', baudrate=230400)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(SOCKET_ADDRESS)
s.listen(1)

print(f"Server creado en {socket.gethostname()} en el puerto {SOCKET_ADDRESS[1]}")

while True:
    print("Esperando conexión...")
    client, addr = s.accept()
    print(f"Se conectó {addr}")

    ld06.read_until(START_CHARACTER)
    ld06.reset_input_buffer()

    try:
        while True:
            data = ld06.read(512)
            client.send(data)
    except Exception as e:
        print(e)
