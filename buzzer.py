from gpiozero import PWMOutputDevice

buzzer = PWMOutputDevice(18, frequency=1200, initial_value=0)

def buzz_on(volume=0.15):
    buzzer.value = volume

def buzz_off():
    buzzer.value = 0

def chirp():
    buzzer.value = 0.15
    import time
    time.sleep(0.15)
    buzzer.value = 0
