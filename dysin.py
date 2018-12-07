# -*- coding:utf-8 -*-

import sys, random, math, time, pickle, threading
from pymedia import muxer, audio
from PySide import QtCore, QtGui
import fileRead
import setting

reload(sys)
sys.setdefaultencoding("gbk")
import ui_debugWindow
import ui_dialog

QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("utf8"))
QtCore.QTextCodec.setCodecForCStrings(QtCore.QTextCodec.codecForName("utf8"))
QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName("utf8"))


class SoundPlaying(threading.Thread):
    def __init__(self):
        super(SoundPlaying, self).__init__()
        self.setDaemon(True)
        self.operation = True
        self.playFlag = False
        self.swapFlag = False
        self.currentSound = ""
        self.start()

    def loadSound(self, filename):
        f = open(filename, 'rb')
        self.data = f.read()
        f.close()
        self.demuxer = muxer.Demuxer('wav')
        self.frames = self.demuxer.parse(self.data)
        frame = self.frames[0]
        self.decoder = audio.acodec.Decoder(self.demuxer.streams[0])
        r = self.decoder.decode(frame[1])
        self.snd = audio.sound.Output(r.sample_rate, r.channels, audio.sound.AFMT_S16_LE)
        self.snd.setVolume(65000)
        self.playFlag = True

    def run(self):
        while self.operation:
            # print(self.playFlag,self.swapFlag,self.currentSound)
            if self.playFlag or self.swapFlag and self.currentSound:
                self.swapFlag = False
                self.playFlag = True
                self.loadSound(self.currentSound)
                print("playing")
                for frame in self.frames:
                    r = self.decoder.decode(frame[1])
                    if r and r.data:
                        self.snd.play(r.data)
                    if not self.playFlag:
                        break
                    if self.swapFlag:
                        break
                self.playFlag = False

    def swap(self, filename):
        print("swaping")
        self.swapFlag = True
        self.currentSound = filename


class MusicPlaying(threading.Thread):
    def __init__(self, fileName):
        super(MusicPlaying, self).__init__()
        self.setDaemon(True)
        self.loadSound(fileName)
        self.start()

    def playSound(self):
        self.startTime = time.clock()
        self.currentFrame = 1
        self.f.seek(0)
        frames = []
        while not frames:
            data = self.f.read(512)
            frames = self.demuxer.parse(data)
        frame = frames[0]
        self.decoder = audio.acodec.Decoder(self.demuxer.streams[0])
        r = self.decoder.decode(frame[1])
        self.snd = audio.sound.Output(r.sample_rate, r.channels, audio.sound.AFMT_S16_LE)
        while self.operation and data:
            data = self.f.read(512)
            frames = self.demuxer.parse(data)
            for frame in frames:
                r = self.decoder.decode(frame[1])
                if r and r.data:
                    self.snd.play(r.data)
            if self.stopFlag or self.swapFlag:
                if self.snd.getVolume() < 1000:
                    self.snd.stop()
                    self.operation = False
                else:
                    self.snd.setVolume(self.snd.getVolume() - 1000)
            elif self.pauseFlag:
                if self.snd.getVolume() < 1000:
                    self.snd.pause()
                    self.pauseTime = time.clock()
                else:
                    self.snd.setVolume(self.snd.getVolume() - 1000)
            else:
                if self.snd.getVolume() > 64000:
                    self.snd.setVolume(65000)
                else:
                    self.snd.setVolume(self.snd.getVolume() + 1000)
        # self.operation = False
        time.sleep(0.5)
        self.snd.stop()
        if (self.swapFlag):
            self.swapFlag = False
            self.operation = True
            self.loadSound(self.nextMusic)

    def loadSound(self, fileName):
        self.f = open(fileName, 'rb')
        self.demuxer = muxer.Demuxer(fileName[-3:].lower())
        self.pauseFlag = False
        self.stopFlag = False
        self.swapFlag = False
        self.operation = True

    def pause(self):
        self.pauseFlag = True

    def unpause(self):
        self.pauseFlag = False
        self.startTime += time.clock() - self.pauseTime
        self.snd.unpause()

    def run(self):
        while (self.operation):
            self.playSound()

    def getTime(self):
        return time.clock() - self.startTime

    def endPlay(self):
        self.stopFlag = True

    def swapMusic(self, name):
        self.startTime = time.clock()
        self.nextMusic = name
        self.snd.unpause()
        self.swapFlag = True


class Pixmap(QtGui.QPixmap):
    def __init__(self, fileName):
        super(Pixmap, self).__init__(fileName)


