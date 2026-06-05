import json
import paho.mqtt.client as mqtt

from models import SensorEvent

BROKER = "localhost"
PORT = 1883
TOPICS = [
    "zigbee2mqtt/front_door",
    "zigbee2mqtt/sliding_door",
    "zigbee2mqtt/kitchen_door",
]


def parse_zigbee_payload(payload: str):
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None, None

    if "contact" in data:
        contact = data["contact"]
        event_type = "closed" if contact is True else "opened"
        return event_type, contact

    if "occupancy" in data:
        if data["occupancy"] is True:
            return "motion", None

    return None, None


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[MQTT] Connected with result code {reason_code}", flush=True)
    for topic in TOPICS:
        client.subscribe(topic)
        print(f"[MQTT] Subscribed to {topic}", flush=True)


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8")

    print(f"[MQTT] Message received -> {topic}: {payload}", flush=True)

    parts = topic.split("/")
    if len(parts) < 2:
        return

    if parts[0] != "zigbee2mqtt":
        return

    zone_id = parts[1]

    if zone_id == "bridge":
        return

    state = userdata["state"]
    zones = userdata["zones"]
    engine = userdata["engine"]

    if zone_id not in zones:
        return

    event_type, contact = parse_zigbee_payload(payload)

    if event_type is None:
        print(f"[MQTT] Ignored payload from {topic}", flush=True)
        return

    old_contact = state.sensor_contact.get(zone_id)

    if contact is not None:
        state.update_sensor_contact(zone_id, contact)

        print(
            f"[MQTT] {zone_id}: contact={contact} "
            f"old_contact={old_contact} alarm_state={state.state.value}",
            flush=True,
        )

        # CLOSED report updates readiness only. It does not trigger alarm.
        if contact is True:
            return

        # OPEN report only triggers if this is a real CLOSED -> OPEN transition.
        if old_contact is not True:
            print(
                f"[MQTT] Ignored OPEN for {zone_id}: "
                f"old_contact was {old_contact}, not True",
                flush=True,
            )
            return

    event = SensorEvent(
        zone_id=zone_id,
        event_type=event_type,
        source_topic=topic,
    )

    engine.handle(event)


def start_mqtt(engine, state, zones):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    client.user_data_set(
        {
            "engine": engine,
            "state": state,
            "zones": zones,
        }
    )

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)

    print("[MQTT] Starting loop...", flush=True)
    client.loop_forever()


if __name__ == "__main__":
    print("Run this through app.py so the alarm engine is available.")
