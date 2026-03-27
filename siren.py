class Siren:
    def __init__(self, state, logger):
        self.state = state
        self.logger = logger

    def on(self, source="system"):
        if self.state.siren_muted:
            self.logger.log_event(
                "siren_on_blocked_muted",
                source=source,
                volume=self.state.siren_volume,
                muted=self.state.siren_muted,
            )
            return

        self.state.siren_active = True
        self.logger.log_event(
            "siren_on",
            source=source,
            volume=self.state.siren_volume,
            muted=self.state.siren_muted,
        )

    def off(self, source="system"):
        was_active = self.state.siren_active
        self.state.siren_active = False

        self.logger.log_event(
            "siren_off",
            source=source,
            was_active=was_active,
        )