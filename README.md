# kodi-benq-projector-control

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

Kodi addon and separate daemon to control and automatically shut off BenQ RS232 projectors

## Project Components

This project offers **two different approaches** for controlling BenQ projectors:

### 1. Original Python Daemon + Kodi Addon (Legacy)

* ``benqd``, a Python daemon that connects to a BenQ projector over RS-232 and allows querying and controlling its power (on/off) state via a very simple HTTP API. It also supports powering off the projector after a delay, if not cancelled.
* ``addon.py``, a [Kodi](https://kodi.tv/) Python script addon that hooks into Kodi's screensaver system and notifies the daemon of when the screensaver starts and stops.

### 2. ESPHome-based Control (Recommended)

* ``esp32-projector.yaml``, an ESPHome configuration for ESP32 that provides the same projector control functionality with better Home Assistant integration
* Direct integration with Home Assistant automations and dashboard controls
* More reliable hardware-based solution with WiFi connectivity
* See [ESPHome_Setup.md](ESPHome_Setup.md) for detailed setup instructions

## Which Approach to Choose?

**Choose ESPHome if:**
- You use Home Assistant for home automation
- You want a dedicated hardware solution
- You prefer modern IoT-based control
- You want better reliability and monitoring

**Choose Python Daemon if:**
- You only use Kodi without Home Assistant
- You want to run everything on the same device as Kodi
- You prefer software-only solutions

## Project Files

### ESPHome Files
- `esp32-projector.yaml` - Complete ESPHome configuration for ESP32
- `ESPHome_Setup.md` - Detailed setup and wiring instructions
- `secrets.yaml.example` - Template for WiFi and API credentials
- `test_setup.sh` - Automated testing script for validation
- `COMPARISON.md` - Detailed comparison between Python and ESPHome approaches

### Python Daemon Files (Legacy)
- `benqd.py` - Python daemon for projector control
- `benqd.service` - SystemD service file
- `addon.py` - Kodi addon for screensaver integration
- `addon.xml` - Kodi addon metadata

## Quick Start

### For ESPHome (Recommended)
1. Follow the [ESPHome_Setup.md](ESPHome_Setup.md) guide
2. Copy `secrets.yaml.example` to `secrets.yaml` and fill in your details
3. Flash the ESP32 with `esphome run esp32-projector.yaml`
4. Run `./test_setup.sh` to validate your setup

### For Python Daemon (Legacy)
1. ``cd`` to your kodi addon directory, i.e. ``~/.kodi/addons``
1. ``git clone https://github.com/jantman/kodi-benq-projector-control.git service.benq-projector-control``
1. ``ln -s /home/pi/.kodi/addons/service.benq-projector-control/benqd.service /etc/systemd/system/benqd.service``
1. ``systemctl reload-daemon && systemctl start benqd.service``
1. Restart kodi
