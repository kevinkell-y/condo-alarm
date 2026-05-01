from gpiozero import PWMOutputDevice
import time

BUZZER_PIN = 18

buzzer = PWMOutputDevice(
    BUZZER_PIN,
    frequency=1200,
    initial_value=0,
)


def buzz_on(volume=0.15, frequency=1200):
    buzzer.frequency = frequency
    buzzer.value = volume


def buzz_off():
    buzzer.value = 0
    buzzer.off()


def chirp(volume=0.15):
    buzz_on(volume=volume, frequency=1200)
    time.sleep(0.15)
    buzz_off()


def alarm_pulse(volume=0.5):
    buzz_on(volume=volume, frequency=1800)
    time.sleep(0.25)
    buzz_off()
    time.sleep(0.15)