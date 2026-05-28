# -*- coding:utf-8 -*-
"""Image frame / sprite-sheet helper."""
import os
from PySide6.QtGui import QPixmap


class FramePixmap:
    def __init__(self, fileName=None, col=4, raw=4):
        self.fileName = fileName; self.col = col; self.raw = raw
        if fileName and os.path.exists(fileName):
            self.originImage = QPixmap(fileName)
            if not self.originImage.isNull():
                self.imageWidth = self.originImage.width() // raw
                self.imageHeight = self.originImage.height() // col
                self.frameNum = raw
            else: self._set_defaults()
        else: self._set_defaults()

    def _set_defaults(self):
        self.imageWidth = 64; self.imageHeight = 64; self.frameNum = 4
        self.originImage = QPixmap()

    def frameImage(self, x, y):
        if self.originImage.isNull(): return QPixmap()
        return self.originImage.copy(x * self.imageWidth, y * self.imageHeight, self.imageWidth, self.imageHeight)
