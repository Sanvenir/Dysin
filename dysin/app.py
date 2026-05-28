# -*- coding:utf-8 -*-
"""Main Application entry point."""
import sys, pickle
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialog
from dysin.core.config import SAV_DIR
from dysin.character import Character
from dysin.ui.tray import SystemTrayIcon
from dysin.ui.first_run import FirstDialog
from dysin.core import setting


class MainApplication:
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)
        self.timer = QTimer()
        self.timer.start(16)
        self.character = Character(self.timer, self)
        self.debugWindow = None
        self.trayIcon = SystemTrayIcon(self.character)
        self.trayIcon.setVisible(True)
        SAV_DIR.mkdir(exist_ok=True)
        savFile = SAV_DIR / 'sav.dat'
        hasSave = False
        if savFile.exists():
            try:
                with open(savFile, 'rb') as f:
                    data = pickle.load(f)
                if data.get('name'):
                    self.loadData(data)
                    hasSave = True
            except: pass
        if not hasSave:
            self.firstDialog = FirstDialog(self)
            if self.firstDialog.exec() != QDialog.Accepted:
                sys.exit(0)
        self.timer.timeout.connect(self.character.spirit.update)
        self.character.dialog.show()
        self.character.spirit.show()

    def load(self):
        SAV_DIR.mkdir(exist_ok=True)
        savFile = SAV_DIR / 'sav.dat'
        if savFile.exists():
            try:
                with open(savFile, 'rb') as f:
                    data = pickle.load(f)
                self.loadData(data)
            except: pass

    def loadData(self, data):
        if 'mood' in data:
            mood_data = data['mood']
            for key in dir(self.character.mood):
                if not key.startswith('_') and key in mood_data:
                    setattr(self.character.mood, key, mood_data[key])
        if 'variable' in data:
            for key, value in data['variable'].items():
                if key in setting.variable: setting.variable[key] = value
        if 'name' in data: setting.text_calling = data['name']

    def save(self):
        SAV_DIR.mkdir(exist_ok=True)
        savFile = SAV_DIR / 'sav.dat'
        data = {
            'mood': {
                'familiar': self.character.mood.familiar,
                'friendship': self.character.mood.friendship,
                'love': self.character.mood.love,
                'fear': self.character.mood.fear,
                'hate': self.character.mood.hate,
                'happy': self.character.mood.happy,
                'angry': self.character.mood.angry,
                'sorrow': self.character.mood.sorrow,
                'horror': self.character.mood.horror,
                'surprised': self.character.mood.surprised,
                'shyness': self.character.mood.shyness,
                'relation': self.character.mood.relation,
                'emotion': self.character.mood.emotion,
                'tired': self.character.mood.tired,
                'interest': self.character.mood.interest,
                'stopMoving': self.character.mood.stopMoving,
            },
            'variable': setting.variable.copy(),
            'name': setting.text_calling,
        }
        try:
            with open(savFile, 'wb') as f: pickle.dump(data, f)
        except: pass

    def saveName(self, name):
        setting.text_calling = name
        self.save()

    def run(self):
        return self.app.exec()


def main():
    """Main entry point for the desktop spirit application."""
    app = MainApplication()
    return app.run()
