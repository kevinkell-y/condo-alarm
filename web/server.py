from flask import Flask, redirect, render_template
from models import SensorEvent


def create_app(state, notifier, siren, engine, zones, logger, config_store):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.engine = engine
    app.zones = zones
    app.logger_store = logger
    app.config_store = config_store

    @app.route("/")
    def home():
        recent_events = app.logger_store.recent(limit=10)
        return render_template(
            "index.html",
            state=state.state.value,
            siren_active=state.siren_active,
            state_volume=state.siren_volume,
            state_muted=state.siren_muted,
            recent_events=recent_events,
            zones=app.zones,
        )

    @app.route("/arm-home")
    def arm_home():
        state.arm_home()
        logger.log_event("arm_home", state=state.state.value)
        siren.arm_home_chirp()
        notifier.send("SYSTEM: Armed Home")
        return redirect("/")

    @app.route("/arm-away")
    def arm_away():
        state.arm_away()
        logger.log_event("arm_away", state=state.state.value)
        siren.arm_home_chirp()
        notifier.send("SYSTEM: Armed Away")
        return redirect("/")

    @app.route("/disarm")
    def disarm():
        state.disarm()
        logger.log_event("disarm", state=state.state.value)
        siren.off(source="web_disarm")
        siren.disarm_chirp()
        notifier.send("SYSTEM: Disarmed")
        return redirect("/")

    @app.route("/panic")
    def panic():
        state.trigger_alarm()
        logger.log_event("panic", state=state.state.value)
        siren.on(source="web_panic")
        notifier.send("PANIC: Alarm manually triggered")
        return redirect("/")

    @app.route("/trigger/<zone_id>")
    def trigger(zone_id):
        if zone_id not in app.zones:
            logger.log_event("invalid_zone_trigger", zone_id=zone_id, level="WARNING")
            return "Invalid zone", 404

        zone = app.zones[zone_id]

        event = SensorEvent(
            zone_id=zone.id,
            event_type="opened",
            source_topic=zone.topic,
        )

        app.engine.handle(event)
        return redirect("/")

    @app.route("/silence")
    def silence():
        state.silence()
        logger.log_event("silence_siren", state=state.state.value)
        siren.off(source="web_silence")
        notifier.send("SYSTEM: Siren silenced")
        return redirect("/")

    @app.route("/mute")
    def mute():
        state.mute()
        app.config_store.update_siren_settings(muted=state.siren_muted)
        logger.log_event(
            "mute",
            muted=state.siren_muted,
            volume=state.siren_volume,
        )
        notifier.send("SYSTEM: Siren muted")
        return redirect("/")

    @app.route("/unmute")
    def unmute():
        state.unmute()
        app.config_store.update_siren_settings(muted=state.siren_muted)
        logger.log_event(
            "unmute",
            muted=state.siren_muted,
            volume=state.siren_volume,
        )
        notifier.send("SYSTEM: Siren unmuted")
        return redirect("/")

    @app.route("/volume/<level>")
    def volume(level):
        level = level.upper()

        if level in ["LOW", "MEDIUM", "HIGH"]:
            state.set_volume(level)
            app.config_store.update_siren_settings(volume=state.siren_volume)
            logger.log_event(
                "volume_changed",
                volume=state.siren_volume,
                muted=state.siren_muted,
            )
            notifier.send(f"SYSTEM: Volume set to {level}")
        else:
            logger.log_event("invalid_volume", requested_level=level, level="WARNING")

        return redirect("/")

    @app.route("/test-buzzer")
    def test_buzzer():
        from buzzer import chirp

        chirp(volume=0.15)
        logger.log_event(
            "test_buzzer",
            volume=state.siren_volume,
            muted=state.siren_muted,
        )
        return redirect("/")

    return app