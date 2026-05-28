# -*- coding:utf-8 -*-
"""Debug window for mood inspection."""
from PySide6.QtWidgets import (QDialog, QTextEdit, QDialogButtonBox,
                                QVBoxLayout, QHBoxLayout)


class DebugWindow(QDialog):
    def __init__(self, character):
        super().__init__(); self.character = character; self.initUI()

    def initUI(self):
        self.setWindowTitle('Debug'); self.resize(600, 400)
        layout = QVBoxLayout()
        self.textEdit = QTextEdit(); self.textEdit.setReadOnly(True)
        layout.addWidget(self.textEdit)
        buttonLayout = QHBoxLayout()
        refreshBtn = QDialogButtonBox()
        refreshBtn.addButton('refresh', QDialogButtonBox.ActionRole)
        refreshBtn.addButton('close', QDialogButtonBox.RejectRole)
        refreshBtn.button(QDialogButtonBox.ActionRole).clicked.connect(self.refresh)
        refreshBtn.button(QDialogButtonBox.RejectRole).clicked.connect(self.close)
        buttonLayout.addWidget(refreshBtn)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        mood = self.character.mood
        text = f"Mood: f={mood.familiar} fr={mood.friendship}"
        self.textEdit.setPlainText(text)
