# -*- coding:utf-8 -*-
import sys, os, random, time, threading, pickle, socket, json
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
import setting, fileRead, i18n
from PySide6.QtCore import QPoint, QRect, QRectF, Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QColor, QAction, QIcon, QPainter, QPixmap, QActionGroup, QGuiApplication, QTextDocument
from PySide6.QtWidgets import (QLabel, QMenu, QWidget, QDialog, QSystemTrayIcon, QTextEdit, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QApplication, QScrollArea)
from PySide6.QtGui import QActionGroup
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

RES_DIR = PROJECT_ROOT / 'res'
IMAGE_DIR = RES_DIR / 'image'
SOUND_DIR = RES_DIR / 'sound'
TEXT_DIR = RES_DIR / 'text'
SAV_DIR = PROJECT_ROOT / 'sav'

class MessageServer(QThread):
    """TCP/UDP 消息服务器，接受外部消息并显示到对话框"""
    messageReceived = Signal(str)  # 信号：收到消息时触发

    def __init__(self, port=7654):
        super().__init__()
        self.port = port
        self.running = False
        self.tcp_socket = None
        self.udp_socket = None

    def run(self):
        self.running = True
        # TCP 服务器
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(('127.0.0.1', self.port))
        self.tcp_socket.listen(5)
        self.tcp_socket.settimeout(1.0)  # 允许超时退出

        # UDP 服务器
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(('127.0.0.1', self.port))
        self.udp_socket.settimeout(1.0)

        while self.running:
            # TCP 接受
            try:
                client, addr = self.tcp_socket.accept()
                data = client.recv(4096).decode('utf-8', errors='ignore')
                client.close()
                if data and self.messageReceived:
                    self.messageReceived.emit(data.strip())
            except socket.timeout:
                pass
            except Exception:
                pass

            # UDP 接收
            try:
                data, addr = self.udp_socket.recvfrom(4096)
                message = data.decode('utf-8', errors='ignore').strip()
                if message and self.messageReceived:
                    self.messageReceived.emit(message)
            except socket.timeout:
                pass
            except Exception:
                pass

    def stop(self):
        self.running = False
        if self.tcp_socket:
            try: self.tcp_socket.close()
            except: pass
        if self.udp_socket:
            try: self.udp_socket.close()
            except: pass

class SoundPlaying(threading.Thread):
    def __init__(self):
        super().__init__(); self.setDaemon(True)
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
        super().__init__(); self.setDaemon(True)
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
    def __init__(self, character, dialogList):
        super().__init__(); self.character = character; self.unconscious = ''
        result = ''
        for line in dialogList: result += fileRead.fileReadStr(line, 'unconscious')
        result = result.split(':'); self.unconscious = result[1]
        self.addAction(PlayerAction(self, self.character, 'unconscious', result[0].strip(), setting.ActionSetting, result[1].strip()))
        for reaction in setting.reactionList:
            result = ''
            for line in dialogList: result += fileRead.fileReadStr(line, reaction)
            if result:
                result = result.split(':'); self.addAction(PlayerAction(self, self.character, reaction, result[0].strip(), setting.ActionSetting, result[1].strip()))

    def posShow(self, pos): self.move(pos); self.show()

class Sentence:
    def __init__(self, sentence):
        self.condition = {}; self.goto = ''; self.context = sentence; self.icon = ''; self.sound = ''
        if self.context.find('@') > 0:
            self.icon = str(IMAGE_DIR / (self.context.split('@')[0].strip() + '.png'))
            self.context = self.context.split('@')[1].strip()
        if self.context.find('^') > 0:
            self.sound = str(SOUND_DIR / (self.context.split('^')[0].strip() + '.wav'))
            self.context = self.context.split('^')[1].strip()
        if self.context.find('|') > 0:
            condition_parts = self.context.split('|')[0].split('&')
            self.context = self.context.split('|')[1].strip()
            for cond in condition_parts:
                for variable in setting.variable.keys():
                    if cond.find(variable) > -1: self.condition[variable] = fileRead.fileReadStr(cond, variable)
        if self.context.find(':') > 0:
            self.goto = self.context.split(':')[1].strip()
            self.context = self.context.split(':')[0].strip()

