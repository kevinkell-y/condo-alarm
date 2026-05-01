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


def beep(duration=0.1, volume=0.2, frequency=1200):
    buzz_on(volume=volume, frequency=frequency)
    time.sleep(duration)
    buzz_off()


def chirp(volume=0.15):
    beep(duration=0.12, volume=volume, frequency=1200)


def double_chirp(volume=0.15):
    chirp(volume)
    time.sleep(0.12)
    chirp(volume)


def alarm_pulse(volume=0.6):
    beep(duration=0.18, volume=volume, frequency=1800)
    time.sleep(0.08)
    beep(duration=0.18, volume=volume, frequency=1400)
    time.sleep(0.08)