from flask import Flask, redirect, render_template
from models import SensorEvent


def create_app(state, notifier, siren, engine, zones, logger):
    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.engine = engine
    app.zones = zones
    app.logger_store = logger

    @app.route("/")
    def home():
        recent_events = app.logger_store.recent(limit=10)
        return render_template(
            "index.html",
            state=state.state.value,
            siren_active=getattr(state, "siren_active", False),
            recent_events=recent_events,
        )

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