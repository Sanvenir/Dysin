# -*- coding:utf-8 -*-
"""First-run name input dialog."""
from PySide6.QtWidgets import (QDialog, QLabel, QTextEdit, QDialogButtonBox,
                                QVBoxLayout, QHBoxLayout)


class FirstDialog(QDialog):
    def __init__(self, mainApp):
        super().__init__(); self.mainApp = mainApp; self.initUI()

    def initUI(self):
        self.setWindowTitle('Dysin - \u521d\u6b21\u89c1\u9762')
        self.setMinimumWidth(350)
        self.setMinimumHeight(180)
        self.resize(380, 200)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        self.promptLabel = QLabel('\u521d\u6b21\u89c1\u9762\uff0c\u8bf7\u544a\u8bc9\u6211\u4f60\u7684\u540d\u5b57\uff1a')
        self.promptLabel.setWordWrap(True)
        layout.addWidget(self.promptLabel)
        self.nameEdit = QTextEdit()
        self.nameEdit.setMaximumHeight(60)
        self.nameEdit.setPlaceholderText('\u8f93\u5165\u4f60\u7684\u540d\u5b57...')
        layout.addWidget(self.nameEdit)
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        self.okButton = QDialogButtonBox()
        self.cancelButton = QDialogButtonBox()
        self.okButton.addButton(QDialogButtonBox.Ok)
        self.cancelButton.addButton(QDialogButtonBox.Cancel)
        self.okButton.button(QDialogButtonBox.Ok).setText('\u786e\u5b9a')
        self.cancelButton.button(QDialogButtonBox.Cancel).setText('\u53d6\u6d88')
        self.okButton.accepted.connect(self.handleAccept)
        self.cancelButton.rejected.connect(self.reject)
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        self.nameEdit.setFocus()

    def handleAccept(self):
        name = self.nameEdit.toPlainText().strip()
        if name:
            self.mainApp.saveName(name)
            self.accept()
        else:
            self.nameEdit.setPlaceholderText('\u540d\u5b57\u4e0d\u80fd\u4e3a\u7a7a\uff0c\u8bf7\u91cd\u65b0\u8f93\u5165')

    def reject(self): super().reject()
