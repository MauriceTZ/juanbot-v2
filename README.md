# juanbot v2
Segunda iteración del código para juanbot.

Funciona en una Raspberry Pi 3 con el sistema operativo Raspberry Pi OS.
## Instalación
Usando Python (ver. 3.11.2 funciona) cree un entorno virtual:
```sh
python -m venv .venv
```
Si instaló la versión especifica de Python de forma separada, entonces debería hacer:
```sh
python3.11 -m venv .venv
```
A continuación debe activar el entorno virtual con:
```sh
source .venv/bin/activate
```
Luego instale las dependencias del proyecto:
```sh
pip install -r requirements.txt
```
Ya puede ejecutar cualquiera de los tests encontrados en
```sh
ls src/tests/*.py
```
ó los programas principales ubicados en la carpeta `src`. Ejemplo:
```sh
python src/tests/test_joystick.py
```
```sh
python src/infonor.py
```