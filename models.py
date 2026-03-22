from dataclasses import dataclass
from enum import Enum

class AlarmState(str, Enum):
    DISARMED = "DISARMED"
    ARMED_HOME = "ARMED_HOME"
    ARMED_AWAY = "ARMED_AWAY"
    ENTRY_DELAY = "ENTRY_DELAY"
    ALARM_TRIGGERED = "ALARM_TRIGGERED"

@dataclass
class Zone:
    id: str
    label: str
    topic: str
    entry_delay_home: bool = False
    entry_delay_away: bool = False

@dataclass
class SensorEvent:
    zone_id: str
    event_type: str
    source_topic: str