class Stating:
    def __init__(self, name, dialogList):
        self.name = name; self.context = {}; self.settingContext(dialogList)

    def settingContext(self, dialogList):
        for relation in setting.relationList:
            self.context[relation] = fileRead.listReadLines(f'_{relation}_', '_end_', dialogList)
            if not self.context[relation]: self.context[relation] = self.context[setting.relationTree[relation]]
            else:
                for i in range(len(self.context[relation])): self.context[relation][i] = Sentence(self.context[relation][i])

    def showSentence(self, relation):
        readyList = []
        for sentence in self.context[relation]:
            success = True
            for variable in setting.variable.keys():
                if variable in sentence.condition.keys():
                    if sentence.condition[variable] != setting.variable[variable]: success = False; break
            if success: readyList.append(sentence)
        if not readyList: return '', '', '', ''
        num = random.randrange(len(readyList))
        return readyList[num].context, readyList[num].goto, readyList[num].icon, readyList[num].sound

class Language:
    def __init__(self, character):
        talkfile_path = TEXT_DIR / 'talk.txt'
        funcfile_path = TEXT_DIR / 'function.txt'
        with open(talkfile_path, 'r', encoding='utf-8') as file: self.talkfile = fileRead.fileToList(file)
        with open(funcfile_path, 'r', encoding='utf-8') as file: self.funcfile = fileRead.fileToList(file)
        self.stating = {}; self.dialogMenu = {}; self.currentMenu = None
        self.currentMessage = ('', '', '', ''); self.nextMessage = ('', '', '', '')
        self.currentState = ''; self.nextState = ''; self.character = character
        self.initialize(); self.fadeOutTime = 0

    def replaceText(self, line):
        line = line.replace('_TIMEPERIOD_', setting.getTimePeriod())
        line = line.replace('_CALLING_', setting.text_calling)
        line = line.replace('\\n', '\n')
        for define_key in self.outerDefine.keys(): line = line.replace(f'_{define_key}_', self.outerDefine[define_key])
        return line

    def initialize(self):
        context = fileRead.listReadAllLines('====================talk====================', '====================talk====================', self.talkfile)
        for dialogList in context:
            name = fileRead.fileReadStr(dialogList[0], 'state')
            self.stating[name] = Stating(name, dialogList)
        reaction = fileRead.listReadAllLines('====================func====================', '====================func====================', self.funcfile)
        for dialogList in reaction:
            name = fileRead.fileReadStr(dialogList[0], 'state')
            self.dialogMenu[name] = dialogList
        self.outerDefine = fileRead.fileReadVariable(str(TEXT_DIR / 'define.txt'))

    @property
    def currentState(self): return self._currentState
    @currentState.setter
    def currentState(self, value): self._currentState = value

    def showSpeakTime(self): return setting.showSpeakTime(self.showMessage())
    def showMessage(self): return self.replaceText(self.currentMessage[0])
    def showState(self): return self._currentState
    def showGoto(self): return self.currentMessage[1]
    def showFace(self): return self.currentMessage[2]
    def showSound(self): return self.currentMessage[3]

    def swap(self):
        self.currentMessage = self.nextMessage; self._currentState = self.nextState
        if self.currentMessage[1]:
            self.currentMenu = DialogMenu(self.character, self.dialogMenu[self.currentMessage[1]])
        else: self.currentMenu = None
        if self.currentMessage[3]: self.character.soundThread.swap(self.currentMessage[3])
        if self.currentMenu: self.setNextMessage(self.currentMenu.unconscious, 0)
        else: self.setNextMessage('', 0)

    def showFadeOutTime(self):
        if self.fadeOutTime: t = self.fadeOutTime; self.fadeOutTime = 0; return t
        else: return self.showSpeakTime()

    def setNextText(self, text, fadeOutTime):
        if text: self.nextMessage = (text, '', '', ''); self.nextState = ''; self.fadeOutTime = fadeOutTime

    def setNextMessage(self, name, fadeOutTime):
        if name:
            if name in self.stating.keys():
                self.nextMessage = self.stating[name].showSentence(self.character.mood.relation)
                self.nextState = name; self.fadeOutTime = fadeOutTime
        else: self.nextMessage = ('', '', '', ''); self.nextState = ''; self.fadeOutTime = fadeOutTime

