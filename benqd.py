#!/usr/bin/env python3
"""
BenQ RS-232 projector control daemon

Configuration is via environment variables:

FLASK_DEBUG - set to 'true' to enable Flask debugging
FLASK_PORT - defaults to 8080
PROJECTOR_DEVICE - defaults to '/dev/ttyUSB0'
SERIAL_BAUDRATE - defaults to 115200
OFF_DELAY - how many seconds after screensaver to turn off projector; default 300

The API is as follows:

GET / - return JSON including "power_on" boolean
POST / - POST JSON, including one of:
  {"power_on": true|false} - turn the projector on or off

AGPL 3.0
https://github.com/jantman/kodi-benq-projector-control
"""

import ctypes
import struct
import serial
import logging
import os
from threading import Timer

from flask import Flask, request, jsonify

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

app = Flask(__name__)
app.logger.propagate = True

OFF_DELAY = int(os.environ.get('OFF_DELAY', '600'))


class ProjectorCommunicator:

    def __init__(self):
        dev = os.environ.get('PROJECTOR_DEVICE', '/dev/ttyUSB0')
        baud = int(os.environ.get('SERIAL_BAUDRATE', '115200'))
        app.logger.info(
            'Opening serial connection to %s at %s', dev, baud
        )
        try:
            self.conn = serial.Serial(dev, baud, timeout=0.5)
        except Exception as ex:
            app.logger.exception(
                'Unable to open serial connection to %s at %s: %s',
                dev, baud, ex, exc_info=True
            )
            raise
        app.logger.info('ProjectorCommunicator initialized.')

    @property
    def is_on(self):
        result = self._send_command(b'\r*pow=?#\r').strip()
        if result == '*POW=ON#':
            return True
        if result == '*POW=OFF#':
            return False
        raise RuntimeError('ERROR: Unknown power query response: "%s"' % result)

    def turn_on(self):
        result = self._send_command(b'\r*pow=on#\r').strip()
        if result == '*POW=ON#':
            return True
        raise RuntimeError(
            'ERROR: Unexpected response to pow=on: "%s"' % result
        )

    def turn_off(self):
        result = self._send_command(b'\r*pow=off#\r').strip()
        if result == '*POW=OFF#':
            return True
        raise RuntimeError(
            'ERROR: Unexpected response to pow=off: "%s"' % result
        )

    def _send_command(self, cmd):
        # returns a STRING
        # We reset the input and output buffers first, in case the port
        # has gotten into a weird state where, for some reason, there is
        # data waiting.
        app.logger.debug('Resetting input and output buffers')
        self.conn.reset_input_buffer()
        self.conn.reset_output_buffer()
        app.logger.info('Send command: %s', cmd)
        self.conn.write(cmd)
        # first line should echo the command back
        buf = self.conn.readline()
        app.logger.info('Readline: %s', buf)
        # second line should be the response
        buf = self.conn.readline()
        app.logger.info('Readline: %s', buf)
        return buf.decode()


COMM = ProjectorCommunicator()


def uptime():
    libc = ctypes.CDLL('libc.so.6')
    buf = ctypes.create_string_buffer(4096)
    if libc.sysinfo(buf) != 0:
        print('failed')
        return -1
    uptime = struct.unpack_from('@l', buf.raw)[0]
    return uptime


def get_status():
    try:
        return {
            'power_on': COMM.is_on,
            'success': True,
            'message': ''
        }
    except Exception as ex:
        app.logger.exception(
            'Exception getting power state: %s', ex, exc_info=True
        )
        return {
            'power_on': None,
            'success': False,
            'message': 'Exception getting power state: %s' % ex
        }


def screensaver_timer_callback():
    app.logger.info('Got off timer callback')
    try:
        COMM.turn_off()
        app.logger.info('Projector turned off')
    except Exception as ex:
        app.logger.exception(
            'Exception turning off from timer: %s', ex, exc_info=True
        )


def get_timer():
    return Timer(OFF_DELAY, screensaver_timer_callback)


OFF_TIMER = get_timer()


@app.route('/screensaver', methods=['GET', 'POST'])
def handle_screensaver():
    global OFF_TIMER
    app.logger.info(
        'Got screensaver request with values: %s' % dict(request.form)
    )
    if request.method != 'POST':
        return jsonify({'timer_running': OFF_TIMER.is_alive()})
    data = request.get_json()
    app.logger.info(
        'Got /screensaver POST from %s: %s', request.remote_addr, data
    )
    if data.get('screensaver_on', False) is True:
        # screensaver was just turned on
        if not OFF_TIMER.is_alive():
            app.logger.info(
                'Start screensaver timer for %d seconds', OFF_DELAY
            )
            del OFF_TIMER
            OFF_TIMER = get_timer()
            OFF_TIMER.start()
            return jsonify({'message': 'timer started'}), 202
        else:
            app.logger.info(
                'Screensaver started, but timer already running'
            )
            return jsonify({'message': 'timer already running'}), 200
    # else the screensaver has been turned off
    app.logger.info('Stop screensaver timer')
    OFF_TIMER.cancel()
    return jsonify({'message': 'timer stopped'}), 200


@app.route('/', methods=['GET', 'POST'])
def handle():
    app.logger.info('Got request with values: %s' % dict(request.form))
    status = get_status()
    status['uptime'] = uptime()
    status['server'] = 'benqd.py from https://github.com/jantman/' \
                       'kodi-benq-projector-control'
    if not status['success']:
        return jsonify(status), 500
    if request.method != 'POST':
        return jsonify(status)
    # else POST request
    data = request.get_json()
    app.logger.info('Got POST from %s: %s', request.remote_addr, data)
    rcode = 200
    if data.get('power_on') is True and status['power_on'] is False:
        app.logger.info('Turning projector on')
        try:
            COMM.turn_on()
            status['power_on'] = True
            status['message'] = 'Projector powered on'
            rcode = 201
        except Exception as ex:
            status['success'] = False
            status['message'] = 'Exception turning on projector: %s' % ex
            rcode = 500
    elif data.get('power_on') is False and status['power_on'] is True:
        app.logger.info('Turning projector off')
        try:
            COMM.turn_off()
            status['power_on'] = False
            status['message'] = 'Projector powered off'
            rcode = 201
        except Exception as ex:
            status['success'] = False
            status['message'] = 'Exception turning off projector: %s' % ex
            rcode = 500
    else:
        app.logger.info('POST but no state change')
        status['message'] = 'Projector already in desired state.'
    return jsonify(status), rcode


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '') == 'true'
    app.run(
        host="0.0.0.0", port=int(os.environ.get('FLASK_PORT', '8080')),
        debug=debug
    )