class FramePixmap:
    def __init__(self, fileName="res//image//move.png", col=4, raw=4):
        self.originImage = Pixmap(fileName)
        self.imageWidth = self.originImage.rect().width() / raw
        self.imageHeight = self.originImage.rect().height() / col
        self.frameNum = raw

    def frameImage(self, x, y):
        return self.originImage.copy(x * self.imageWidth, y * self.imageHeight, self.imageWidth, self.imageHeight)


class PlayerAction(QtGui.QAction):
    def __init__(self, parent, character, name, label, function, nextMessage=None):
        super(PlayerAction, self).__init__(unicode(label), parent)
        self.name = name
        self.character = character
        self.label = label
        self.function = function
        self.character = character
        self.nextMessage = nextMessage
        self.triggered.connect(self.react)

    def setProperty(self, parent, character, name, label, function, nextMessage=None):
        self.setText(unicode(label))
        self.name = name
        self.character = character
        self.label = label
        self.function = function
        self.character = character
        self.nextMessage = nextMessage

    def react(self):
        if self.character.language.showState() != self.name:
            t = self.function(self.character.mood, self.name)
            if (not self.nextMessage):
                self.nextMessage = t
            if (not self.nextMessage):
                self.nextMessage = self.name
            self.character.dialog.speak(self.nextMessage)
            self.character.activate()


class MediaAction(QtGui.QActionGroup):
    def __init__(self, character, parent):
        super(MediaAction, self).__init__(parent)
        self.character = character
        self.pauseAction = PlayerAction(self, self.character, "pauseMusic", u"暂停播放", self.pauseMusic)
        self.unpauseAction = PlayerAction(self, self.character, "unpauseMusic", u"继续播放", self.unpauseMusic)
        self.stopAction = PlayerAction(self, self.character, "stopMusic", u"停止播放", self.stopMusic)
        self.pauseAction.setIcon(QtGui.QIcon('res//image//pause.png'))
        self.unpauseAction.setIcon(QtGui.QIcon('res//image//unpause.png'))
        self.stopAction.setIcon(QtGui.QIcon('res//image//stop.png'))
        self.addAction(self.pauseAction)
        self.addAction(self.unpauseAction)
        self.addAction(self.stopAction)
        self.setVisible(False)

    def pauseMusic(self, t1="", t2=""):
        self.character.musicThread.pause()

    def unpauseMusic(self, t1="", t2=""):
        self.character.musicThread.unpause()

    def stopMusic(self, t1="", t2=""):
        self.character.musicThread.endPlay()

    def setting(self):
        if self.character.musicThread:
            if self.character.musicThread.operation and not self.character.musicThread.stopFlag:
                self.setVisible(True)
                if self.character.musicThread.pauseFlag:
                    self.pauseAction.setVisible(False)
                    self.unpauseAction.setVisible(True)
                else:
                    self.pauseAction.setVisible(True)
                    self.unpauseAction.setVisible(False)
            else:
                self.setVisible(False)
        else:
            self.setVisible(False)


class ActionMenu(QtGui.QMenu):
    def __init__(self, character):
        super(ActionMenu, self).__init__()
        self.character = character
        self.addAction(PlayerAction(self, self.character, "talk", u"搭话", setting.ActionSetting))
        self.addAction(PlayerAction(self, self.character, "touch", u"摸摸头", setting.ActionSetting))
        self.movingAction = PlayerAction(self, self.character, "disableMoving", u"不要走动", setting.ActionSetting)
        self.musicMenu = MediaAction(self.character, self)
        self.addAction(self.movingAction)
        self.addSeparator()
        self.addActions(self.musicMenu.actions())
        self.addSeparator()
        self.addAction(PlayerAction(self, self.character, "exit", u"离开", self.character.exiting))

    def posShow(self, pos):
        self.musicMenu.setting()
        self.move(pos)
        if self.character.mood.stopMoving:
            self.movingAction.setProperty(self, self.character, "enableMoving", u"自由行动", setting.ActionSetting)
        else:
            self.movingAction.setProperty(self, self.character, "disableMoving", u"不要走动", setting.ActionSetting)
        super(ActionMenu, self).show()


class DialogMenu(QtGui.QMenu):
    def __init__(self, character, list):
        super(DialogMenu, self).__init__()
        self.character = character
        self.unconscious = ""
        result = ""
        for line in list:
            result += fileRead.fileReadStr(line, "unconscious")
        result = result.split(":")

        self.unconscious = result[1]
        self.addAction(PlayerAction(self, self.character, "unconscious", result[0].strip(),
                                    setting.ActionSetting, result[1].strip()))
        for reaction in setting.reactionList:
            result = ""
            for line in list:
                result += fileRead.fileReadStr(line, reaction)
            if result:
                result = result.split(":")
                self.addAction(PlayerAction(self, self.character, reaction, result[0].strip(),
                                            setting.ActionSetting, result[1].strip()))

    def posShow(self, pos):
        self.move(pos)
        super(DialogMenu, self).show()


