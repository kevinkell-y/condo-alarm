import json
from datetime import datetime

class Logger:
    def __init__(self, path):
        self.path = path

    def log(self, data):
        record = {
            "time": datetime.now().isoformat(),
            **data
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")
