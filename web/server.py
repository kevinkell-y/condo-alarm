from flask import Flask, redirect, render_template_string
from models import SensorEvent


def create_app(state, notifier, siren, engine, zones):
    app = Flask(__name__)

    app.engine = engine
    app.zones = zones

    HTML = """
    <!doctype html>
    <html>
    <head>
        <title>Condo Alarm</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 500px;
                margin: 40px auto;
                padding: 16px;
            }
            .card {
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 16px;
                margin-bottom: 20px;
            }
            h3 {
                margin-top: 24px;
            }
            .buttons a {
                display: block;
                text-decoration: none;
                margin: 10px 0;
                padding: 14px 16px;
                border-radius: 8px;
                background: #f3f3f3;
                color: #111;
                border: 1px solid #ccc;
            }
            .buttons a:hover {
                background: #e9e9e9;
            }
        </style>
    </head>
    <body>
        <h1>Condo Alarm</h1>

        <div class="card">
            <p><strong>State:</strong> {{ state }}</p>
        </div>

        <div class="buttons">
            <a href="/arm-home">Arm Home</a>
            <a href="/arm-away">Arm Away</a>
            <a href="/disarm">Disarm</a>
            <a href="/panic">Panic</a>
        </div>

        <h3>Test Triggers</h3>
        <div class="buttons">
            <a href="/trigger/front_door">Trigger Front Door</a>
            <a href="/trigger/sliding_door">Trigger Sliding Door</a>
            <a href="/trigger/kitchen_door">Trigger Kitchen Door</a>
            <a href="/trigger/bedroom_window">Trigger Bedroom Window</a>
            <a href="/trigger/studio_window">Trigger Studio Window</a>
        </div>
    </body>
    </html>
    """

    @app.route("/")
    def home():
        return render_template_string(HTML, state=state.state.value)

    @app.route("/arm-home")
    def arm_home():
        state.arm_home()
        notifier.send("SYSTEM: Armed Home")
        return redirect("/")

    @app.route("/arm-away")
    def arm_away():
        state.arm_away()
        notifier.send("SYSTEM: Armed Away")
        return redirect("/")

    @app.route("/disarm")
    def disarm():
        state.disarm()
        siren.off()
        notifier.send("SYSTEM: Disarmed")
        return redirect("/")

    @app.route("/panic")
    def panic():
        state.trigger_alarm()
        siren.on()
        notifier.send("PANIC: Alarm manually triggered")
        return redirect("/")

    @app.route("/trigger/<zone_id>")
    def trigger(zone_id):
        if zone_id not in app.zones:
            return "Invalid zone", 404

        zone = app.zones[zone_id]

        event = SensorEvent(
            zone_id=zone.id,
            event_type="opened",
            source_topic=zone.topic,
        )

        app.engine.handle(event)
        return redirect("/")

    return app