class Sentence:
    def __init__(self, sentence):
        self.condition = {}
        self.goto = ""
        self.context = sentence
        self.icon = ""
        self.sound = ""
        if self.context.find("@") > 0:
            self.icon = "res//image//%s.png" % self.context.split("@")[0].strip()
            self.context = self.context.split("@")[1].strip()
        if self.context.find("^") > 0:
            self.sound = "res//sound//%s.wav" % self.context.split("^")[0].strip()
            self.context = self.context.split("^")[1].strip()
        if self.context.find("|") > 0:
            condition = self.context.split("|")[0].split('&')
            self.context = self.context.split("|")[1].strip()
            for line in condition:
                for variable in setting.variable.keys():
                    if line.find(variable) > -1:
                        self.condition[variable] = fileRead.fileReadStr(line, variable)
        if self.context.find(":") > 0:
            self.goto = self.context.split(":")[1].strip()
            self.context = self.context.split(":")[0].strip()


class Stating:
    def __init__(self, name, list):
        self.name = name
        self.context = {}
        self.settingContext(list)

    def settingContext(self, list):
        for relation in setting.relationList:
            self.context[relation] = fileRead.listReadLines("_%s_" % relation, "_end_", list)
            if (self.context[relation] == []):
                self.context[relation] = self.context[setting.relationTree[relation]]
            else:
                for i in range(len(self.context[relation])):
                    self.context[relation][i] = Sentence(self.context[relation][i])

    def showSentence(self, relation):
        readyList = []
        for sentence in self.context[relation]:
            success = True
            for variable in setting.variable.keys():
                if variable in sentence.condition.keys():
                    if sentence.condition[variable] != setting.variable[variable]:
                        success = False
                        break
            if (success):
                readyList.append(sentence)
        num = random.randrange(len(readyList))
        result = readyList[num].context
        goto = readyList[num].goto
        icon = readyList[num].icon
        sound = readyList[num].sound
        return result, goto, icon, sound


class Language:
    def __init__(self, character):
        file = open("res//text//talk.txt")
        self.talkfile = fileRead.fileToList(file)
        file.close()
        file = open("res//text//function.txt")
        self.funcfile = fileRead.fileToList(file)
        file.close()
        self.stating = {}
        self.dialogMenu = {}
        self.currentMenu = None
        self.currentMessage = "", "", "", ""
        self.nextMessage = "", "", "", ""
        self.currentState = ""
        self.nextState = ""
        self.character = character
        self.initialize()
        self.fadeOutTime = 0

    def replaceText(self, line):
        line = line.replace("_TIMEPERIOD_", setting.getTimePeriod())
        line = line.replace("_CALLING_", setting.text_calling)
        line = line.replace("\\", "\n")
        for define in self.outerDefine.keys():
            line = line.replace("_%s_" % define, self.outerDefine[define])
        return line

    def initialize(self):
        context = fileRead.listReadAllLines("====================talk====================",
                                            "====================talk====================", self.talkfile)
        for list in context:
            name = fileRead.fileReadStr(list[0], "state")
            self.stating[name] = Stating(name, list)
        reaction = fileRead.listReadAllLines("====================func====================",
                                             "====================func====================", self.funcfile)
        for list in reaction:
            name = fileRead.fileReadStr(list[0], "state")
            self.dialogMenu[name] = list
        self.outerDefine = fileRead.fileReadVariable("res//text//define.txt")

    def showSpeakTime(self):
        return setting.showSpeakTime(self.showMessage())

    def showMessage(self):
        return self.replaceText(self.currentMessage[0])

    def showState(self):
        return self.currentState

    def showGoto(self):
        return self.currentMessage[1]

    def showFace(self):
        return self.currentMessage[2]

    def showSound(self):
        return self.currentMessage[3]

    def swap(self):
        self.currentMessage = self.nextMessage
        self.currentState = self.nextState
        print(self.currentMessage)
        if self.currentMessage[1]:
            self.currentMenu = DialogMenu(self.character, self.dialogMenu[self.currentMessage[1]])
        else:
            self.currentMenu = None
        if self.currentMessage[3]:
            self.character.soundThread.swap(self.currentMessage[3])
        if self.currentMenu:
            self.setNextMessage(self.currentMenu.unconscious, 0)
        else:
            self.setNextMessage("", 0)

    def showFadeOutTime(self):
        if self.fadeOutTime:
            t = self.fadeOutTime
            self.fadeOutTime = 0
            return t
        else:
            return self.showSpeakTime()

    def setNextText(self, text, fadeOutTime):
        if text:
            self.nextMessage = text, "", "", ""
            self.nextState = ""
            self.fadeOutTime = fadeOutTime

    def setNextMessage(self, name, fadeOutTime):
        if name:
            if name in self.stating.keys():
                self.nextMessage = self.stating[name].showSentence(self.character.mood.relation)
                self.nextState = name
                self.fadeOutTime = fadeOutTime
        else:
            self.nextMessage = "", "", "", ""
            self.nextState = ""
            self.fadeOutTime = fadeOutTime


