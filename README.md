# kodi-benq-projector-control

Kodi addon and separate daemon to control and automatically shut off BenQ RS232 projectors

This project is made up of two distinct pieces:

* ``benqd``, a Python daemon that connects to a BenQ projector over RS-232 and allows querying and controlling its power (on/off) state via a very simple HTTP API. It also supports powering off the projector after a delay, if not cancelled.
* ``addon.py``, a [Kodi](https://kodi.tv/) Python script addon that hooks into Kodi's screensaver system and notifies the daemon of when the screensaver starts and stops.

*Note about power-off timer:* As far as I can tell, aside from spawning a thread, there's no clear way to have a Kodi addon perform an action in N seconds/minutes without blocking. As a result, this solution just uses the Kodi addon to notify the daemon about screensaver status changes and the daemon handles the delayed turn-off functionality.

## Installation

1. ``cd`` to your kodi addon directory, i.e. ``~/.kodi/addons``
2. ``git clone https://github.com/jantman/kodi-benq-projector-control.git service.benq-projector-control``
3. Restart kodi
