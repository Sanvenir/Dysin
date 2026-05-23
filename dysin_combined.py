# -*- coding:utf-8 -*-
"""Dysin - 妗岄潰绮剧伒绋嬪簭 Python 3 + PySide6"""


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
        speed = (50 - self.tired) / 100 * (self.angry + self.happy + 20) / (self.sorrow + self.horror + self.surprised + 20)
        return max(0.8, min(1.2, speed))

    def animeWalkSpeed(self):
        return max(0.9, min(1.1, self.posWalkSpeed()))

    def changeDirectionChance(self):
        return 0.1

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

        config_path = TEXT_DIR / "config.txt"
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config_list = file.readlines()
            self.animeWalkSpeed = fileRead.listReadInt(config_list, "animeWalkSpeed")
            self.posWalkSpeed = fileRead.listReadInt(config_list, "posWalkSpeed")
            self.chatChance = fileRead.listReadFloat(config_list, "chatChance")
            self.changeDirectionChance = fileRead.listReadFloat(config_list, "changeDirectionChance")
            self.moveChance = fileRead.listReadFloat(config_list, "moveChance")
            self.stopChance = fileRead.listReadFloat(config_list, "stopChance")
            self.frameRawNum = fileRead.listReadInt(config_list, "frameRawNum")
            self.standFrame = fileRead.actionFrameSetting(config_list, "standFrame")
            self.walkFrame = fileRead.actionFrameSetting(config_list, "walkFrame")
            self.headIconWidth = fileRead.listReadInt(config_list, "headIconWidth")
            self.headIconHeight = fileRead.listReadInt(config_list, "headIconHeight")
            self.dialogMargin = fileRead.listReadInt(config_list, "dialogMargin")
            self.dialogWidth = fileRead.listReadInt(config_list, "dialogWidth")
            self.dialogHeight = fileRead.listReadInt(config_list, "dialogHeight")
            self.fontFamily = fileRead.listReadStr(config_list, "fontFamily")
            self.fontSize = fileRead.listReadInt(config_list, "fontSize")
            self.fontColor = QColor(
                fileRead.listReadInt(config_list, "fontRed"),
                fileRead.listReadInt(config_list, "fontGreen"),
                fileRead.listReadInt(config_list, "fontBlue"),
                fileRead.listReadInt(config_list, "fontAlpha")
            )
        except:
            self.animeWalkSpeed = 5
            self.posWalkSpeed = 10
            self.chatChance = 0.1
            self.changeDirectionChance = 0.1
            self.moveChance = 0.3
            self.stopChance = 0.7
            self.frameRawNum = 4
            self.standFrame = [0, 1, 2, 3]
            self.walkFrame = [0, 1, 2, 3]
            self.headIconWidth = 80
            self.headIconHeight = 80
            self.dialogMargin = 10
            self.dialogWidth = 300
            self.dialogHeight = 100
            self.fontFamily = "瀹嬩綋"
            self.fontSize = 12
            self.fontColor = QColor(0, 0, 0, 255)
        self.animeWalkSpeed *= 3  # 60fps tick scaling

        self.screen = QDesktopWidget().geometry()
        move_png = str(IMAGE_DIR / "move.png")
        if os.path.exists(move_png):
            self.moveImage = FramePixmap(move_png, raw=self.frameRawNum)
        else:
            self.moveImage = FramePixmap(None, raw=self.frameRawNum)

        self.width = self.moveImage.imageWidth
        self.height = self.moveImage.imageHeight
        self.setPixmap(self.moveImage.frameImage(0, 0))
        self.resize(self.moveImage.imageWidth, self.moveImage.imageHeight)

        self.character = character
        self.moveDirectionList = [QPoint(0, 1), QPoint(-1, 0), QPoint(1, 0), QPoint(0, -1)]
        self.move(-200, 300)
        self.currentDirection = 1
        self.currentFrame = 0
        self.frameCount = 0
        self.nextDirection = 0
        self.destiny = QPoint(100, 300)
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
        if not self.character.isPlayingMusic() and check < self.character.mood.chatChance() * self.chatChance:
            self.character.dialog.chat()
            return

        check = random.random()
        if check < self.character.mood.changeDirectionChance() * self.changeDirectionChance:
            self.nextDirection = random.randrange(4)

        if self.stand:
            if random.random() < self.character.mood.moveChance() * self.moveChance:
                self.stand = False
        else:
            if random.random() < self.character.mood.stopChance() * self.stopChance:
                self.stand = True

    def mousePressEvent(self, event):
        self.character.activate()
        if event.button() == Qt.LeftButton:
            self.mouseOnPoint = QPoint(event.pos())
            self.stopMoving = True
        if event.button() == Qt.RightButton and not self.exitFlag:
            self.testActionMenu.posShow(event.globalPos())
        if event.button() == Qt.MiddleButton:
            self.character.dialog.chat()

    def mouseMoveEvent(self, event):
        if self.mouseOnPoint:
            self.move(event.globalPos().x() - self.mouseOnPoint.x(),
                     event.globalPos().y() - self.mouseOnPoint.y())
            self.character.dialog.posUpdate()

    def mouseReleaseEvent(self, event):
        self.mouseOnPoint = None
        self.stopMoving = False

    def centerPos(self):
        return self.pos() + QPoint(self.width // 2, self.height // 2)

    def update(self):
        if not self.timeCount % 1800:
            self.character.mainApplication.save()

        if not self.timeCount % 180:
            if self.character.isPlayingMusic():
                self.character.mood.tired += 2
            self.character.mood.update()
            if not (self.stopMoving or self.character.dialog.standFlag or
                    self.testActionMenu.isVisible() or self.positionMove or
                    self.character.mood.stopMoving):
                self.randomDirection()

        if (self.stopMoving or self.character.dialog.standFlag or
            self.testActionMenu.isVisible() or self.character.mood.stopMoving) and not self.exitFlag:
            self.stand = True
            self.nextDirection = 0
        elif self.positionMove:
            self.positionMoveFunc()

        if self.exitFlag:
            self.destiny = QPoint(-500, self.pos().y())
            self.positionMove = True

        self.timeCount += 1

        direction_map = {(0, 3): 1, (1, 2): 3, (2, 1): 0, (3, 0): 2}
        key = (self.currentDirection, self.nextDirection)
        self.currentDirection = direction_map.get(key, self.nextDirection)

        self.frameCount += 1
        frameList = self.standFrame if self.stand else self.walkFrame
        if self.frameCount > int(self.animeWalkSpeed / max(0.1, self.character.mood.animeWalkSpeed())):
            self.frameCount = 0
            self.currentFrame += 1
        if self.currentFrame >= len(frameList):
            self.currentFrame = 0

        self.setPixmap(self.moveImage.frameImage(frameList[self.currentFrame], self.currentDirection))

        if not self.stand:
            self.character.mood.tired += 0.03
            self.move(self.pos() + int(self.posWalkSpeed * self.character.mood.posWalkSpeed() / 3) *
                      self.moveDirectionList[self.currentDirection])
            sw, sh = self.screen.width(), self.screen.height()
            if self.pos().x() > sw - self.width:
                self.nextDirection = 1
            if self.pos().y() > sh - self.height:
                self.nextDirection = 3
            if self.pos().x() < 0:
                self.nextDirection = 2
            if self.pos().y() < 0:
                self.nextDirection = 0

        self.character.dialog.update()
# -*- coding:utf-8 -*-
"""Dysin - 妗岄潰绮剧伒绋嬪簭 Python 3 + PySide6 - Part 3"""


class Dialog(QWidget):
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(1.0)
        self.screen = QDesktopWidget().geometry()
        self.character = character
        self.iconWidth = self.character.spirit.headIconWidth
        self.iconHeight = self.character.spirit.headIconHeight
        self.margin = self.character.spirit.dialogMargin
        self.textWidth = self.character.spirit.dialogWidth
        self.textHeight = self.character.spirit.dialogHeight
        self.resize(self.textWidth, self.iconHeight + self.textHeight)
        self.Image = {
            "normal": 0, "happy": 2, "cheerful": 4, "teasing": 6,
            "sad": 8, "surprised": 10, "crying": 12, "angry": 14
        }
        self.direction = 0
        self.directionPos = 0
        self.face = "normal"
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
        if self.character.language.showState() != "chat":
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
                    self.lyric = 0
        else:
            self.playingMusic = False

        if self.character.language.showState() in ("chat", "talk"):
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
        if self.character.language.showFace():
            iconName = self.character.language.showFace()
        else:
            iconName = str(IMAGE_DIR / f"{self.Image[self.face] + self.direction}.png")
        iconPixmap = QPixmap(iconName)
        if not iconPixmap.isNull():
            scaledIcon = iconPixmap.scaledToWidth(self.iconWidth, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaledIcon.copy(0, 0, self.iconWidth, self.iconHeight))

        rect = QRect(0, self.iconHeight, self.textWidth, self.textHeight)
        dialogPixmap = QPixmap(str(IMAGE_DIR / "dialog.png"))
        if not dialogPixmap.isNull():
            painter.drawPixmap(rect, dialogPixmap.scaled(rect.size()))

        textRect = QRectF(rect.left() + 20, rect.top() + 20, self.textWidth - 40, 90)
        font = QFont(self.character.spirit.fontFamily, self.character.spirit.fontSize)
        painter.setFont(font)
        painter.setPen(self.character.spirit.fontColor)
        painter.drawText(textRect, self.character.language.showMessage())

    def checkDirection(self):
        if self.centerPos().x() < (self.screen.width() // 2) and not self.direction:
            self.direction = 1
        elif self.centerPos().x() > (self.screen.width() // 2) and self.direction:
            self.direction = 0

    def centerPos(self):
        return self.pos() + QPoint(self.iconWidth // 2, self.iconHeight // 2)

    def moveTo(self, pos):
        if (pos.x() + self.margin + self.iconWidth + self.textWidth) > self.screen.width():
            self.directionPos = 0
        elif (pos.x() - self.margin - self.iconWidth - self.textWidth) < 0:
            self.directionPos = 1

        y = max(20, min(
            self.screen.height() - self.textHeight - self.iconHeight - 20,
            pos.y() - self.character.spirit.height // 2 - self.iconHeight // 2
        ))
        x = pos.x() + self.margin if self.directionPos else pos.x() - self.margin - self.textWidth
        self.move(x, y)
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
        super().__init__(parent)
        self.character = character
        iconPath = str(IMAGE_DIR / "headicon.png")
        if os.path.exists(iconPath):
            self.setIcon(QIcon(iconPath))
        if hasattr(self.character.language, 'outerDefine'):
            outerDefine = self.character.language.outerDefine
            self.name = outerDefine.get("TRAY_NAME", "Dysin")
            self.showMessage(str(self.name), str(outerDefine.get("WELCOMING_TEXT", "Hello!")))
            self.setToolTip(str(outerDefine.get("TRAY_TOOL_TIPS", "Dysin")))
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
                self.showMessage(
                    str(self.name),
                    str(self.character.language.outerDefine.get("CLICK_TEXT", "Click!"))
                )
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
        return "exit"

    def isPlayingMusic(self):
        return bool(
            self.musicThread and
            self.musicThread.operation and
            not (self.musicThread.pauseFlag or
                 self.musicThread.stopFlag or
                 self.musicThread.swapFlag)
        )


class FirstDialog(QDialog):
    def __init__(self, mainApp):
        super().__init__()
        self.mainApp = mainApp
        self.initUI()

    def initUI(self):
        self.setWindowTitle("鍒濇瑙侀潰")
        self.setWindowFlags(Qt.Window | Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        layout = QVBoxLayout()

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setPlainText("鍒濇瑙侀潰锛岃鍛婅瘔鎴戜綘鐨勫悕瀛楋細")
        layout.addWidget(self.textEdit)

        self.nameEdit = QTextEdit()
        self.nameEdit.setMaximumHeight(50)
        layout.addWidget(self.nameEdit)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

        self.setLayout(layout)
        self.resize(400, 300)

    def accept(self):
        name = self.nameEdit.toPlainText().strip()
        if name:
            self.mainApp.saveName(name)
        super().accept()

    def reject(self):
        super().reject()


class DebugWindow(QDialog):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Debug")
        self.resize(600, 400)

        layout = QVBoxLayout()

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        layout.addWidget(self.textEdit)

        buttonLayout = QHBoxLayout()
        refreshBtn = QDialogButtonBox()
        refreshBtn.addButton("鍒锋柊", QDialogButtonBox.ActionRole)
        refreshBtn.addButton("鍏抽棴", QDialogButtonBox.RejectRole)
        refreshBtn.button(QDialogButtonBox.ActionRole).clicked.connect(self.refresh)
        refreshBtn.button(QDialogButtonBox.RejectRole).clicked.connect(self.close)
        buttonLayout.addWidget(refreshBtn)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        mood = self.character.mood
        text = f"""Mood Stats:
- familiar: {mood.familiar}
- friendship: {mood.friendship}
- love: {mood.love}
- fear: {mood.fear}
- hate: {mood.hate}
- happy: {mood.happy}
- angry: {mood.angry}
- sorrow: {mood.sorrow}
- horror: {mood.horror}
- surprised: {mood.surprised}
- shyness: {mood.shyness}
- relation: {mood.relation}
- emotion: {mood.emotion}
- tired: {mood.tired}
- interest: {mood.interest}
- stopMoving: {mood.stopMoving}

Variables:
"""
        for key, value in setting.variable.items():
            text += f"- {key}: {value}\n"

        self.textEdit.setPlainText(text)


class MainApplication:
    def __init__(self):
        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)

        self.timer = QTimer()
        self.timer.start(16)

        self.character = Character(self.timer, self)
        self.debugWindow = None

        self.trayIcon = SystemTrayIcon(self.character)
        self.trayIcon.setVisible(True)

        self.firstDialog = FirstDialog(self)
        if self.firstDialog.exec() == QDialog.Accepted:
            self.load()
        else:
            sys.exit(0)

        self.timer.timeout.connect(self.character.spirit.update)
        self.character.dialog.show()
        self.character.spirit.show()

    def load(self):
        SAV_DIR.mkdir(exist_ok=True)
        savFile = SAV_DIR / "sav.dat"
        if savFile.exists():
            try:
                with open(savFile, 'rb') as f:
                    data = pickle.load(f)
                self.loadData(data)
            except:
                pass

    def loadData(self, data):
        if 'mood' in data:
            mood_data = data['mood']
            for key in dir(self.character.mood):
                if not key.startswith('_') and key in mood_data:
                    setattr(self.character.mood, key, mood_data[key])
        if 'variable' in data:
            for key, value in data['variable'].items():
                if key in setting.variable:
                    setting.variable[key] = value
        if 'name' in data:
            setting.text_calling = data['name']

    def save(self):
        SAV_DIR.mkdir(exist_ok=True)
        savFile = SAV_DIR / "sav.dat"
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
            with open(savFile, 'wb') as f:
                pickle.dump(data, f)
        except:
            pass

    def saveName(self, name):
        setting.text_calling = name
        self.save()

    def run(self):
        return self.app.exec()


if __name__ == "__main__":
    app = MainApplication()
    sys.exit(app.run())