class Mood:
    def __init__(self):
        self.familiar = 0.0
        self.friendship = 0.0
        self.love = 0.0
        self.fear = 0.0
        self.hate = 0.0

        self.happy = 0.0
        self.angry = 0.0
        self.sorrow = 0.0
        self.horror = 0.0
        self.surprised = 0.0
        self.shyness = 0.0

        self.relation = "strange"
        self.emotion = "normal"

        self.tired = 0.0
        self.interest = 0.0
        self.stopMoving = False

    def showFace(self):
        return setting.emotionSetting(self)

    def initialize(self):
        self.happy = 0.0
        self.angry = 0.0
        self.sorrow = 0.0
        self.horror = 0.0
        self.surprised = 0.0
        self.tired = 0.0
        self.interest = 1.0
        self.stopMoving = False

    def update(self):
        setting.moodUpdate(self)

    def posWalkSpeed(self):
        speed = (50 - self.tired) / 100 * (self.angry + self.happy + 20) / (
                self.sorrow + self.horror + self.surprised + 20)
        speed = min(1.2, speed)
        speed = max(0.8, speed)
        return speed

    def animeWalkSpeed(self):
        posSpeed = self.posWalkSpeed()
        posSpeed = min(1.1, posSpeed)
        posSpeed = max(0.9, posSpeed)
        return posSpeed

    def changeDirectionChance(self):
        chance = 0.1
        chance = min(1.0, chance)
        chance = max(0.1, chance)
        return chance

    def moveChance(self):
        chance = (50 - self.tired) / 100 * self.happy * self.angry / self.horror / self.sorrow
        chance = min(0.5, chance)
        chance = max(0.0, chance)
        return chance

    def stopChance(self):
        chance = 1 / (0.1 + self.moveChance())
        chance = min(1.0, chance)
        chance = max(0.5, chance)
        return chance

    def chatChance(self):
        chance = (self.interest + 1.0) * self.happy / 20.0 / self.angry / self.horror / self.sorrow
        chance = min(1.0, chance)
        chance = max(0.0, chance)
        return chance


