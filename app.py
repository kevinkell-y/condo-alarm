import yaml
import time
import threading

from state import StateManager
from logger import Logger
from notifier import Notifier
from siren import Siren
from zones import load_zones
from alarm_engine import AlarmEngine
from web.server import create_app

cfg = yaml.safe_load(open("config.yaml"))

state = StateManager(
    cfg["states"]["default_mode"],
    cfg["states"]["entry_delay_seconds"],
    cfg["states"]["exit_delay_seconds"]
)

logger = Logger(cfg["logging"]["file"])
notifier = Notifier()
siren = Siren(state)
zones = load_zones(cfg)

engine = AlarmEngine(state, notifier, siren, logger, zones)

def loop():
    while True:
        engine.tick()
        time.sleep(1)

threading.Thread(target=loop, daemon=True).start()

app = create_app(state, notifier, siren, engine, zones, logger)

app.run(host="0.0.0.0", port=5000)
