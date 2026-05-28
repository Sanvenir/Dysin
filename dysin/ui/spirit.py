# -*- coding:utf-8 -*-
"""Character spirit / sprite (movable QLabel on desktop)."""
import sys, os, random
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPixmap, QGuiApplication
from PySide6.QtWidgets import QLabel
from dysin.core.config import IMAGE_DIR
from dysin.core.frame import FramePixmap
from dysin.ui.menu import ActionMenu
from dysin.core.yaml_handler import get_loader


class Spirit(QLabel):
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        yaml_loader = get_loader()
        sc = yaml_loader.spirit_config
        dc = yaml_loader.dialog_config
        self.animeWalkSpeed = sc.get('anime_walk_speed', 5)
        self.posWalkSpeed = sc.get('pos_walk_speed', 10)
        self.chatChance = sc.get('chat_chance', 1.0)
        self.changeDirectionChance = sc.get('change_direction_chance', 1.0)
        self.moveChance = sc.get('move_chance', 1.0)
        self.stopChance = sc.get('stop_chance', 1.0)
        self.frameRawNum = sc.get('frame_raw_num', 4)
        self.standFrame = sc.get('stand_frame', [0, 1, 2, 3])
        self.walkFrame = sc.get('walk_frame', [0, 1, 2, 3])
        self.headIconWidth = dc.get('head_icon_width', 80)
        self.headIconHeight = dc.get('head_icon_height', 80)
        self.dialogMargin = dc.get('margin', 10)
        self.dialogWidth = dc.get('width', 300)
        self.dialogHeight = dc.get('height', 100)
        self.fontFamily = dc.get('font_family', 'song')
        self.fontSize = dc.get('font_size', 12)
        fc = dc.get('font_color', {})
        self.fontColor = QColor(fc.get('r', 0), fc.get('g', 0), fc.get('b', 0), fc.get('a', 255))
        self.animeWalkSpeed *= 3
        self.screen = QGuiApplication.primaryScreen().geometry()
        move_png = str(IMAGE_DIR / 'move.png')
        if os.path.exists(move_png): self.moveImage = FramePixmap(move_png, raw=self.frameRawNum)
        else: self.moveImage = FramePixmap(None, raw=self.frameRawNum)
        self.width = self.moveImage.imageWidth; self.height = self.moveImage.imageHeight
        self.setPixmap(self.moveImage.frameImage(0, 0))
        self.resize(self.moveImage.imageWidth, self.moveImage.imageHeight)
        self.character = character
        self.moveDirectionList = [QPoint(0, 1), QPoint(-1, 0), QPoint(1, 0), QPoint(0, -1)]
        self.move(-200, 300); self.currentDirection = 1; self.currentFrame = 0; self.frameCount = 0
        self.nextDirection = 0; self.destiny = QPoint(100, 300); self.posDelta = 10; self.timeCount = 0
        self.stand = False; self.positionMove = True; self.stopMoving = False; self.exitFlag = False
        self.testActionMenu = ActionMenu(self.character); self.mouseOnPoint = None

    def positionMoveFunc(self):
        self.stand = False; delta = self.destiny - self.pos()
        if delta.x() > self.posDelta: self.nextDirection = 2
        elif delta.x() < -self.posDelta: self.nextDirection = 1
        elif delta.y() > self.posDelta: self.nextDirection = 0
        elif delta.y() < -self.posDelta: self.nextDirection = 3
        else:
            self.nextDirection = 0; self.stand = True; self.positionMove = False
            if self.exitFlag: self.character.mainApplication.save(); sys.exit(0)

    def randomDirection(self):
        check = random.random()
        if not self.character.isPlayingMusic() and check < self.character.mood.chatChance() * self.chatChance:
            self.character.dialog.chat(); return
        check = random.random()
        if check < self.character.mood.changeDirectionChance() * self.changeDirectionChance:
            self.nextDirection = random.randrange(4)
        if self.stand:
            if random.random() < self.character.mood.moveChance() * self.moveChance: self.stand = False
        else:
            if random.random() < self.character.mood.stopChance() * self.stopChance: self.stand = True

    def mousePressEvent(self, event):
        self.character.activate()
        if event.button() == Qt.LeftButton:
            self.mouseOnPoint = QPoint(event.position().toPoint()); self.stopMoving = True
        if event.button() == Qt.RightButton and not self.exitFlag:
            self.testActionMenu.posShow(event.globalPosition().toPoint())
        if event.button() == Qt.MiddleButton: self.character.dialog.chat()

    def mouseMoveEvent(self, event):
        if self.mouseOnPoint:
            self.move(event.globalPosition().toPoint().x() - self.mouseOnPoint.x(),
                      event.globalPosition().toPoint().y() - self.mouseOnPoint.y())
            self.character.dialog.posUpdate()

    def mouseReleaseEvent(self, event):
        self.mouseOnPoint = None; self.stopMoving = False

    def centerPos(self): return self.pos() + QPoint(self.width // 2, self.height // 2)

    def update(self):
        if not self.timeCount % 1800: self.character.mainApplication.save()
        if not self.timeCount % 180:
            if self.character.isPlayingMusic(): self.character.mood.tired += 2
            self.character.mood.update()
            if not (self.stopMoving or self.character.dialog.standFlag or
                    self.testActionMenu.isVisible() or self.positionMove or
                    self.character.mood.stopMoving):
                self.randomDirection()
        if (self.stopMoving or self.character.dialog.standFlag or
                self.testActionMenu.isVisible() or self.character.mood.stopMoving) and not self.exitFlag:
            self.stand = True; self.nextDirection = 0
        elif self.positionMove: self.positionMoveFunc()
        if self.exitFlag: self.destiny = QPoint(-500, self.pos().y()); self.positionMove = True
        self.timeCount += 1
        direction_map = {(0, 3): 1, (1, 2): 3, (2, 1): 0, (3, 0): 2}
        key = (self.currentDirection, self.nextDirection)
        self.currentDirection = direction_map.get(key, self.nextDirection)
        self.frameCount += 1
        frameList = self.standFrame if self.stand else self.walkFrame
        if self.frameCount > int(self.animeWalkSpeed / max(0.1, self.character.mood.animeWalkSpeed())):
            self.frameCount = 0; self.currentFrame += 1
        if self.currentFrame >= len(frameList): self.currentFrame = 0
        self.setPixmap(self.moveImage.frameImage(frameList[self.currentFrame], self.currentDirection))
        if not self.stand:
            self.character.mood.tired += 0.03
            self.move(self.pos() + int(self.posWalkSpeed * self.character.mood.posWalkSpeed() / 3) *
                      self.moveDirectionList[self.currentDirection])
            sw, sh = self.screen.width(), self.screen.height()
            if self.pos().x() > sw - self.width: self.nextDirection = 1
            if self.pos().y() > sh - self.height: self.nextDirection = 3
            if self.pos().x() < 0: self.nextDirection = 2
            if self.pos().y() < 0: self.nextDirection = 0
        self.character.dialog.update()