class Spirit(QtGui.QLabel):
    def __init__(self, character, parent=None, f=0):
        super(Spirit, self).__init__(parent, f)

        file = open("res//text//config.txt", "r")
        list = file.readlines()
        file.close()
        self.animeWalkSpeed = fileRead.listReadInt(list, "animeWalkSpeed")
        self.posWalkSpeed = fileRead.listReadInt(list, "posWalkSpeed")
        self.chatChance = fileRead.listReadFloat(list, "chatChance")
        self.changeDirectionChance = fileRead.listReadFloat(list, "changeDirectionChance")
        self.moveChance = fileRead.listReadFloat(list, "moveChance")
        self.stopChance = fileRead.listReadFloat(list, "stopChance")
        self.frameRawNum = fileRead.listReadInt(list, "frameRawNum")
        self.standFrame = fileRead.actionFrameSetting(list, "standFrame")
        self.walkFrame = fileRead.actionFrameSetting(list, "walkFrame")
        self.headIconWidth = fileRead.listReadInt(list, "headIconWidth")
        self.headIconHeight = fileRead.listReadInt(list, "headIconHeight")
        self.dialogMargin = fileRead.listReadInt(list, "dialogMargin")
        self.dialogWidth = fileRead.listReadInt(list, "dialogWidth")
        self.dialogHeight = fileRead.listReadInt(list, "dialogHeight")
        self.fontFamily = fileRead.listReadStr(list, "fontFamily")
        self.fontSize = fileRead.listReadInt(list, "fontSize")
        self.fontColor = QtGui.QColor(fileRead.listReadInt(list, "fontRed"),
                                      fileRead.listReadInt(list, "fontGreen"),
                                      fileRead.listReadInt(list, "fontBlue"),
                                      fileRead.listReadInt(list, "fontAlpha"))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Widget | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.screen = QtGui.QDesktopWidget().rect()
        self.moveImage = FramePixmap(raw=self.frameRawNum)
        self.width = self.moveImage.imageWidth
        self.height = self.moveImage.imageHeight
        self.setPixmap(self.moveImage.frameImage(0, 0))
        self.resize(self.moveImage.imageWidth, self.moveImage.imageHeight)
        self.character = character
        self.character.timer.timeout.connect(self.update)
        self.moveDirectionList = [QtCore.QPoint(0, 1), QtCore.QPoint(-1, 0), QtCore.QPoint(1, 0), QtCore.QPoint(0, -1)]
        self.move(-200, 300)
        self.currentDirection = 1
        self.currentFrame = 0
        self.frameCount = 0
        self.nextDirection = 0
        self.destiny = QtCore.QPoint(100, 300)
        self.posDelta = 10
        self.timeCount = 0
        self.stand = False
        self.positionMove = True
        self.stopMoving = False
        self.exitFlag = False
        self.testActionMenu = ActionMenu(self.character)
        self.mouseOnPoint = None

    def positionMoveFunc(self):
        self.stand = False
        delta = self.destiny - self.pos()
        if delta.x() > self.posDelta:
            self.nextDirection = 2
        elif delta.x() < -self.posDelta:
            self.nextDirection = 1
        elif delta.y() > self.posDelta:
            self.nextDirection = 0
        elif delta.y() < -self.posDelta:
            self.nextDirection = 3
        else:
            self.nextDirection = 0
            self.stand = True
            self.positionMove = False
            if self.exitFlag:
                self.character.mainApplication.save()
                sys.exit(0)

    def randomDirection(self):
        check = random.random()
        if not self.character.dialog.playingMusic and check < self.character.mood.chatChance() * self.chatChance:
            self.character.dialog.chat()
            return
        check = random.random()
        if check < self.character.mood.changeDirectionChance() * self.changeDirectionChance:
            self.nextDirection = random.randrange(4)
        if self.stand:
            check = random.random()
            if check < self.character.mood.moveChance() * self.moveChance:
                self.stand = False
        else:
            check = random.random()
            if check < self.character.mood.stopChance() * self.stopChance:
                self.stand = True

    def mousePressEvent(self, event):
        self.character.activate()
        if event.button() == QtCore.Qt.LeftButton:
            self.mouseOnPoint = QtCore.QPoint(event.pos())
            self.stopMoving = True
        if event.button() == QtCore.Qt.RightButton and not self.exitFlag:
            self.testActionMenu.posShow(event.globalPos())
        if event.button() == QtCore.Qt.MiddleButton:
            self.character.dialog.chat()

    def mouseMoveEvent(self, event):
        if (self.mouseOnPoint):
            self.move(event.globalPos().x() - self.mouseOnPoint.x(), event.globalPos().y() - self.mouseOnPoint.y())
            self.character.dialog.posUpdate()

    def mouseReleaseEvent(self, event):
        self.mouseOnPoint = None
        self.stopMoving = False

    def centerPos(self):
        return self.pos() + QtCore.QPoint(self.width / 2, self.height / 2)

    def update(self):
        if not self.timeCount % 600:
            self.character.mainApplication.save()
        if not self.timeCount % 60:
            if self.character.isPlayingMusic():
                self.character.mood.tired += 2
            self.character.mood.update()
            if not (self.stopMoving or
                    self.character.dialog.standFlag or
                    self.testActionMenu.isVisible() or
                    self.positionMove or
                    self.character.mood.stopMoving):
                self.randomDirection()
        if (self.stopMoving or
                self.character.dialog.standFlag or
                self.testActionMenu.isVisible() or
                self.character.mood.stopMoving
                and not self.exitFlag):
            self.stand = True
            self.nextDirection = 0
        elif (self.positionMove):
            self.positionMoveFunc()
        if (self.exitFlag):
            self.destiny = QtCore.QPoint(-500, self.pos().y())
            self.positionMove = True
        self.timeCount += 1
        if (self.currentDirection == 0) and (self.nextDirection == 3):
            self.currentDirection = 1
        elif (self.currentDirection == 1) and (self.nextDirection == 2):
            self.currentDirection = 3
        elif (self.currentDirection == 2) and (self.nextDirection == 1):
            self.currentDirection = 0
        elif (self.currentDirection == 3) and (self.nextDirection == 0):
            self.currentDirection = 2
        else:
            self.currentDirection = self.nextDirection
        self.frameCount += 1
        if self.stand:
            frameList = self.standFrame
        else:
            frameList = self.walkFrame
        if self.frameCount > int(self.animeWalkSpeed / self.character.mood.animeWalkSpeed()):
            self.frameCount = 0
            self.currentFrame += 1
        if self.currentFrame >= len(frameList):
            self.currentFrame = 0
        self.setPixmap(self.moveImage.frameImage(frameList[self.currentFrame], self.currentDirection))
        if not self.stand:
            self.character.mood.tired += 0.1
            self.move(self.pos() +
                      self.posWalkSpeed * self.character.mood.posWalkSpeed() *
                      self.moveDirectionList[self.currentDirection])
            if self.pos().x() > self.screen.width() - self.width:
                self.nextDirection = 1
            if self.pos().y() > self.screen.height() - self.height:
                self.nextDirection = 3
            if self.pos().x() < 0:
                self.nextDirection = 2
            if self.pos().y() < 0:
                self.nextDirection = 0
        self.character.dialog.update()


