# -*- coding:utf-8 -*-
"""Dialogue / language system: Sentence, Stating, Language."""
from dysin.core.config import IMAGE_DIR, SOUND_DIR
from dysin.core.yaml_handler import YamlLoader
from dysin.ui.menu import DialogMenu
from dysin.core import setting


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
                    if cond.find(variable) > -1:
                        val = cond.split('=')[1].strip() if '=' in cond else ''
                        self.condition[variable] = val
        if self.context.find(':') > 0:
            self.goto = self.context.split(':')[1].strip()
            self.context = self.context.split(':')[0].strip()


class Stating:
    def __init__(self, name, yaml_loader):
        self.name = name
        self.yaml_loader = yaml_loader

    def showSentence(self, relation):
        text, goto, icon, sound = self.yaml_loader.get_weighted_dialogue(self.name, relation)
        return text, goto, icon, sound


class Language:
    def __init__(self, character):
        self.talkfile = []
        self.funcfile = []
        self.stating = {}; self.dialogMenu = {}; self.currentMenu = None
        self.currentMessage = ('', '', '', ''); self.nextMessage = ('', '', '', '')
        self.currentState = ''; self.nextState = ''; self.character = character
        self.initialize(); self.fadeOutTime = 0

    def replaceText(self, line):
        line = line.replace('{{TIMEPERIOD}}', setting.getTimePeriod())
        line = line.replace('{{CALLING}}', setting.text_calling)
        line = line.replace('\\n', '\n')
        for define_key in self.outerDefine.keys():
            line = line.replace('{{' + define_key + '}}', str(self.outerDefine[define_key]))
        return line

    def initialize(self):
        self.yaml_loader = YamlLoader()
        dialogue = self.yaml_loader.dialogue
        for state_name in dialogue.get('states', {}).keys():
            self.stating[state_name] = Stating(state_name, self.yaml_loader)
        func_data = self.yaml_loader.function.get('states', {})
        for state_name, reactions in func_data.items():
            self.dialogMenu[state_name] = reactions
        if hasattr(self.yaml_loader, 'outer_define'):
            self.outerDefine = self.yaml_loader.outer_define

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
