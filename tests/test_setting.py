# -*- coding:utf-8 -*-
"""Tests for setting module."""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import setting
from setting import (
    getTimePeriod, showSpeakTime, moodInit,
    ActionSetting, emotionSetting, relationSetting
)


class MockMood:
    """Mock Mood object for testing."""
    def __init__(self):
        self.familiar = 50.0
        self.friendship = 50.0
        self.love = 50.0
        self.fear = 50.0
        self.hate = 50.0
        self.happy = 5.0
        self.angry = 5.0
        self.sorrow = 5.0
        self.horror = 5.0
        self.surprised = 5.0
        self.shyness = 5.0
        self.relation = "normal"
        self.emotion = "normal"
        self.tired = 50.0
        self.interest = 1.0
        self.stopMoving = False


class TestGetTimePeriod:
    def test_getTimePeriod_night(self, mocker):
        """测试夜间时段 (23:00-05:00)"""
        mocker.patch('time.strftime', return_value='03')
        assert getTimePeriod() == "深夜"

    def test_getTimePeriod_morning(self, mocker):
        """测试早晨时段 (05:00-08:00)"""
        mocker.patch('time.strftime', return_value='06')
        assert getTimePeriod() == "早上"

    def test_getTimePeriod_forenoon(self, mocker):
        """测试上午时段 (08:00-10:00)"""
        mocker.patch('time.strftime', return_value='09')
        assert getTimePeriod() == "上午"

    def test_getTimePeriod_noon(self, mocker):
        """测试中午时段 (10:00-12:00)"""
        mocker.patch('time.strftime', return_value='11')
        assert getTimePeriod() == "中午"

    def test_getTimePeriod_afternoon(self, mocker):
        """测试下午时段 (12:00-18:00)"""
        mocker.patch('time.strftime', return_value='15')
        assert getTimePeriod() == "下午"

    def test_getTimePeriod_evening(self, mocker):
        """测试晚间时段 (18:00-23:00)"""
        mocker.patch('time.strftime', return_value='20')
        assert getTimePeriod() == "晚上"


class TestShowSpeakTime:
    def test_showSpeakTime_basic(self):
        assert showSpeakTime("hello") == 5 * 5 + 20

    def test_showSpeakTime_empty(self):
        assert showSpeakTime("") == 20

    def test_showSpeakTime_long(self):
        text = "a" * 100
        assert showSpeakTime(text) == 5 * 100 + 20


class TestMoodInit:
    def test_moodInit_clamps_values(self):
        mood = MockMood()
        mood.happy = 25.0
        mood.angry = 25.0
        moodInit(mood)
        # 应该被 clamp 到最大值 20.0
        assert mood.happy == 20.0
        assert mood.angry == 20.0

    def test_moodInit_clamps_min(self):
        mood = MockMood()
        mood.love = 0.5
        mood.fear = 0.5
        moodInit(mood)
        # 应该被 clamp 到最小值 1.0
        assert mood.love == 1.0
        assert mood.fear == 1.0

    def test_moodInit_interest_bounds(self):
        mood = MockMood()
        mood.interest = 2.0
        moodInit(mood)
        assert mood.interest == 1.0

        mood.interest = -2.0
        moodInit(mood)
        assert mood.interest == -1.0


class TestActionSetting:
    def test_actionSetting_talk(self):
        mood = MockMood()
        mood.interest = 1.0
        mood.happy = 5.0
        result = ActionSetting(mood, "talk")
        assert result == "talk"
        assert mood.interest == 0.0

    def test_actionSetting_touch_good(self):
        mood = MockMood()
        mood.friendship = 60.0
        mood.hate = 0.0
        mood.angry = 3.0
        mood.happy = 5.0
        result = ActionSetting(mood, "touch")
        assert result == "goodTouch"
        assert mood.happy > 5.0

    def test_actionSetting_touch_bad(self):
        mood = MockMood()
        mood.friendship = 10.0
        mood.hate = 50.0
        mood.angry = 10.0
        mood.happy = 5.0
        result = ActionSetting(mood, "touch")
        assert result == "badTouch"
        assert mood.happy < 5.0

    def test_actionSetting_break(self):
        mood = MockMood()
        mood.happy = 5.0
        mood.angry = 3.0
        result = ActionSetting(mood, "break")
        assert result == "break"
        assert mood.angry > 3.0

    def test_actionSetting_positive(self):
        mood = MockMood()
        mood.happy = 5.0
        mood.angry = 5.0
        result = ActionSetting(mood, "positive")
        assert result == "positive"
        assert mood.happy > 5.0
        assert mood.angry < 5.0

    def test_actionSetting_negative(self):
        mood = MockMood()
        mood.happy = 5.0
        result = ActionSetting(mood, "negative")
        assert result == "negative"
        assert mood.happy < 5.0

    def test_actionSetting_disableMoving(self):
        mood = MockMood()
        mood.stopMoving = False
        ActionSetting(mood, "disableMoving")
        assert mood.stopMoving is True

    def test_actionSetting_enableMoving(self):
        mood = MockMood()
        mood.stopMoving = True
        ActionSetting(mood, "enableMoving")
        assert mood.stopMoving is False