class Mood:
    def __init__(self):
        self.familiar = 0.0; self.friendship = 0.0; self.love = 0.0; self.fear = 0.0; self.hate = 0.0
        self.happy = 0.0; self.angry = 0.0; self.sorrow = 0.0; self.horror = 0.0; self.surprised = 0.0; self.shyness = 0.0
        self.relation = 'strange'; self.emotion = 'normal'
        self.tired = 0.0; self.interest = 0.0; self.stopMoving = False

    def showFace(self): return setting.emotionSetting(self)
    def initialize(self):
        self.happy = 0.0; self.angry = 0.0; self.sorrow = 0.0; self.horror = 0.0
        self.surprised = 0.0; self.tired = 0.0; self.interest = 1.0; self.stopMoving = False
    def update(self): setting.moodUpdate(self)
    def posWalkSpeed(self):
        speed = (50 - self.tired) / 100 * (self.angry + self.happy + 20) / (self.sorrow + self.horror + self.surprised + 20)
        return max(0.8, min(1.2, speed))
    def animeWalkSpeed(self): return max(0.9, min(1.1, self.posWalkSpeed()))
    def changeDirectionChance(self): return 0.1
    def moveChance(self):
        chance = (50 - self.tired) / 100 * self.happy * self.angry / self.horror / self.sorrow
        return max(0.0, min(0.5, chance))
    def stopChance(self):
        chance = 1.0 / (0.1 + self.moveChance())
        return max(0.5, min(1.0, chance))
    def chatChance(self):
        chance = (self.interest + 1.0) * self.happy / 20.0 / self.angry / self.horror / self.sorrow
        return max(0.0, min(1.0, chance))