class Dialog(QtGui.QWidget):
    def __init__(self, character, parent=None, f=0):
        super(Dialog, self).__init__(parent, f)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Widget | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(1.0)
        self.screen = QtGui.QDesktopWidget().rect()
        self.character = character
        self.iconWidth = self.character.spirit.headIconWidth
        self.iconHeight = self.character.spirit.headIconHeight
        self.margin = self.character.spirit.dialogMargin
        self.textWidth = self.character.spirit.dialogWidth
        self.textHeight = self.character.spirit.dialogHeight
        self.resize(self.textWidth, self.iconHeight + self.textHeight)
        self.Image = {"normal": 0,
                      "happy": 2,
                      "cheerful": 4,
                      "teasing": 6,
                      "sad": 8,
                      "surprised": 10,
                      "crying": 12,
                      "angry": 14}
        self.direction = 0
        self.directionPos = 0
        self.face = "normal"
        self.alpha = 0
        self.timeCount = 0
        self.character = character
        self.standFlag = False
        self.fadeOutTimeOut = 0
        self.speakTimeOut = 0
        self.hideFlag = False
        self.setWindowOpacity(self.alpha)
        self.setAcceptDrops(True)
        self.currentLyric = 0
        self.playingMusic = False
        self.lyric = 0
        self.show()

    def changeFace(self, face):
        if face in self.Image.keys():
            self.face = face

    def breakSpeak(self):
        self.funcBreakSpeak()
        setting.ActionSetting(self.character.mood, "break")

    def funcBreakSpeak(self):
        self.speakTimeOut = self.timeCount
        self.fadeOutTimeOut = self.timeCount

    def speak(self, name, fadeOutTime=0):
        self.character.language.setNextMessage(name, fadeOutTime)

    def chat(self):
        if self.character.language.currentState != "chat":
            self.speak("chat")

    def posUpdate(self):
        self.moveTo(self.character.spirit.centerPos())

    def talkUpdate(self):
        self.repaint()
        if self.character.isPlayingMusic() and self.lyric:
            self.playingMusic = True
            if self.character.musicThread.getTime() > self.lyric[self.currentLyric][0]:
                self.funcBreakSpeak()
                self.character.language.setNextText(self.lyric[self.currentLyric][1], 0)
                self.currentLyric += 1
                if self.currentLyric == len(self.lyric):
                    del self.lyric
                    self.lyric = 0
        else:
            self.playingMusic = False
        if self.character.language.currentState == "chat":
            self.standFlag = True
        elif self.character.language.currentState == "talk":
            self.standFlag = True
        else:
            self.standFlag = False
        if self.timeCount > self.fadeOutTimeOut:
            self.fadeOut()
        if self.timeCount > self.speakTimeOut:
            self.hideFlag = False
        if self.alpha < 0.1:
            if not self.hideFlag:
                self.character.language.swap()
                if self.character.language.currentMessage[0]:
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
            if self.alpha >= 1.0:
                self.alpha = 1.0
            else:
                self.alpha += 0.2
        else:
            if self.alpha <= 0.0:
                self.alpha = 0.0
            else:
                self.alpha -= 0.2

    def fadeIn(self):
        self.fadeFlag = 1

    def fadeOut(self):
        self.fadeFlag = 0

    def paintEvent(self, paintEvent):
        painter = QtGui.QPainter(self)
        if self.character.language.showFace():
            iconName = self.character.language.showFace()
        else:
            identity = self.Image[self.face] + self.direction
            iconName = "res//image//%s.png" % identity
        painter.drawPixmap(0, 0,
                           Pixmap(iconName).scaledToWidth(self.iconWidth, mode=QtCore.Qt.SmoothTransformation).copy(0,
                                                                                                                    0,
                                                                                                                    self.iconWidth,
                                                                                                                    self.iconHeight))
        rect = QtCore.QRect(0, self.iconHeight, self.textWidth, self.textHeight)
        painter.drawPixmap(rect, QtGui.QPixmap("res//image//dialog.png").scaled(rect.width(), rect.height()))
        textRect = QtCore.QRectF(rect.left() + 20, rect.top() + 20, self.textWidth - 40, 90)
        font = QtGui.QFont(unicode(self.character.spirit.fontFamily), self.character.spirit.fontSize)
        painter.setFont(font)
        painter.setPen(self.character.spirit.fontColor)
        message = self.character.language.showMessage()
        painter.drawText(textRect, unicode(message))

    def checkDirection(self):
        if self.centerPos().x() < (self.screen.width() / 2) and not self.direction:
            self.direction = 1
        elif self.centerPos().x() > (self.screen.width() / 2) and self.direction:
            self.direction = 0

    def centerPos(self):
        return self.pos() + QtCore.QPoint(self.iconWidth / 2, self.iconHeight / 2)

    def moveTo(self, pos):
        if (pos.x() + self.margin + self.iconWidth + self.textWidth) > self.screen.width():
            self.directionPos = 0
        elif (pos.x() - self.margin - self.iconWidth - self.textWidth) < 0:
            self.directionPos = 1
        y = max(20, pos.y() - self.character.spirit.height / 2 - self.iconHeight / 2)
        y = min(self.screen.height() - self.textHeight - self.iconHeight - 20, y)
        if self.directionPos:
            x = pos.x() + self.margin
        else:
            x = pos.x() - self.margin - self.textWidth
        self.move(x, y)
        self.checkDirection()

    def mousePressEvent(self, event):
        self.character.activate()
        if event.button() == QtCore.Qt.RightButton:
            if self.character.language.currentMenu:
                self.character.language.currentMenu.posShow(event.globalPos())
        else:
            self.hideFlag = True

    def dropEvent(self, event):
        name = event.mimeData().urls()[0].path()[1:]
        self.lyric = fileRead.lyricRead(name[:-3] + u'lrc')
        if self.lyric:
            self.currentLyric = 0
        if self.character.musicThread and self.character.musicThread.operation:
            self.character.musicThread.swapMusic(name)
        else:
            self.character.musicThread = MusicPlaying(name)

    def dragEnterEvent(self, event):
        name = event.mimeData().urls()[0].path()
        a = name.split('.')
        if a[-1].upper() == u'MP3' or a[-1].upper() == u'WAV':
            event.accept()


