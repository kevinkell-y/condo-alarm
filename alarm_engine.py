from models import AlarmState, SensorEvent


class AlarmEngine:
    def __init__(self, state, notifier, siren, logger, zones):
        self.state = state
        self.notifier = notifier
        self.siren = siren
        self.logger = logger
        self.zones = zones
        self._last_entry_beep_second = None

    def handle(self, event: SensorEvent):
        zone = self.zones[event.zone_id]
        current_state = self.state.state

        self.logger.log_event(
            "zone_triggered",
            zone_id=zone.id,
            zone=zone.label,
            source_topic=event.source_topic,
            event_type=event.event_type,
            state=current_state.value,
        )

        if current_state == AlarmState.DISARMED:
            self.logger.log_event(
                "ignored_trigger_disarmed",
                zone_id=zone.id,
                zone=zone.label,
                source_topic=event.source_topic,
                state=current_state.value,
            )
            return

        if current_state == AlarmState.ARMED_HOME:
            if zone.entry_delay_home:
                self.state.start_entry_delay(zone.label)
                self.notifier.send(f"ENTRY: {zone.label}")
                self.logger.log_event(
                    "entry_delay_started",
                    zone_id=zone.id,
                    zone=zone.label,
                    source_topic=event.source_topic,
                    mode=current_state.value,
                )
                return

            self.trigger(zone, source_topic=event.source_topic)
            return

        if current_state == AlarmState.ARMED_AWAY:
            if zone.entry_delay_away:
                self.state.start_entry_delay(zone.label)
                self.notifier.send(f"ENTRY: {zone.label}")
                self.logger.log_event(
                    "entry_delay_started",
                    zone_id=zone.id,
                    zone=zone.label,
                    source_topic=event.source_topic,
                    mode=current_state.value,
                )
                return

            self.trigger(zone, source_topic=event.source_topic)
            return

        if current_state == AlarmState.ENTRY_DELAY:
            self.logger.log_event(
                "ignored_trigger_during_entry_delay",
                zone_id=zone.id,
                zone=zone.label,
                source_topic=event.source_topic,
                state=current_state.value,
            )
            return

        if current_state == AlarmState.ALARM_TRIGGERED:
            self.logger.log_event(
                "ignored_trigger_alarm_already_active",
                zone_id=zone.id,
                zone=zone.label,
                source_topic=event.source_topic,
                state=current_state.value,
            )
            return

    def trigger(self, zone, source_topic="manual"):
        self.state.trigger_alarm()
        self.siren.on(source="alarm_engine")
        self.notifier.send(f"ALARM: {zone.label}")
        self.logger.log_event(
            "alarm_triggered",
            zone_id=zone.id,
            zone=zone.label,
            source_topic=source_topic,
            state=self.state.state.value,
        )

    def tick(self):
        if self.state.state == AlarmState.ENTRY_DELAY:
            seconds_remaining = self.state.entry_seconds_remaining()

            if seconds_remaining is not None:
                if seconds_remaining != self._last_entry_beep_second:
                    self._last_entry_beep_second = seconds_remaining

                    if seconds_remaining <= 10:
                        self.siren.entry_delay_fast_beep()
                    elif seconds_remaining % 2 == 0:
                        self.siren.entry_delay_beep()

            if self.state.entry_expired():
                pending_label = self.state.pending_zone

                pending_zone = None
                for zone in self.zones.values():
                    if zone.label == pending_label:
                        pending_zone = zone
                        break

                self.logger.log_event(
                    "entry_delay_expired",
                    zone=pending_label,
                    source_topic="timer",
                )

                if pending_zone is not None:
                    self.trigger(pending_zone, source_topic="timer")
                else:
                    self.state.trigger_alarm()
                    self.siren.on(source="entry_delay_timer")
                    self.notifier.send(f"ALARM: {pending_label}")
                    self.logger.log_event(
                        "alarm_triggered",
                        zone=pending_label,
                        source_topic="timer",
                        state=self.state.state.value,
                    )
        else:
            self._last_entry_beep_second = None