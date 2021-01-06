#!/usr/bin/env python3
"""
BenQ RS-232 projector control daemon

AGPL 3.0
https://github.com/jantman/kodi-benq-projector-control
"""

import ctypes
import stuct
import pyserial
import logging

from flask import Flask, request, jsonify

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

app = Flask(__name__)
app.logger.propagate = True


def uptime():
    libc = ctypes.CDLL('libc.so.6')
    buf = ctypes.create_string_buffer(4096)
    if libc.sysinfo(buf) != 0:
        print('failed')
        return -1
    uptime = struct.unpack_from('@l', buf.raw)[0]
    return uptime


def humantime(secs):
    if secs > 31536000:
        return '%s years' % round(secs / 31536000, 1)
    if secs > 2592000:
        return '%s months' % round(secs / 2592000, 1)
    if secs > 86400:
        return '%s days' % round(secs / 86400, 1)
    if secs > 3600:
        return '%s hours' % round(secs / 3600, 1)
    if secs > 60:
        return '%s minutes' % round(secs / 60, 1)
    return '%s seconds' % secs


def get_status():
    try:
        info = DISPLAY.dpms_info()
    except Exception as ex:
        app.logger.error('Exception getting dpms_info', exc_info=True)
        return {
            'success': False,
            'is_on': False,
            'state': 'unknown',
            'exception': str(ex)
        }
    state = 'unknown'
    is_on = False
    if info.power_level == dpms.DPMSModeOn:
        state = 'on'
        is_on = True
    elif info.power_level in [dpms.DPMSModeOff, dpms.DPMSModeStandby, dpms.DPMSModeSuspend]:
        state = 'off'
        is_on = False
    return {
        'success': True,
        'is_on': is_on,
        'state': state
    }


def ensure_timeouts():
    timeouts = DISPLAY.dpms_get_timeouts()
    app.logger.info('Current timeouts: %s', timeouts)
    DISPLAY.dpms_set_timeouts(
        DISPLAY_TIMEOUT_SEC, DISPLAY_TIMEOUT_SEC, DISPLAY_TIMEOUT_SEC
    )
    DISPLAY.sync()
    app.logger.info('Timeouts updated to: %s seconds', DISPLAY_TIMEOUT_SEC)


@app.route('/', methods=['GET', 'POST'])
def handle():
    app.logger.info('Got request with values: %s' % dict(request.form))
    if request.method == 'POST':
        data = request.get_json()
        app.logger.info('Got POST from %s: %s', request.remote_addr, data)
        status = get_status()
        if data.get('state') is True and status['is_on'] is False:
            app.logger.info('Turning on screen via DPMS')
            DISPLAY.dpms_force_level(dpms.DPMSModeOn)
            DISPLAY.sync()
        elif data.get('state') is False and status['is_on'] is True:
            app.logger.info('Turning off screen via DPMS')
            DISPLAY.dpms_force_level(dpms.DPMSModeOff)
            DISPLAY.sync()
        else:
            app.logger.info('POST but no state change')
    status = get_status()
    status['uptime'] = uptime()
    status['server'] = 'dpmsweb.py managed by privatepuppet::couchpi'
    return jsonify(status)


if __name__ == '__main__':
    debug = 'FLASK_DEBUG' in os.environ
    ensure_timeouts()
    app.run(
        host="0.0.0.0", port=int(os.environ.get('FLASK_PORT', '80')),
        debug=debug
    )