class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, character, parent=None):
        super(SystemTrayIcon, self).__init__(parent)
        self.character = character
        self.setIcon(QtGui.QIcon("res//image//headicon.png"))
        self.name = self.character.language.outerDefine["TRAY_NAME"]
        self.show()
        self.showMessage(unicode(self.name), unicode(self.character.language.outerDefine["WELCOMING_TEXT"]))
        self.setToolTip(unicode(self.character.language.outerDefine["TRAY_TOOL_TIPS"]))
        self.activated.connect(self.clickMessage)
        self.menu = QtGui.QMenu()
        self.setContextMenu(self.menu)

    def clickMessage(self, message):
        if (message == self.Trigger):
            self.showMessage(unicode(self.name), unicode(self.character.language.outerDefine["CLICK_TEXT"]))
            self.character.activate()


class Character:
    def __init__(self, timer, mainApplication):
        self.timer = timer
        self.spirit = Spirit(self)
        self.dialog = Dialog(self)
        self.language = Language(self)
        self.mood = Mood()
        self.soundThread = SoundPlaying()
        self.musicThread = None
        self.mainApplication = mainApplication
        self.activate()

    def activate(self):
        self.spirit.activateWindow()
        self.spirit.raise_()
        self.dialog.activateWindow()
        self.dialog.raise_()

    def exiting(self, h1=None, h2=None):
        self.mainApplication.save()
        self.spirit.exitFlag = True
        if self.musicThread:
            self.musicThread.endPlay()
        self.dialog.funcBreakSpeak()
        self.dialog.setAcceptDrops(False)
        return "exit"

    def isPlayingMusic(self):
        if (self.musicThread and
                self.musicThread.operation and not
                (self.musicThread.pauseFlag or
                 self.musicThread.stopFlag or
                 self.musicThread.swapFlag)):
            return True
        else:
            return False


