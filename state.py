from datetime import datetime, timedelta
from models import AlarmState

class StateManager:
    def __init__(self, default_state, entry_delay, exit_delay):
        self.state = AlarmState(default_state)
        self.entry_delay = entry_delay
        self.exit_delay = exit_delay
        self.entry_deadline = None
        self.pending_zone = None

    def arm_home(self):
        self.state = AlarmState.ARMED_HOME

    def arm_away(self):
        self.state = AlarmState.ARMED_AWAY

    def disarm(self):
        self.state = AlarmState.DISARMED
        self.entry_deadline = None
        self.pending_zone = None

    def start_entry_delay(self, zone):
        self.state = AlarmState.ENTRY_DELAY
        self.pending_zone = zone
        self.entry_deadline = datetime.now() + timedelta(seconds=self.entry_delay)

    def trigger_alarm(self):
        self.state = AlarmState.ALARM_TRIGGERED

    def entry_expired(self):
        return self.entry_deadline and datetime.now() >= self.entry_deadline
