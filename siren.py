import threading
import time

from buzzer import buzz_off, chirp, double_chirp, beep, alarm_pulse


class Siren:
    def __init__(self, state, logger):
        self.state = state
        self.logger = logger
        self._thread = None
        self._stop_event = threading.Event()

    def _volume_value(self):
        volume = getattr(self.state, "siren_volume", "MEDIUM").upper()

        if volume == "LOW":
            return 0.08
        if volume == "HIGH":
            return 0.9

        return 0.35

    def _run_alarm_pattern(self):
        while not self._stop_event.is_set():
            if self.state.siren_muted or not self.state.siren_active:
                buzz_off()
                break

            alarm_pulse(volume=self._volume_value())

        buzz_off()

    def arm_home_chirp(self):
        double_chirp(volume=0.15)

    def disarm_chirp(self):
        chirp(volume=0.15)

    def entry_delay_beep(self):
        # One short warning beep. AlarmEngine can call this repeatedly.
        beep(duration=0.08, volume=0.18, frequency=1100)

    def entry_delay_fast_beep(self):
        beep(duration=0.06, volume=0.22, frequency=1500)

    def on(self, source="system"):
        if self.state.siren_muted:
            self.logger.log_event(
                "siren_on_blocked_muted",
                source=source,
                volume=self.state.siren_volume,
                muted=self.state.siren_muted,
            )
            buzz_off()
            return

        self.state.siren_active = True
        self._stop_event.clear()

        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run_alarm_pattern, daemon=True)
            self._thread.start()

        self.logger.log_event(
            "siren_on",
            source=source,
            volume=self.state.siren_volume,
            muted=self.state.siren_muted,
        )

    def off(self, source="system"):
        was_active = self.state.siren_active
        self.state.siren_active = False
        self._stop_event.set()
        buzz_off()

        self.logger.log_event(
            "siren_off",
            source=source,
            was_active=was_active,
        )