class FirstDialog(QtGui.QDialog):
    def __init__(self, mainApp):
        super(FirstDialog, self).__init__()
        self.ui = ui_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Widget | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(True)
        self.ui.textEdit.setAlignment(QtCore.Qt.AlignVCenter)
        self.mainApp = mainApp

    def paintEvent(self, paintEvent):
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QBrush(QtGui.QImage("res//image//dialog.png").scaled(self.size())))
        # painter.setBackground(QtGui.QBrush(QtCore.Qt.gray))
        painter.drawRect(self.rect())

    def accept(self):
        setting.text_calling = self.ui.textEdit.toPlainText()
        setting.text_calling = str(setting.text_calling.strip())
        if not setting.text_calling:
            setting.text_calling = u"……"
        super(FirstDialog, self).accept()

    def reject(self):
        sys.exit(0)
        super(FirstDialog, self).reject()


class DebugWindow(QtGui.QDialog):
    def __init__(self, character):
        super(DebugWindow, self).__init__()
        self.character = character
        self.ui = ui_debugWindow.Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.familiarText.setNum(self.character.mood.familiar)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def setText(self):
        self.ui.familiarText.setNum(self.character.mood.familiar)
        self.ui.angryText.setNum(self.character.mood.angry)
        self.ui.fearText.setNum(self.character.mood.fear)
        self.ui.friendshipText.setNum(self.character.mood.friendship)
        self.ui.happyText.setNum(self.character.mood.happy)
        self.ui.hateText.setNum(self.character.mood.hate)
        self.ui.horrorText.setNum(self.character.mood.horror)
        self.ui.loveText.setNum(self.character.mood.love)
        self.ui.shynessText.setNum(self.character.mood.shyness)
        self.ui.sorrowText.setNum(self.character.mood.sorrow)
        self.ui.surprisedText.setNum(self.character.mood.surprised)
        self.ui.tiredText.setNum(self.character.mood.tired)


class MainApplication:
    def __init__(self):
        self.timer = QtCore.QTimer()
        self.character = Character(self.timer, self)
        self.systemTrayIcon = SystemTrayIcon(self.character)
        self.debugWindow = DebugWindow(self.character)
        self.timer.start(int(1000 / 30))
        self.timer.timeout.connect(self.debugWindow.setText)
        self.character.spirit.show()
        self.actionSetting()
        self.load()
        self.character.mood.update()
        self.character.dialog.speak("start")

    def __del__(self):
        self.save()

    def actionSetting(self):
        self.onTopAction = QtGui.QAction("人物始\n终可见", self.systemTrayIcon)
        self.onTopAction.setToolTip("置顶")
        self.onTopAction.setCheckable(True)
        self.onTopAction.changed.connect(self.settingOnTop)
        self.debugAction = QtGui.QAction("*debug*显示情绪监控窗口", self.systemTrayIcon)
        self.debugAction.setCheckable(True)
        self.debugAction.changed.connect(self.showDebugWindow)
        self.exitAction = QtGui.QAction("再见啦", self.systemTrayIcon)
        self.exitAction.setToolTip("退出")
        self.exitAction.triggered.connect(self.exiting)
        self.systemTrayIcon.menu.addAction(self.onTopAction)
        self.systemTrayIcon.menu.addAction(self.debugAction)
        self.systemTrayIcon.menu.addAction(self.exitAction)

    def showDebugWindow(self):
        if self.debugAction.isChecked():
            self.debugWindow.show()
        else:
            self.debugWindow.hide()

    def settingOnTop(self):
        if (self.onTopAction.isChecked()):
            self.character.spirit.hide()
            self.character.dialog.hide()
            self.character.spirit.setWindowFlags(
                QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
            self.character.dialog.setWindowFlags(
                QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
            self.character.spirit.show()
            self.character.dialog.show()
        else:
            self.character.spirit.hide()
            self.character.dialog.hide()
            self.character.spirit.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Widget | QtCore.Qt.Tool)
            self.character.dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Widget | QtCore.Qt.Tool)
            self.character.spirit.show()
            self.character.dialog.show()

    def save(self):
        print("saving")
        saveFile = open("sav//sav.dat", "wb")
        pickle.dump((self.character.mood, self.onTopAction.isChecked(), setting.text_calling), saveFile)
        saveFile.close()

    def load(self):
        try:
            loadFile = open("sav//sav.dat", "rb")
            self.character.mood, onTop, setting.text_calling = pickle.load(loadFile)
            self.character.mood.initialize()
            self.onTopAction.setChecked(onTop)
            loadFile.close()
        except:
            self.character.spirit.stopMoving = True
            self.initialize()
            self.character.spirit.stopMoving = False
            self.character.dialog.speak("start")

    def initialize(self):
        firstdialog = FirstDialog(self)
        firstdialog.show()
        firstdialog.exec_()

    def exiting(self):
        self.character.spirit.exitFlag = True
        self.character.dialog.speak("exit")
        self.character.dialog.funcBreakSpeak()


def main():
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainApplication()
    app.exec_()


if __name__ == "__main__":
    main()
