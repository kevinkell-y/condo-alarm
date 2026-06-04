import json
import paho.mqtt.client as mqtt

from models import SensorEvent

BROKER = "localhost"
PORT = 1883
TOPIC = "zigbee2mqtt/#"


def parse_zigbee_event(payload: str):
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None

    if "contact" in data:
        return "closed" if data["contact"] is True else "opened"

    if "occupancy" in data:
        return "motion" if data["occupancy"] is True else None

    return None


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[MQTT] Connected with result code {reason_code}")
    client.subscribe(TOPIC)
    print(f"[MQTT] Subscribed to {TOPIC}")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8")

    print(f"[MQTT] Message received -> {topic}: {payload}")

    parts = topic.split("/")
    if len(parts) < 2:
        return

    zone_id = parts[1]

    # Ignore Zigbee2MQTT bridge/system messages
    if zone_id == "bridge":
        return

    event_type = parse_zigbee_event(payload)

    if event_type is None:
        print(f"[MQTT] Ignored payload from {topic}")
        return

    state = userdata["state"]
    zones = userdata["zones"]

    if zone_id in zones:
        state.mark_sensor_seen(zone_id)

    event = SensorEvent(
        zone_id=zone_id,
        event_type=event_type,
        source_topic=topic,
    )

    userdata["engine"].handle(event)


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

    print("[MQTT] Starting loop...")
    client.loop_forever()


if __name__ == "__main__":
    print("Run this through app.py so the alarm engine is available.")