class TestEmotionSetting:
    def test_emotionSetting_cheerful(self):
        mood = MockMood()
        mood.happy = 15.0
        mood.angry = 1.0
        mood.sorrow = 1.0
        mood.horror = 1.0
        mood.hate = 10.0
        mood.love = 50.0
        assert emotionSetting(mood) == "cheerful"

    def test_emotionSetting_happy(self):
        mood = MockMood()
        mood.happy = 10.0
        mood.angry = 2.0
        mood.sorrow = 2.0
        mood.horror = 2.0
        mood.hate = 10.0
        mood.friendship = 50.0
        assert emotionSetting(mood) == "happy"

    def test_emotionSetting_teasing(self):
        mood = MockMood()
        mood.happy = 6.0
        mood.angry = 2.0
        mood.sorrow = 1.0
        mood.horror = 1.0
        assert emotionSetting(mood) == "teasing"

    def test_emotionSetting_sad(self):
        mood = MockMood()
        mood.sorrow = 10.0
        mood.angry = 6.0
        mood.happy = 0.5
        assert emotionSetting(mood) == "sad"

    def test_emotionSetting_angry(self):
        mood = MockMood()
        mood.angry = 10.0
        mood.happy = 0.0
        mood.sorrow = 0.0
        mood.horror = 0.0
        assert emotionSetting(mood) == "angry"

    def test_emotionSetting_crying(self):
        mood = MockMood()
        mood.sorrow = 15.0
        mood.happy = 0.0
        mood.angry = 0.0
        mood.horror = 0.0
        assert emotionSetting(mood) == "crying"

    def test_emotionSetting_surprised(self):
        mood = MockMood()
        mood.surprised = 10.0
        mood.happy = 0.0
        mood.angry = 0.0
        mood.sorrow = 0.0
        mood.horror = 0.0
        assert emotionSetting(mood) == "surprised"

    def test_emotionSetting_normal(self):
        mood = MockMood()
        mood.happy = 0.0
        mood.angry = 0.0
        mood.sorrow = 0.0
        mood.horror = 0.0
        mood.surprised = 0.0
        assert emotionSetting(mood) == "normal"


class TestRelationSetting:
    def test_relationSetting_strange(self):
        mood = MockMood()
        mood.familiar = 100.0
        mood.friendship = 50.0
        mood.love = 50.0
        mood.hate = 50.0
        mood.fear = 50.0
        assert relationSetting(mood) == "strange"

    def test_relationSetting_enemy(self):
        mood = MockMood()
        mood.familiar = 100.0
        mood.hate = 150.0
        assert relationSetting(mood) == "enemy"

    def test_relationSetting_friend(self):
        mood = MockMood()
        mood.familiar = 1000.0
        mood.friendship = 150.0
        mood.love = 50.0
        mood.hate = 50.0
        assert relationSetting(mood) == "friend"

    def test_relationSetting_lover(self):
        mood = MockMood()
        mood.familiar = 1000.0
        mood.friendship = 150.0
        mood.love = 150.0
        mood.hate = 50.0
        assert relationSetting(mood) == "lover"

    def test_relationSetting_slave(self):
        mood = MockMood()
        mood.familiar = 1000.0
        mood.friendship = 50.0
        mood.love = 50.0
        mood.hate = 50.0
        mood.fear = 150.0
        assert relationSetting(mood) == "slave"

    def test_relationSetting_normal(self):
        mood = MockMood()
        mood.familiar = 1000.0
        mood.friendship = 50.0
        mood.love = 50.0
        mood.hate = 50.0
        mood.fear = 50.0
        assert relationSetting(mood) == "normal"