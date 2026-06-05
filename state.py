from datetime import datetime, timedelta
from models import AlarmState


class StateManager:
    def __init__(self, default_state, entry_delay, exit_delay):
        self.state = AlarmState(default_state)
        self.entry_delay = entry_delay
        self.exit_delay = exit_delay

        self.entry_deadline = None
        self.pending_zone = None

        self.siren_active = False
        self.siren_volume = "HIGH"
        self.siren_muted = False

        # Sensor state is session-only and intentionally NOT persisted.
        #
        # contact=True  means CLOSED
        # contact=False means OPEN
        # missing key      means UNKNOWN
        self.sensor_contact = {}
        self.sensor_last_seen = {}

    def mark_sensor_seen(self, zone_id, contact=None):
        self.sensor_last_seen[zone_id] = datetime.now().isoformat()

        if contact is not None:
            self.sensor_contact[zone_id] = contact

    def update_sensor_contact(self, zone_id, contact):
        self.sensor_last_seen[zone_id] = datetime.now().isoformat()
        self.sensor_contact[zone_id] = contact

    def sensor_has_checked_in(self, zone_id):
        return zone_id in self.sensor_last_seen

    def sensor_is_closed(self, zone_id):
        return self.sensor_contact.get(zone_id) is True

    def sensor_is_open(self, zone_id):
        return self.sensor_contact.get(zone_id) is False

    def sensor_is_unknown(self, zone_id):
        return zone_id not in self.sensor_contact

    def all_sensors_ready(self, zones):
        return all(
            self.sensor_is_closed(zone_id)
            for zone_id in zones.keys()
        )

    def missing_sensors(self, zones):
        return [
            zone_id
            for zone_id in zones.keys()
            if self.sensor_is_unknown(zone_id)
        ]

    def open_sensors(self, zones):
        return [
            zone_id
            for zone_id in zones.keys()
            if self.sensor_is_open(zone_id)
        ]

    def not_ready_sensors(self, zones):
        return [
            zone_id
            for zone_id in zones.keys()
            if not self.sensor_is_closed(zone_id)
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
        self.siren_active = True

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
