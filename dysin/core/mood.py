# -*- coding:utf-8 -*-
"""Character mood / emotion system."""
from dysin.core import setting


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
