# -*- coding:utf-8 -*-
"""Sound and music playback threads."""
import time, threading
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class SoundPlaying(threading.Thread):
    def __init__(self):
        super().__init__(); self.daemon = True
        self.operation = True; self.playFlag = False; self.swapFlag = False
        self.currentSound = ''; self.player = None; self.start()

    def loadSound(self, filename):
        try:
            self.player = QMediaPlayer()
            self.audioOutput = QAudioOutput()
            self.player.setAudioOutput(self.audioOutput)
            self.player.setSource(filename); self.playFlag = True
        except: self.playFlag = False

    def run(self):
        while self.operation:
            if self.playFlag or (self.swapFlag and self.currentSound):
                self.swapFlag = False; self.playFlag = True
                self.loadSound(self.currentSound)
                if self.playFlag and self.player:
                    self.player.play()
                    while self.player.playbackState() == QMediaPlayer.PlayingState:
                        time.sleep(0.1)
                        if not self.playFlag: break
                    if self.player: self.player.stop()
                self.playFlag = False
            time.sleep(0.1)

    def swap(self, filename): self.swapFlag = True; self.currentSound = filename


class MusicPlaying(threading.Thread):
    def __init__(self, fileName):
        super().__init__(); self.daemon = True
        self.fileName = fileName; self.pauseFlag = False; self.stopFlag = False
        self.swapFlag = False; self.operation = True; self.nextMusic = None
        self.player = None; self.start()

    def playSound(self):
        try:
            self.player = QMediaPlayer()
            self.audioOutput = QAudioOutput()
            self.player.setAudioOutput(self.audioOutput)
            self.player.setSource(self.fileName); self.player.play()
            while self.operation and self.player.playbackState() == QMediaPlayer.PlayingState:
                if self.stopFlag: self.player.stop(); self.operation = False; break
                elif self.swapFlag: self.player.stop(); break
                time.sleep(0.1)
            if self.player: self.player.stop()
            if self.swapFlag: self.swapFlag = False; self.operation = True; self.fileName = self.nextMusic
        except: self.operation = False

    def pause(self):
        if self.player: self.player.pause()
        self.pauseFlag = True

    def unpause(self):
        if self.player: self.player.play()
        self.pauseFlag = False

    def run(self): self.playSound()

    def getTime(self):
        if self.player: return self.player.position() / 1000.0
        return 0

    def endPlay(self): self.stopFlag = True

    def swapMusic(self, name):
        self.nextMusic = name; self.swapFlag = True
        if self.player: self.player.play()
