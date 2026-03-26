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
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        return list(reversed(events))