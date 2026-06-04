import yaml
import time
import threading

from config_store import ConfigStore
from state import StateManager
from logger import Logger
from notifier import Notifier
from siren import Siren
from zones import load_zones
from alarm_engine import AlarmEngine
from web.server import create_app
from mqtt_client import start_mqtt

config_store = ConfigStore("config.yaml")
cfg = config_store.load()

state = StateManager(
    cfg["states"]["default_mode"],
    cfg["states"]["entry_delay_seconds"],
    cfg["states"]["exit_delay_seconds"]
)

# Apply persisted siren settings
siren_cfg = cfg.get("siren_settings", {})

state.set_volume(siren_cfg.get("default_volume", "HIGH"))

if siren_cfg.get("default_muted", False):
    state.mute()
else:
    state.unmute()

logger = Logger(
    event_path=cfg["logging"]["file"],
    app_log_path="./logs/condo_alarm.log"
)
notifier = Notifier(logger)
siren = Siren(state, logger)
zones = load_zones(cfg)

engine = AlarmEngine(state, notifier, siren, logger, zones)
threading.Thread(target=start_mqtt, args=(engine, state, zones), daemon=True).start()

def loop():
    while True:
        engine.tick()
        time.sleep(1)

threading.Thread(target=loop, daemon=True).start()

app = create_app(state, notifier, siren, engine, zones, logger, config_store)

app.run(host="0.0.0.0", port=5000)
