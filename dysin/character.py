# -*- coding:utf-8 -*-
"""Character controller: wires up spirit, dialog, language, mood, media."""
from dysin.ui.spirit import Spirit
from dysin.ui.dialog import Dialog
from dysin.core.language import Language
from dysin.core.mood import Mood
from dysin.network.audio import SoundPlaying
from dysin.network.server import MessageServer
from dysin.core import setting


class Character:
    def __init__(self, timer, mainApplication):
        self.timer = timer; self.spirit = Spirit(self); self.dialog = Dialog(self)
        self.language = Language(self); self.mood = Mood()
        self.soundThread = SoundPlaying(); self.musicThread = None
        self.mainApplication = mainApplication; self.activate()
        if getattr(setting, 'MESSAGE_SERVER_ENABLED', True):
            port = getattr(setting, 'MESSAGE_SERVER_PORT', 7654)
            self.msgServer = MessageServer(port)
            self.msgServer.messageReceived.connect(self.onExternalMessage)
            self.msgServer.start()
        else:
            self.msgServer = None

    def onExternalMessage(self, message):
        if message and self.dialog:
            self.dialog.setExternalMessage(message)

    def activate(self):
        self.spirit.activateWindow(); self.spirit.raise_()
        self.dialog.activateWindow(); self.dialog.raise_()

    def exiting(self, h1=None, h2=None):
        self.mainApplication.save(); self.spirit.exitFlag = True
        if self.musicThread: self.musicThread.endPlay()
        self.dialog.funcBreakSpeak(); return 'exit'

    def isPlayingMusic(self):
        return bool(self.musicThread and self.musicThread.operation and
                    not (self.musicThread.pauseFlag or self.musicThread.stopFlag or
                         self.musicThread.swapFlag))
