import os
import secrets
from functools import wraps

from flask import Flask, Response, redirect, render_template, request

from models import SensorEvent


def require_auth(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        username = os.environ.get("ALARM_USERNAME", "admin")
        password = os.environ.get("ALARM_PASSWORD")

        if not password:
            return "ALARM_PASSWORD is not set on server", 500

        auth = request.authorization

        if (
            auth
            and secrets.compare_digest(auth.username, username)
            and secrets.compare_digest(auth.password, password)
        ):
            return view_func(*args, **kwargs)

        return Response(
            "Authentication required",
            401,
            {"WWW-Authenticate": 'Basic realm="Condo Alarm"'},
        )

    return wrapped


def create_app(state, notifier, siren, engine, zones, logger, config_store):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.engine = engine
    app.zones = zones
    app.logger_store = logger
    app.config_store = config_store

    @app.route("/")
    @require_auth
    def home():
        recent_events = app.logger_store.recent(limit=10)
        all_sensors_ready = state.all_sensors_ready(app.zones)
        missing_sensors = state.missing_sensors(app.zones)
        open_sensors = state.open_sensors(app.zones)
        not_ready_sensors = state.not_ready_sensors(app.zones)

        return render_template(
            "index.html",
            state=state.state.value,
            siren_active=state.siren_active,
            state_volume=state.siren_volume,
            state_muted=state.siren_muted,
            recent_events=recent_events,
            zones=app.zones,
            all_sensors_ready=all_sensors_ready,
            missing_sensors=missing_sensors,
            sensor_seen_since_startup=state.sensor_last_seen,
            open_sensors=open_sensors,
            not_ready_sensors=not_ready_sensors,
            sensor_contact=state.sensor_contact,
        )

    @app.route("/arm-home")
    @require_auth
    def arm_home():
        if not state.all_sensors_ready(app.zones):
            logger.log_event(
                "arm_home_blocked_sensor_check",
                missing_sensors=",".join(state.missing_sensors(app.zones)),
                state=state.state.value,
                level="WARNING",
            )
            return redirect("/")

        state.arm_home()
        logger.log_event("arm_home", state=state.state.value)
        siren.arm_home_chirp()
        notifier.send("SYSTEM: Armed Home")
        return redirect("/")

    @app.route("/arm-away")
    @require_auth
    def arm_away():
        if not state.all_sensors_ready(app.zones):
            logger.log_event(
                "arm_away_blocked_sensor_check",
                missing_sensors=",".join(state.missing_sensors(app.zones)),
                state=state.state.value,
                level="WARNING",
            )
            return redirect("/")

        state.arm_away()
        logger.log_event("arm_away", state=state.state.value)
        siren.arm_home_chirp()
        notifier.send("SYSTEM: Armed Away")
        return redirect("/")

    @app.route("/disarm")
    @require_auth
    def disarm():
        state.disarm()
        logger.log_event("disarm", state=state.state.value)
        siren.off(source="web_disarm")
        siren.disarm_chirp()
        notifier.send("SYSTEM: Disarmed")
        return redirect("/")

    @app.route("/panic")
    @require_auth
    def panic():
        state.trigger_alarm()
        logger.log_event("panic", state=state.state.value)
        siren.on(source="web_panic")
        notifier.send("PANIC: Alarm manually triggered")
        return redirect("/")

    @app.route("/trigger/<zone_id>")
    @require_auth
    def trigger(zone_id):
        if zone_id not in app.zones:
            logger.log_event("invalid_zone_trigger", zone_id=zone_id, level="WARNING")
            return "Invalid zone", 404

        zone = app.zones[zone_id]

        # Test trigger also counts as a local software test, NOT a real sensor check.
        # So we intentionally do not call state.mark_sensor_seen(zone_id) here.
        event = SensorEvent(
            zone_id=zone.id,
            event_type="opened",
            source_topic=zone.topic,
        )

        app.engine.handle(event)
        return redirect("/")

    @app.route("/silence")
    @require_auth
    def silence():
        state.silence()
        logger.log_event("silence_siren", state=state.state.value)
        siren.off(source="web_silence")
        notifier.send("SYSTEM: Siren silenced")
        return redirect("/")

    @app.route("/mute")
    @require_auth
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
    @require_auth
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
    @require_auth
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
    @require_auth
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
