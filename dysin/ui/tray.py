# -*- coding:utf-8 -*-
"""System tray icon with context menu."""
import os
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from dysin.core.config import IMAGE_DIR
from dysin.core import i18n


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, character, parent=None):
        super().__init__(parent); self.character = character
        iconPath = str(IMAGE_DIR / 'headicon.png')
        if os.path.exists(iconPath): self.setIcon(QIcon(iconPath))
        if hasattr(self.character.language, 'outerDefine'):
            outerDefine = self.character.language.outerDefine
            self.name = outerDefine.get('TRAY_NAME', 'Dysin')
            self.showMessage(str(self.name), str(outerDefine.get('WELCOMING_TEXT', 'Hello!')))
            self.setToolTip(str(outerDefine.get('TRAY_TOOL_TIPS', 'Dysin')))
        self.activated.connect(self.clickMessage)
        self.menu = QMenu()
        self.setContextMenu(self.menu)
        self.menu.addAction(i18n.tr("menu.talk", "聊天"), lambda: self._trigger_action('talk'))
        self.menu.addAction(i18n.tr("menu.touch", "触摸"), lambda: self._trigger_action('touch'))
        self.menu.addSeparator()
        self.menu.addAction(i18n.tr("menu.exit", "离开"), lambda: self._trigger_action('exit'))

    def _trigger_action(self, action_name):
        if action_name == 'exit':
            self.character.exiting()
        elif action_name in ('talk', 'touch'):
            self.character.spirit.standFlag = True
            self.character.activate()

    def clickMessage(self, message):
        if message == QSystemTrayIcon.Trigger:
            if hasattr(self.character.language, 'outerDefine'):
                self.showMessage(str(self.name),
                                 str(self.character.language.outerDefine.get('CLICK_TEXT', 'Click!')))
            self.character.activate()
