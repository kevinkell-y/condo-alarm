import json
import os
from datetime import datetime, timedelta

from models import AlarmState

class StateManager:
    def __init__(self, default_state, entry_delay, exit_delay):
        self.state = AlarmState(default_state)
        self.entry_delay = entry_delay
        self.exit_delay = exit_delay

        self.entry_deadline = None
        self.pending_zone = None

        # Siren state
        self.siren_active = False
        self.siren_volume = "HIGH"   # LOW / MEDIUM / HIGH
        self.siren_muted = False

        # Sensor health state
        # zone_id -> ISO timestamp of most recent live message received
        self.sensor_health_path = "./logs/sensor_health.json"
        self.sensor_last_seen = self._load_sensor_health()

    def _load_sensor_health(self):
        if not os.path.exists(self.sensor_health_path):
            return {}

        try:
            with open(self.sensor_health_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_sensor_health(self):
        os.makedirs(os.path.dirname(self.sensor_health_path), exist_ok=True)

        with open(self.sensor_health_path, "w") as f:
            json.dump(self.sensor_last_seen, f, indent=2)

    def mark_sensor_seen(self, zone_id):
        self.sensor_last_seen[zone_id] = datetime.now().isoformat()
        self._save_sensor_health()

    def sensor_has_checked_in(self, zone_id):
        return zone_id in self.sensor_last_seen

    def all_sensors_ready(self, zones):
        return all(self.sensor_has_checked_in(zone_id) for zone_id in zones.keys())

    def missing_sensors(self, zones):
        return [
            zone_id
            for zone_id in zones.keys()
            if not self.sensor_has_checked_in(zone_id)
        ]

    def arm_home(self):
        self.state = AlarmState.ARMED_HOME

    def arm_away(self):
        self.state = AlarmState.ARMED_AWAY

    def disarm(self):
        self.state = AlarmState.DISARMED
        self.entry_deadline = None
        self.pending_zone = None
        self.siren_active = False

    def start_entry_delay(self, zone):
        self.state = AlarmState.ENTRY_DELAY
        self.pending_zone = zone
        self.entry_deadline = datetime.now() + timedelta(seconds=self.entry_delay)

    def trigger_alarm(self):
        self.state = AlarmState.ALARM_TRIGGERED

    def entry_expired(self):
        return self.entry_deadline and datetime.now() >= self.entry_deadline

    def entry_seconds_remaining(self):
        if not self.entry_deadline:
            return None

        remaining = (self.entry_deadline - datetime.now()).total_seconds()
        return max(0, int(remaining))

    def set_volume(self, level):
        self.siren_volume = level

    def mute(self):
        self.siren_muted = True

    def unmute(self):
        self.siren_muted = False

    def silence(self):
        self.siren_active = False