class Spirit(QLabel):
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        config_path = TEXT_DIR / 'config.txt'
        try:
            with open(config_path, 'r', encoding='utf-8') as file: config_list = file.readlines()
            self.animeWalkSpeed = fileRead.listReadInt(config_list, 'animeWalkSpeed')
            self.posWalkSpeed = fileRead.listReadInt(config_list, 'posWalkSpeed')
            self.chatChance = fileRead.listReadFloat(config_list, 'chatChance')
            self.changeDirectionChance = fileRead.listReadFloat(config_list, 'changeDirectionChance')
            self.moveChance = fileRead.listReadFloat(config_list, 'moveChance')
            self.stopChance = fileRead.listReadFloat(config_list, 'stopChance')
            self.frameRawNum = fileRead.listReadInt(config_list, 'frameRawNum')
            self.standFrame = fileRead.actionFrameSetting(config_list, 'standFrame')
            self.walkFrame = fileRead.actionFrameSetting(config_list, 'walkFrame')
            self.headIconWidth = fileRead.listReadInt(config_list, 'headIconWidth')
            self.headIconHeight = fileRead.listReadInt(config_list, 'headIconHeight')
            self.dialogMargin = fileRead.listReadInt(config_list, 'dialogMargin')
            self.dialogWidth = fileRead.listReadInt(config_list, 'dialogWidth')
            self.dialogHeight = fileRead.listReadInt(config_list, 'dialogHeight')
            self.fontFamily = fileRead.listReadStr(config_list, 'fontFamily')
            self.fontSize = fileRead.listReadInt(config_list, 'fontSize')
            self.fontColor = QColor(fileRead.listReadInt(config_list, 'fontRed'), fileRead.listReadInt(config_list, 'fontGreen'), fileRead.listReadInt(config_list, 'fontBlue'), fileRead.listReadInt(config_list, 'fontAlpha'))
        except:
            self.animeWalkSpeed = 5; self.posWalkSpeed = 10; self.chatChance = 0.1; self.changeDirectionChance = 0.1
            self.moveChance = 0.3; self.stopChance = 0.7; self.frameRawNum = 4
            self.standFrame = [0,1,2,3]; self.walkFrame = [0,1,2,3]
            self.headIconWidth = 80; self.headIconHeight = 80; self.dialogMargin = 10
            self.dialogWidth = 300; self.dialogHeight = 100
            self.fontFamily = 'song'; self.fontSize = 12; self.fontColor = QColor(0, 0, 0, 255)
        self.animeWalkSpeed *= 3  # 60fps tick scaling
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
        if check < self.character.mood.changeDirectionChance() * self.changeDirectionChance: self.nextDirection = random.randrange(4)
        if self.stand:
            if random.random() < self.character.mood.moveChance() * self.moveChance: self.stand = False
        else:
            if random.random() < self.character.mood.stopChance() * self.stopChance: self.stand = True

    def mousePressEvent(self, event):
        self.character.activate()
        if event.button() == Qt.LeftButton: self.mouseOnPoint = QPoint(event.pos()); self.stopMoving = True
        if event.button() == Qt.RightButton and not self.exitFlag: self.testActionMenu.posShow(event.globalPos())
        if event.button() == Qt.MiddleButton: self.character.dialog.chat()

    def mouseMoveEvent(self, event):
        if self.mouseOnPoint:
            self.move(event.globalPos().x() - self.mouseOnPoint.x(), event.globalPos().y() - self.mouseOnPoint.y())
            self.character.dialog.posUpdate()

    def mouseReleaseEvent(self, event): self.mouseOnPoint = None; self.stopMoving = False
    def centerPos(self): return self.pos() + QPoint(self.width // 2, self.height // 2)

    def update(self):
        if not self.timeCount % 1800: self.character.mainApplication.save()
        if not self.timeCount % 180:
            if self.character.isPlayingMusic(): self.character.mood.tired += 2
            self.character.mood.update()
            if not (self.stopMoving or self.character.dialog.standFlag or self.testActionMenu.isVisible() or self.positionMove or self.character.mood.stopMoving): self.randomDirection()
        if (self.stopMoving or self.character.dialog.standFlag or self.testActionMenu.isVisible() or self.character.mood.stopMoving) and not self.exitFlag: self.stand = True; self.nextDirection = 0
        elif self.positionMove: self.positionMoveFunc()
        if self.exitFlag: self.destiny = QPoint(-500, self.pos().y()); self.positionMove = True
        self.timeCount += 1
        direction_map = {(0, 3): 1, (1, 2): 3, (2, 1): 0, (3, 0): 2}
        key = (self.currentDirection, self.nextDirection)
        self.currentDirection = direction_map.get(key, self.nextDirection)
        self.frameCount += 1
        frameList = self.standFrame if self.stand else self.walkFrame
        if self.frameCount > int(self.animeWalkSpeed / max(0.1, self.character.mood.animeWalkSpeed())): self.frameCount = 0; self.currentFrame += 1
        if self.currentFrame >= len(frameList): self.currentFrame = 0
        self.setPixmap(self.moveImage.frameImage(frameList[self.currentFrame], self.currentDirection))
        if not self.stand:
            self.character.mood.tired += 0.03
            self.move(self.pos() + int(self.posWalkSpeed * self.character.mood.posWalkSpeed() / 3) * self.moveDirectionList[self.currentDirection])
            sw, sh = self.screen.width(), self.screen.height()
            if self.pos().x() > sw - self.width: self.nextDirection = 1
            if self.pos().y() > sh - self.height: self.nextDirection = 3
            if self.pos().x() < 0: self.nextDirection = 2
            if self.pos().y() < 0: self.nextDirection = 0
        self.character.dialog.update()
class Dialog(QWidget):
    """对话框：显示角色头像+文字（支持HTML/Markdown、自适应高度、桌面范围内）"""
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(1.0)
        self.screen = QGuiApplication.primaryScreen().geometry()
        self.character = character

        # 基础尺寸（文本区默认最大高度设为屏幕40%）
        self.margin = self.character.spirit.dialogMargin
        self.iconWidth = self.character.spirit.headIconWidth
        self.iconHeight = self.character.spirit.headIconHeight
        self.minTextWidth = self.character.spirit.dialogWidth
        self.maxTextHeight = int(self.screen.height() * 0.4)
        self.baseTextHeight = self.character.spirit.dialogHeight

        self.Image = {'normal': 0, 'happy': 2, 'cheerful': 4, 'teasing': 6, 'sad': 8, 'surprised': 10, 'crying': 12, 'angry': 14}
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

        # 文字显示用 QTextEdit（只读，支持HTML）
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.textEdit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.textEdit.setFocusPolicy(Qt.NoFocus)
        self.textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # 文字边距：上下左右各15px
        self.textPadding = 15
        self.textEdit.setStyleSheet(
            f"QTextEdit {{ background: transparent; border: none; padding: {self.textPadding}px; margin: 0; }}"
        )
        self.textEdit.document().setDocumentMargin(self.textPadding)

        # 设置字体（比配置字体大2px）
        dialogFont = QFont(self.character.spirit.fontFamily, self.character.spirit.fontSize + 2)
        self.textEdit.setFont(dialogFont)

        # 初始窗口大小：icon + 文本区
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

    def chat(self):
        if self.character.language.showState() != 'chat':
            self.speak('chat')

    def posUpdate(self):
        self.moveTo(self.character.spirit.centerPos())

    def setExternalMessage(self, message, fadeOutTime=300):
        """显示外部消息（来自网络服务器）支持 HTML/Markdown"""
        # 预处理：把 Markdown 转为 HTML
        html = self._renderContent(message)
        self.textEdit.setHtml(html)
        self._adjustSize()

        # 中断当前说话，强行显示外部消息
        self.funcBreakSpeak()
        self.speakTimeOut = self.timeCount + fadeOutTime
        self.fadeOutTimeOut = self.timeCount + fadeOutTime + 60
        self.fadeIn()

    def _renderContent(self, text):
        """简单 Markdown→HTML 转换"""
        if not text:
            return ""
        # 转义 HTML 特殊字符（不在 pre/code 块内时）
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
            # 标题
            if stripped.startswith('### '):
                result.append(f'<h3>{self._escapeHtml(stripped[4:])}</h3>')
            elif stripped.startswith('## '):
                result.append(f'<h2>{self._escapeHtml(stripped[3:])}</h2>')
            elif stripped.startswith('# '):
                result.append(f'<h1>{self._escapeHtml(stripped[2:])}</h1>')
            # 列表
            elif stripped.startswith('- ') or stripped.startswith('* '):
                result.append(f'<li>{self._inlineRender(stripped[2:])}</li>')
            # 分割线
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
        """行内渲染：加粗、斜体、代码、行内Markdown"""
        result = self._escapeHtml(text)
        # 行内代码 `code`
        import re
        result = re.sub(r'`([^`]+)`', r'<code>\1</code>', result)
        # 加粗 **bold**
        result = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', result)
        # 斜体 *italic*
        result = re.sub(r'\*(.+?)\*', r'<i>\1</i>', result)
        # 删除线 ~~del~~
        result = re.sub(r'~~(.+?)~~', r'<s>\1</s>', result)
        # 链接 [text](url)
        result = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', result)
        return result

    def _adjustSize(self):
        """根据文本内容自适应窗口高度，保持在屏幕范围内"""
        doc = self.textEdit.document()
        # 文本内容宽度 = 窗口宽度 - 左右padding - 对话框边框
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
        if self.character.language.showState() in ('chat', 'talk'):
            self.standFlag = True
        else:
            self.standFlag = False
        if self.timeCount > self.fadeOutTimeOut:
            self.fadeOut()
        if self.timeCount > self.speakTimeOut:
            self.hideFlag = False
        if self.alpha < 0.05 and not self.hideFlag:
            self.character.language.swap()
            if self.character.language.currentMessage[0]:
                msg = self.character.language.showMessage()
                html = self._renderContent(msg)
                self.textEdit.setHtml(html)
                self._adjustSize()
                self.speakTimeOut = self.timeCount + self.character.language.showSpeakTime()
                self.fadeOutTimeOut = self.timeCount + self.character.language.showFadeOutTime()
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
        # 头像
        if self.character.language.showFace():
            iconName = self.character.language.showFace()
        else:
            iconName = str(IMAGE_DIR / f'{self.Image[self.face] + self.direction}.png')
        iconPixmap = QPixmap(iconName)
        if not iconPixmap.isNull():
            scaledIcon = iconPixmap.scaledToWidth(self.iconWidth, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaledIcon.copy(0, 0, self.iconWidth, self.iconHeight))
        # 对话框背景
        textY = self.iconHeight
        textH = self.textEdit.height()
        rect = QRect(0, textY, self.width(), textH)
        dialogPixmap = QPixmap(str(IMAGE_DIR / 'dialog.png'))
        if not dialogPixmap.isNull():
            painter.drawPixmap(rect, dialogPixmap.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # QTextEdit 覆盖在文本区上
        self.textEdit.move(0, textY)

    def checkDirection(self):
        if self.centerPos().x() < (self.screen.width() // 2) and not self.direction:
            self.direction = 1
        elif self.centerPos().x() > (self.screen.width() // 2) and self.direction:
            self.direction = 0

    def centerPos(self):
        return self.pos() + QPoint(self.iconWidth // 2, self.iconHeight // 2)

    def moveTo(self, pos):
        # pos 是精灵头顶中间的位置 (centerPos)
        spiritX = pos.x()  # 精灵中心的x
        spiritY = pos.y()  # 精灵中心的y
        spiritH = self.character.spirit.height

        # 对话框总尺寸
        totalWidth = self.iconWidth + self.textEdit.width()
        totalHeight = self.iconHeight + self.textEdit.height()

        # 目标：对话框顶部与精灵顶部对齐（头顶贴着头顶）
        # 精灵的顶部 = spiritY - spiritH//2
        spiritTop = spiritY - spiritH // 2

        # 水平：精灵居中于水平位置
        preferredX = spiritX - totalWidth // 2
        if preferredX + totalWidth > self.screen.width() - 20:
            preferredX = self.screen.width() - totalWidth - 20
        if preferredX < 20:
            preferredX = 20

        # 优先：对话框顶部对齐精灵顶部，水平居中
        preferredY = spiritTop - totalHeight - self.margin

        # 如果上方放不下（超出屏幕顶部），改放精灵下方，顶部对齐精灵顶部
        if preferredY < 20:
            preferredY = spiritTop + self.margin

        # 确保不超出屏幕底部
        if preferredY + totalHeight > self.screen.height() - 20:
            preferredY = self.screen.height() - totalHeight - 20

        self.move(preferredX, preferredY)
        self.checkDirection()

    def mousePressEvent(self, event):
        self.character.activate()
        if event.button() == Qt.RightButton:
            if self.character.language.currentMenu:
                self.character.language.currentMenu.posShow(event.globalPos())
        else:
            self.hideFlag = True

    def dropEvent(self, event):
        name = event.mimeData().urls()[0].path()
        if name.startswith('/'):
            name = name[1:]
        lrcName = name[:-3] + 'lrc'
        self.lyric = fileRead.lyricRead(lrcName)
        if self.lyric:
            self.currentLyric = 0
        if self.character.musicThread and self.character.musicThread.operation:
            self.character.musicThread.swapMusic(name)
        else:
            self.character.musicThread = MusicPlaying(name)

    def dragEnterEvent(self, event):
        if event.mimeData().urls()[0].path().split('.')[-1].upper() in ('MP3', 'WAV'):
            event.accept()

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
        # 向托盘菜单添加选项（使用 i18n）
        self.menu.addAction(i18n.tr("menu.talk", "聊天"), lambda: self._trigger_action('talk'))
        self.menu.addAction(i18n.tr("menu.touch", "触摸"), lambda: self._trigger_action('touch'))
        self.menu.addSeparator()
        self.menu.addAction(i18n.tr("menu.exit", "离开"), lambda: self._trigger_action('exit'))

    def _trigger_action(self, action_name):
        """触发菜单动作"""
        if action_name == 'exit':
            self.character.exiting()
        elif action_name == 'talk':
            self.character.spirit.standFlag = True
            self.character.activate()
        elif action_name == 'touch':
            self.character.spirit.standFlag = True
            self.character.activate()

    def clickMessage(self, message):
        if message == QSystemTrayIcon.Trigger:
            if hasattr(self.character.language, 'outerDefine'):
                self.showMessage(str(self.name), str(self.character.language.outerDefine.get('CLICK_TEXT', 'Click!')))
            self.character.activate()

class Character:
    def __init__(self, timer, mainApplication):
        self.timer = timer; self.spirit = Spirit(self); self.dialog = Dialog(self)
        self.language = Language(self); self.mood = Mood()
        self.soundThread = SoundPlaying(); self.musicThread = None
        self.mainApplication = mainApplication; self.activate()

        # 启动消息服务器（TCP+UDP）
        if getattr(setting, 'MESSAGE_SERVER_ENABLED', True):
            port = getattr(setting, 'MESSAGE_SERVER_PORT', 7654)
            self.msgServer = MessageServer(port)
            self.msgServer.messageReceived.connect(self.onExternalMessage)
            self.msgServer.start()
        else:
            self.msgServer = None

    def onExternalMessage(self, message):
        """收到外部消息，在主线程中显示到对话框"""
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
        return bool(self.musicThread and self.musicThread.operation and not (self.musicThread.pauseFlag or self.musicThread.stopFlag or self.musicThread.swapFlag))

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
                'familiar': self.character.mood.familiar, 'friendship': self.character.mood.friendship,
                'love': self.character.mood.love, 'fear': self.character.mood.fear, 'hate': self.character.mood.hate,
                'happy': self.character.mood.happy, 'angry': self.character.mood.angry, 'sorrow': self.character.mood.sorrow,
                'horror': self.character.mood.horror, 'surprised': self.character.mood.surprised, 'shyness': self.character.mood.shyness,
                'relation': self.character.mood.relation, 'emotion': self.character.mood.emotion, 'tired': self.character.mood.tired,
                'interest': self.character.mood.interest, 'stopMoving': self.character.mood.stopMoving,
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


if __name__ == '__main__':
    sys.exit(main())
