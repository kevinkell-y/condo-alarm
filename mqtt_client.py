import paho.mqtt.client as mqtt
from models import SensorEvent

BROKER = "localhost"
PORT = 1883
TOPIC = "condo/#"


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[MQTT] Connected with result code {reason_code}")
    client.subscribe(TOPIC)
    print(f"[MQTT] Subscribed to {TOPIC}")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"[MQTT] Message received -> {topic}: {payload}")

    # Extract zone_id from topic
    # Example: condo/front_door → front_door
    parts = topic.split("/")
    if len(parts) < 2:
        return

    zone_id = parts[1]

    event = SensorEvent(
        zone_id=zone_id,
        event_type=payload,
        source_topic=topic
    )

    # Call the alarm engine
    userdata["engine"].handle(event)


def start_mqtt(engine):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.user_data_set({"engine": engine})
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)

    print("[MQTT] Starting loop...")
    client.loop_forever()


if __name__ == "__main__":
    start_mqtt()
