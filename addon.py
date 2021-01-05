"""
Kodi addon for reporting screen saver and DPMS status to benqd

AGPL 3.0
https://github.com/jantman/kodi-benq-projector-control
"""
import xbmc
import xbmcaddon
import time

_addon_ = xbmcaddon.Addon()
LOGLEVEL = xbmc.LOGWARNING


class ScreenSaverWatcher(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        xbmc.log('ScreenSaverWatcher initialized', LOGLEVEL)

    def onScreensaverActivated(self):
        xbmc.log('ScreenSaverWatcher.onScreensaverActivated() called', LOGLEVEL)

    def onScreensaverDeactivated(self):
        xbmc.log('ScreenSaverWatcher.onScreensaverDeactivated() called', LOGLEVEL)

    def onDPMSActivated(self):
        xbmc.log('ScreenSaverWatcher.onDPMSActivated() called', LOGLEVEL)

    def onDPMSDeactivated(self):
        xbmc.log('ScreenSaverWatcher.onDPMSDeactivated() called', LOGLEVEL)


mon = xbmc.Monitor()
ScreenSaverWatcher()
while not mon.abortRequested():
        if mon.waitForAbort(10):
            break
        xbmc.log("Addon is exiting %s" % time.time(), level=xbmc.LOGNOTICE)
