import json
from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, data):
        record = {
            "time": datetime.now().isoformat(),
            **data
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def recent(self, limit=10):
        if not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        events = []
        for line in lines[-limit:]:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)

                # Convert ISO time to readable format
                try:
                    dt = datetime.fromisoformat(event["time"])
                    event["time_display"] = dt.strftime("%B %d, %Y — %-I:%M:%S %p")
                except Exception:
                    event["time_display"] = event.get("time", "")

                events.append(event)

            except json.JSONDecodeError:
                continue

        return list(reversed(events))