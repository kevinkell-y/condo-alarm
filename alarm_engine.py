from models import AlarmState, SensorEvent


class AlarmEngine:
    def __init__(self, state, notifier, siren, logger, zones):
        self.state = state
        self.notifier = notifier
        self.siren = siren
        self.logger = logger
        self.zones = zones

    def handle(self, event: SensorEvent):
        zone = self.zones[event.zone_id]
        current_state = self.state.state

        if current_state == AlarmState.DISARMED:
            self.logger.log({
                "event": "ignored_trigger_disarmed",
                "zone": zone.label,
                "source_topic": event.source_topic,
            })
            return

        if current_state == AlarmState.ARMED_HOME:
            if zone.entry_delay_home:
                self.state.start_entry_delay(zone.label)
                self.notifier.send(f"ENTRY: {zone.label}")
                self.logger.log({
                    "event": "entry_delay_started",
                    "zone": zone.label,
                    "source_topic": event.source_topic,
                    "mode": "ARMED_HOME",
                })
                return
            self.trigger(zone.label, event.source_topic)
            return

        if current_state == AlarmState.ARMED_AWAY:
            if zone.entry_delay_away:
                self.state.start_entry_delay(zone.label)
                self.notifier.send(f"ENTRY: {zone.label}")
                self.logger.log({
                    "event": "entry_delay_started",
                    "zone": zone.label,
                    "source_topic": event.source_topic,
                    "mode": "ARMED_AWAY",
                })
                return
            self.trigger(zone.label, event.source_topic)
            return

        if current_state == AlarmState.ENTRY_DELAY:
            return

        if current_state == AlarmState.ALARM_TRIGGERED:
            return

    def trigger(self, label, source_topic="manual"):
        self.state.trigger_alarm()
        self.siren.on()
        self.notifier.send(f"ALARM: {label}")
        self.logger.log({
            "event": "alarm",
            "zone": label,
            "source_topic": source_topic,
        })

    def tick(self):
        if self.state.state == AlarmState.ENTRY_DELAY and self.state.entry_expired():
            self.trigger(self.state.pending_zone, "timer")