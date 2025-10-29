import gpiozero
button = gpiozero.Button(26, pull_up=True, bounce_time=0.01)
print("JUANBOT INICIALIZADO, ESPERANDO BOTON...")
print(button.wait_for_active(timeout=None))
