class Notifier:
    def __init__(self, logger):
        self.logger = logger

    def send(self, msg):
        """
        User-facing notification event.
        This is NOT the same as system events like arm/disarm.
        """
        self.logger.log_event(
            "notify",
            message=msg,
        )