"""
Kodi addon for reporting screen saver and DPMS status to benqd

AGPL 3.0
https://github.com/jantman/kodi-benq-projector-control
"""

import xbmc
import xbmcaddon
import time
import requests

_addon_ = xbmcaddon.Addon()
LOGLEVEL = xbmc.LOGWARNING


class ScreenSaverWatcher(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        xbmc.log('ScreenSaverWatcher initialized', LOGLEVEL)

    def onScreensaverActivated(self):
        xbmc.log('ScreenSaverWatcher.onScreensaverActivated() called', LOGLEVEL)
        r = requests.post(
            'http://127.0.0.1/screensaver', json={'screensaver_on': True}
        )
        xbmc.log(
            'Screensaver post responded HTTP %s: %s', r.status_code, r.text
        )

    def onScreensaverDeactivated(self):
        xbmc.log('ScreenSaverWatcher.onScreensaverDeactivated() called', LOGLEVEL)
        r = requests.post(
            'http://127.0.0.1/screensaver', json={'screensaver_on': False}
        )
        xbmc.log(
            'Screensaver post responded HTTP %s: %s', r.status_code, r.text
        )


watcher = ScreenSaverWatcher()
while not watcher.abortRequested():
    if watcher.waitForAbort(10):
        xbmc.log("ScreenSaverWatcher is exiting at %s" % time.time(), level=xbmc.LOGNOTICE)
        break
