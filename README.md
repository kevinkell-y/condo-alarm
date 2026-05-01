# 🛡️ Condo Alarm System

> A self-owned, open-source home/condo/apartment security system built on Raspberry Pi, MQTT, and Zigbee.

---

## ⚡ What This Is

This project is a **fully self-hosted alarm system**.

No subscriptions.
No cloud dependency.
No third-party control/surveillance over your home.

It runs on a **Raspberry Pi**, listens to **Zigbee sensors**, processes events through **MQTT**, and exposes a simple **web interface** for control, all written on open source software.

It is designed to be:

* Minimal
* Transparent
* Hackable
* Reliable

---

## 🧠 Why This Exists

Most consumer alarm systems are:

* Cloud-dependent
* Subscription-locked
* Data-collecting
* Opaque

This system exists because:

> **You should own your own security system.**

Not rent it.
Not depend on it.
Not ask permission to use it.

---

## 🧭 Philosophy

Owning your own system is both a **right** and a **responsibility**.

### Your Right

* To control your own hardware
* To see and understand your own code
* To operate without surveillance or subscription
* To build systems that work even when the internet doesn’t

### Your Responsibility

* To build thoughtfully
* To test thoroughly
* To understand failure modes
* To maintain what you own

> This is not a plug-and-play toy.
> This is **mechanical literacy for your home.**

---

## 🏗️ System Overview

```
Zigbee Sensors → Zigbee2MQTT → MQTT Broker → Python App → Web UI + Siren
```

### Components

* Raspberry Pi (Zero 2 W)
* Zigbee USB Dongle
* Zigbee Door / Motion Sensors
* Mosquitto (MQTT Broker)
* Python Backend
* GPIO-controlled Buzzer / Siren
* Flask Web Interface

---

## 📁 Project Structure

```
condo-alarm/
├── app.py             # Main application (Flask + MQTT loop)
├── mqtt_client.py     # MQTT subscription + event handling
├── alarm_engine.py    # Core alarm logic
├── buzzer.py          # GPIO buzzer control
├── siren.py           # Siren patterns / modes
├── notifier.py        # Notifications (future)
├── logger.py          # Event logging
├── config.yaml        # System configuration
├── zones.py           # Zone definitions
├── web/               # Frontend UI
├── logs/              # Event logs
└── venv/              # Python virtual environment
```

---

## 🚀 Getting Started

### 1. SSH into your Raspberry Pi

```bash
ssh pi@condo-hub.local
```

### 2. Navigate to the project

```bash
cd ~/condo-alarm
```

### 3. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the app

```bash
python app.py
```

If needed:

```bash
GPIOZERO_PIN_FACTORY=lgpio python app.py
```

### 6. Open the web interface

Open in browser:

```
http://condo-hub.local:5000
```

---

## 🔌 Hardware Setup

### Buzzer (GPIO)

* Connected to GPIO pin **18**
* Controlled via `gpiozero.PWMOutputDevice`

Behavior:

* Chirp → system feedback
* Sustained tone → alarm trigger

---

### Zigbee Sensors

Paired through:

* Zigbee2MQTT

Example topics:

```
zigbee2mqtt/front_door
zigbee2mqtt/sliding_door
```

Mapped in:

```
config.yaml
```

---

## ⚙️ Configuration

Edit:

```yaml
config.yaml
```

Example:

```yaml
zones:
  - id: front_door
    topic: zigbee2mqtt/front_door
    entry_delay: true

siren:
  mode: mock

web:
  host: 0.0.0.0
  port: 5000
```

---

## 📡 MQTT Testing

Subscribe:

```bash
mosquitto_sub -t "#"
```

Publish test event:

```bash
mosquitto_pub -t zigbee2mqtt/front_door -m '{"contact": false}'
```

---

## 🔄 Autostart (systemd)

Create service:

```bash
sudo nano /etc/systemd/system/condo-alarm.service
```

Then enable:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable condo-alarm
sudo systemctl start condo-alarm
```

---

## 🧪 Development Workflow

* Use VSCode Remote SSH
* Edit files directly on Pi
* Save → immediate effect
* Monitor logs in terminal
* Iterate quickly

---

## 🔒 Security Notes

* Runs locally only
* No external API dependency
* Full control over network exposure

Recommended:

* Keep Pi on private network
* Use SSH keys instead of password
* Do NOT expose port 5000 publicly

---

## 🛠️ Roadmap

* [ ] Real siren patterns (multi-tone, escalating)
* [ ] Phone notifications (push/SMS)
* [ ] Battery backup support
* [ ] Device onboarding flow
* [ ] Production server (Gunicorn + systemd)
* [ ] Hardware enclosure + productization

---

## 🧩 Design Philosophy

This is not just software.

It is:

* Electronics
* Networking
* Embedded systems
* Human interface design

> You are building a system that protects physical space.

---

## 🧱 Final Thought

Most people outsource responsibility for their safety.

This project does the opposite.

---

## 📜 License

Open-source. Use it. Break it. Improve it.

---

## 🤝 Contributing

If you understand it well enough to improve it, you’re already qualified to contribute.

---

## 🐺 Built With Intent

Designed and built with:

* curiosity
* independence
* and a refusal to outsource ownership
