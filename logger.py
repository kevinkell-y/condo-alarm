import json
import logging
from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self, event_path, app_log_path=None):
        self.event_path = Path(event_path)
        self.event_path.parent.mkdir(parents=True, exist_ok=True)

        if app_log_path is None:
            self.app_log_path = self.event_path.parent / "condo_alarm.log"
        else:
            self.app_log_path = Path(app_log_path)

        self.app_log_path.parent.mkdir(parents=True, exist_ok=True)

        self._ops_logger = logging.getLogger("condo_alarm")
        self._ops_logger.setLevel(logging.INFO)
        self._ops_logger.propagate = False

        if not self._ops_logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            file_handler = logging.FileHandler(self.app_log_path, encoding="utf-8")
            file_handler.setFormatter(formatter)

            self._ops_logger.addHandler(console_handler)
            self._ops_logger.addHandler(file_handler)

    def log_event(self, event, level="INFO", **fields):
        timestamp = datetime.now().isoformat(timespec="seconds")

        record = {
            "time": timestamp,
            "event": event,
            **fields,
        }

        with self.event_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        message_parts = [f"event={event}"]
        for key, value in fields.items():
            message_parts.append(f"{key}={value}")

        message = " ".join(message_parts)
        log_method = getattr(self._ops_logger, level.lower(), self._ops_logger.info)
        log_method(message)

    def log(self, data):
        """
        Backward-compatible adapter so older calls like:
            logger.log({"event": "alarm", "zone": "Front Door"})
        still work.
        """
        data = dict(data)
        event = data.pop("event", "unknown_event")
        level = data.pop("level", "INFO")
        self.log_event(event, level=level, **data)

    def recent(self, limit=10):
        if not self.event_path.exists():
            return []

        with self.event_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        events = []
        for line in lines[-limit:]:
            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)

                try:
                    dt = datetime.fromisoformat(event["time"])
                    event["time_display"] = dt.strftime("%B %d, %Y — %-I:%M:%S %p")
                except Exception:
                    event["time_display"] = event.get("time", "")

                events.append(event)

            except json.JSONDecodeError:
                continue

        return list(reversed(events))