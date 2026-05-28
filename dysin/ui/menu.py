# -*- coding:utf-8 -*-
"""Context menus: ActionMenu (right-click) and DialogMenu (reaction)."""
import os
from PySide6.QtGui import QAction, QIcon, QActionGroup
from PySide6.QtWidgets import QMenu
from dysin.core.config import IMAGE_DIR
from dysin.core import setting


class PlayerAction(QAction):
    def __init__(self, parent, character, name, label, function, nextMessage=None):
        super().__init__(label, parent)
        self.name = name; self.character = character; self.label = label
        self.function = function; self.nextMessage = nextMessage
        self.triggered.connect(self.react)

    def react(self):
        if self.character.language.showState() != self.name:
            t = self.function(self.character.mood, self.name)
            if not self.nextMessage: self.nextMessage = t
            if not self.nextMessage: self.nextMessage = self.name
            self.character.dialog.speak(self.nextMessage)
            self.character.dialog.funcBreakSpeak()
            self.character.activate()


class MediaAction(QActionGroup):
    def __init__(self, character, parent):
        super().__init__(parent); self.character = character
        self.pauseAction = PlayerAction(self, self.character, 'pauseMusic', '暂停播放', self.pauseMusic)
        self.unpauseAction = PlayerAction(self, self.character, 'unpauseMusic', '统续播放', self.unpauseMusic)
        self.stopAction = PlayerAction(self, self.character, 'stopMusic', '停止播放', self.stopMusic)
        iconPath = str(IMAGE_DIR / 'pause.png')
        if os.path.exists(iconPath):
            self.pauseAction.setIcon(QIcon(iconPath))
            self.unpauseAction.setIcon(QIcon(str(IMAGE_DIR / 'unpause.png')))
            self.stopAction.setIcon(QIcon(str(IMAGE_DIR / 'stop.png')))
        self.addAction(self.pauseAction); self.addAction(self.unpauseAction); self.addAction(self.stopAction)
        self.setVisible(False)

    def pauseMusic(self, t1='', t2=''):
        if self.character.musicThread: self.character.musicThread.pause()

    def unpauseMusic(self, t1='', t2=''):
        if self.character.musicThread: self.character.musicThread.unpause()

    def stopMusic(self, t1='', t2=''):
        if self.character.musicThread: self.character.musicThread.endPlay()

    def setting(self):
        if self.character.musicThread:
            if self.character.musicThread.operation and not self.character.musicThread.stopFlag:
                self.setVisible(True)
                if self.character.musicThread.pauseFlag:
                    self.pauseAction.setVisible(False); self.unpauseAction.setVisible(True)
                else: self.pauseAction.setVisible(True); self.unpauseAction.setVisible(False)
            else: self.setVisible(False)
        else: self.setVisible(False)


class ActionMenu(QMenu):
    def __init__(self, character):
        super().__init__(); self.character = character
        self.addAction(PlayerAction(self, self.character, 'talk', '聊天', setting.ActionSetting))
        self.addAction(PlayerAction(self, self.character, 'touch', '触摸', setting.ActionSetting))
        self.movingAction = PlayerAction(self, self.character, 'disableMoving', '不要走动', setting.ActionSetting)
        self.musicMenu = MediaAction(self.character, self)
        self.addAction(self.movingAction); self.addSeparator()
        self.addActions(self.musicMenu.actions()); self.addSeparator()
        self.addAction(PlayerAction(self, self.character, 'exit', '离开', self.character.exiting))

    def posShow(self, pos):
        self.musicMenu.setting(); self.move(pos)
        if self.character.mood.stopMoving:
            self.movingAction.setText('自由行动'); self.movingAction.name = 'enableMoving'
        else: self.movingAction.setText('不要走动'); self.movingAction.name = 'disableMoving'
        self.show()


class DialogMenu(QMenu):
    def __init__(self, character, reactions):
        super().__init__()
        self.character = character
        self.unconscious = ''
        unconscious_data = reactions.get('unconscious')
        if unconscious_data:
            self.unconscious = unconscious_data.get('next', '')
            self.addAction(PlayerAction(self, self.character, 'unconscious',
                                        unconscious_data.get('label', ''),
                                        setting.ActionSetting, self.unconscious))
        for reaction in setting.reactionList:
            data = reactions.get(reaction)
            if data:
                self.addAction(PlayerAction(self, self.character, reaction,
                                            data.get('label', ''),
                                            setting.ActionSetting, data.get('next', '')))

    def posShow(self, pos): self.move(pos); self.show()
