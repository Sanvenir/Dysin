# -*- coding:utf-8 -*-
"""Dialog bubble widget (head icon + text, HTML/Markdown)."""
import os, re
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QFont, QColor, QPainter, QPixmap, QGuiApplication
from PySide6.QtWidgets import QWidget, QTextEdit
from dysin.core.config import IMAGE_DIR
from dysin.network.audio import MusicPlaying
from dysin.core import setting


class Dialog(QWidget):
    """Dialog bubble with head icon and text area."""

    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(1.0)
        self.screen = QGuiApplication.primaryScreen().geometry()
        self.character = character
        self.margin = self.character.spirit.dialogMargin
        self.iconWidth = self.character.spirit.headIconWidth
        self.iconHeight = self.character.spirit.headIconHeight
        self.minTextWidth = self.character.spirit.dialogWidth
        self.maxTextHeight = int(self.screen.height() * 0.4)
        self.baseTextHeight = self.character.spirit.dialogHeight
        self.Image = {'normal': 0, 'happy': 2, 'cheerful': 4, 'teasing': 6, 'sad': 8,
                      'surprised': 10, 'crying': 12, 'angry': 14}
        self.direction = 0
        self.directionPos = 0
        self.face = 'normal'
        self.alpha = 0
        self.timeCount = 0
        self.standFlag = False
        self.fadeOutTimeOut = 0
        self.speakTimeOut = 0
        self.hideFlag = False
        self.setWindowOpacity(self.alpha)
        self.currentLyric = 0
        self.playingMusic = False
        self.lyric = 0
        self.fadeFlag = True
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.textEdit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.textEdit.setFocusPolicy(Qt.NoFocus)
        self.textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.textPadding = 15
        self.textEdit.setStyleSheet(
            f"QTextEdit {{ background: transparent; border: none; padding: {self.textPadding}px; margin: 0; }}"
        )
        self.textEdit.document().setDocumentMargin(self.textPadding)
        dialogFont = QFont(self.character.spirit.fontFamily, self.character.spirit.fontSize + 2)
        self.textEdit.setFont(dialogFont)
        self.resize(self.minTextWidth, self.iconHeight + self.baseTextHeight)
        self.show()

    def changeFace(self, face):
        if face in self.Image.keys():
            self.face = face

    def breakSpeak(self):
        self.funcBreakSpeak()
        setting.ActionSetting(self.character.mood, 'break')

    def funcBreakSpeak(self):
        self.speakTimeOut = self.timeCount
        self.fadeOutTimeOut = self.timeCount

    def speak(self, name, fadeOutTime=0):
        self.character.language.setNextMessage(name, fadeOutTime)
        self.hideFlag = False

    def chat(self):
        if self.character.language.showState() != 'chat':
            self.speak('chat')

    def posUpdate(self):
        self.moveTo(self.character.spirit.centerPos())

    def setExternalMessage(self, message, fadeOutTime=300):
        html = self._renderContent(message)
        self.textEdit.setHtml(html)
        self._adjustSize()
        self.funcBreakSpeak()
        self.speakTimeOut = self.timeCount + fadeOutTime
        self.fadeOutTimeOut = self.timeCount + fadeOutTime + 60
        self.fadeIn()

    def _renderContent(self, text):
        if not text:
            return ""
        lines = text.split('\n')
        result = []
        inCodeBlock = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('```'):
                inCodeBlock = not inCodeBlock
                result.append('')
                continue
            if inCodeBlock:
                result.append(f'<pre>{self._escapeHtml(line)}</pre>')
                continue
            if stripped.startswith('### '):
                result.append(f'<h3>{self._escapeHtml(stripped[4:])}</h3>')
            elif stripped.startswith('## '):
                result.append(f'<h2>{self._escapeHtml(stripped[3:])}</h2>')
            elif stripped.startswith('# '):
                result.append(f'<h1>{self._escapeHtml(stripped[2:])}</h1>')
            elif stripped.startswith('- ') or stripped.startswith('* '):
                result.append(f'<li>{self._inlineRender(stripped[2:])}</li>')
            elif stripped == '---' or stripped == '***':
                result.append('<hr>')
            else:
                result.append(f'<p>{self._inlineRender(line)}</p>')
        return '<br>'.join(result)

    def _escapeHtml(self, text):
        return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))

    def _inlineRender(self, text):
        result = self._escapeHtml(text)
        result = re.sub(r'`([^`]+)`', r'<code>\1</code>', result)
        result = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', result)
        result = re.sub(r'\*(.+?)\*', r'<i>\1</i>', result)
        result = re.sub(r'~~(.+?)~~', r'<s>\1</s>', result)
        result = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', result)
        return result

    def _adjustSize(self):
        doc = self.textEdit.document()
        contentWidth = self.minTextWidth - 2 * self.textPadding - 10
        doc.setTextWidth(contentWidth)
        textHeight = int(doc.size().height()) + 2 * self.textPadding
        textHeight = max(50, min(textHeight, self.maxTextHeight))
        self.textEdit.setFixedHeight(textHeight)
        totalHeight = self.iconHeight + textHeight
        self.resize(self.minTextWidth, totalHeight)

    def talkUpdate(self):
        self.repaint()
        if self.character.isPlayingMusic() and self.lyric:
            self.playingMusic = True
            if self.character.musicThread.getTime() > self.lyric[self.currentLyric][0]:
                self.funcBreakSpeak()
                self.character.language.setNextText(self.lyric[self.currentLyric][1], 0)
                self.currentLyric += 1
                if self.currentLyric == len(self.lyric):
                    self.lyric = 0
        else:
            self.playingMusic = False
        self.standFlag = self.alpha > 0.05
        if self.timeCount > self.fadeOutTimeOut:
            self.fadeOut()
        if self.timeCount > self.speakTimeOut:
            self.hideFlag = False
        if self.alpha < 0.05 and not self.hideFlag and self.character.language.nextMessage[0]:
            self.character.language.swap()
            if self.character.language.currentMessage[0]:
                msg = self.character.language.showMessage()
                html = self._renderContent(msg)
                self.textEdit.setHtml(html)
                self._adjustSize()
                self.speakTimeOut = self.timeCount + self.character.language.showSpeakTime()
                self.fadeOutTimeOut = self.timeCount + self.character.language.showFadeOutTime()
                # 带 goto 的消息：置顶 + 延长停留，给用户反应时间
                if self.character.language.currentMenu:
                    self.activateWindow()
                    self.raise_()
                    self.speakTimeOut += 300
                    self.fadeOutTimeOut += 360
                self.fadeIn()

    def update(self):
        self.changeFace(self.character.mood.showFace())
        self.timeCount += 1
        self.setWindowOpacity(self.alpha)
        self.talkUpdate()
        self.posUpdate()
        if self.hideFlag:
            self.fadeOut()
        if self.fadeFlag:
            self.alpha = min(1.0, self.alpha + 0.06)
        else:
            self.alpha = max(0.0, self.alpha - 0.06)

    def fadeIn(self):
        self.fadeFlag = True

    def fadeOut(self):
        self.fadeFlag = False

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        if self.character.language.showFace():
            iconName = self.character.language.showFace()
        else:
            iconName = str(IMAGE_DIR / f'{self.Image[self.face] + self.direction}.png')
        iconPixmap = QPixmap(iconName)
        if not iconPixmap.isNull():
            scaledIcon = iconPixmap.scaledToWidth(self.iconWidth, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaledIcon.copy(0, 0, self.iconWidth, self.iconHeight))
        textY = self.iconHeight
        textH = self.textEdit.height()
        rect = QRect(0, textY, self.width(), textH)
        dialogPixmap = QPixmap(str(IMAGE_DIR / 'dialog.png'))
        if not dialogPixmap.isNull():
            painter.drawPixmap(rect, dialogPixmap.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.textEdit.move(0, textY)

    def checkDirection(self):
        if self.centerPos().x() < (self.screen.width() // 2) and not self.direction:
            self.direction = 1
        elif self.centerPos().x() > (self.screen.width() // 2) and self.direction:
            self.direction = 0

    def centerPos(self):
        return self.pos() + QPoint(self.iconWidth // 2, self.iconHeight // 2)

    def moveTo(self, pos):
        spiritX = pos.x()
        spiritY = pos.y()
        spiritH = self.character.spirit.height
        totalWidth = self.iconWidth + self.textEdit.width()
        totalHeight = self.iconHeight + self.textEdit.height()
        spiritTop = spiritY - spiritH // 2
        preferredX = spiritX - totalWidth // 2
        if preferredX + totalWidth > self.screen.width() - 20:
            preferredX = self.screen.width() - totalWidth - 20
        if preferredX < 20:
            preferredX = 20
        preferredY = spiritTop - totalHeight - self.margin
        if preferredY < 20:
            preferredY = spiritTop + self.margin
        if preferredY + totalHeight > self.screen.height() - 20:
            preferredY = self.screen.height() - totalHeight - 20
        self.move(preferredX, preferredY)
        self.checkDirection()

    def mousePressEvent(self, event):
        self.character.activate()
        if event.button() == Qt.RightButton:
            if self.character.language.currentMenu:
                self.character.language.currentMenu.posShow(event.globalPosition().toPoint())
        else:
            self.hideFlag = True

    def dropEvent(self, event):
        name = event.mimeData().urls()[0].path()
        if name.startswith('/'):
            name = name[1:]
        lrcName = name[:-3] + 'lrc'
        lyric = []
        try:
            with open(lrcName, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    if ']' not in line:
                        continue
                    time_part, text = line.split(']', 1)
                    time_part = time_part.strip('[')
                    try:
                        minutes = int(time_part.split(':')[0])
                        seconds = float(time_part.split(':')[1])
                        real_time = minutes * 60 + seconds
                        lyric.append([real_time, text.strip()])
                    except (ValueError, IndexError):
                        pass
        except IOError:
            pass
        self.lyric = lyric
        if self.lyric:
            self.currentLyric = 0
        if self.character.musicThread and self.character.musicThread.operation:
            self.character.musicThread.swapMusic(name)
        else:
            self.character.musicThread = MusicPlaying(name)

    def dragEnterEvent(self, event):
        if event.mimeData().urls()[0].path().split('.')[-1].upper() in ('MP3', 'WAV'):
            event.accept()
