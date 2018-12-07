# -*- coding:utf-8 -*-


text_calling = u"……"

variable = {"TIMEPERIOD" : "morning", "RELATION": "normal", "EMOTION": "normal", "STAMINA": "normal", "INTEREST": "normal"}

relationList = ["normal", "strange", "friend", "lover", "slave", "enemy"]
reactionList = ["positive", "negative", "joking"]

relationTree = {"normal" : "normal",
				"strange" : "normal",
				"friend" : "normal",
				"lover" : "friend",
				"slave" : "normal",
				"enemy" : "strange"
				}

import time, random, math
import setting

def settingVariable(mood):
	hour = int(time.strftime("%H"))
	if(hour <= 5):
		variable["TIMEPERIOD"] = "night"
	elif(hour <= 8):
		variable["TIMEPERIOD"] = "morning"
	elif(hour <= 10):
		variable["TIMEPERIOD"] = "forenoon"
	elif(hour <= 12):
		variable["TIMEPERIOD"] = "noon"
	elif(hour <= 18 ):
		variable["TIMEPERIOD"] = "afternoon"
	else:
		variable["TIMEPERIOD"] = "evening"
	variable["RELATION"] = mood.relation
	variable["EMOTION"] = mood.emotion
	if(mood.tired > 100):
		variable["STAMINA"] = "exhausted"
	elif(mood.tired > 50):
		variable["STAMINA"] = "tired"
	else:
		variable["STAMINA"] = "normal"
	if(mood.interest > 0):
		variable["INTEREST"] = "normal"
	else:
		variable["INTEREST"] = "bored"


def showSpeakTime(text):
	return 5 * len(str(text)) + 20

def getTimePeriod():
	hour = int(time.strftime("%H"))
	if(5 <= hour <= 8):
		return u"早上"
	elif(8<= hour <= 10):
		return u"上午"
	elif(10 <= hour <= 12):
		return u"中午"
	elif(12 <= hour <= 18 ):
		return u"下午"
	else:
		return u"晚上"



def moodInit(mood):
	mood.love = max(mood.love, 1.0)
	mood.fear = max(mood.fear, 1.0)
	mood.hate = max(mood.hate, 1.0)
	mood.familiar = max(mood.familiar, 1.0)
	mood.friendship = max(mood.friendship, 1.0)
	mood.angry = max(mood.angry, 1.0)
	mood.happy = max(mood.happy, 1.0)
	mood.sorrow = max(mood.sorrow, 1.0)
	mood.horror = max(mood.horror, 1.0)
	mood.surprised = max(mood.surprised, 1.0)
	mood.shyness = max(mood.shyness, 1.0)
	mood.tired = max(mood.tired, 1.0)
	mood.interest = min(mood.interest, 1.0)
	mood.interest = max(mood.interest, -1.0)
	mood.angry = min(mood.angry, 20.0)
	mood.happy = min(mood.happy, 20.0)
	mood.sorrow = min(mood.sorrow, 20.0)
	mood.horror = min(mood.horror, 20.0)
	mood.surprised = min(mood.surprised, 20.0)
	mood.shyness = min(mood.shyness, 20.0)
	mood.tired = min(mood.tired, 150.0)

def ActionSetting(mood, type = ""):
	if(type == "talk"):
		mood.happy  += 3.0 * mood.interest
		mood.horror += -1.0 * max(0, mood.interest)
		mood.angry += -1.0 * mood.interest
		mood.sorrow += -1.0 * max(0, mood.interest)
		mood.surprised += 0.0
		mood.shyness += 0.0
		mood.interest -= 1.0
		result =  "talk"
	elif(type == "touch"):
		mood.surprised += 3.0
		mood.shyness += 3.0
		mood.interest -= 0.5
		if( mood.friendship - mood.hate > 50 and mood.angry < 5):
			mood.happy += 5.0
			mood.angry += -3.0
			mood.sorrow += -3.0
			result =  "goodTouch"
		else:
			mood.happy -= 5.0
			mood.angry += 5.0
			result =  "badTouch"
	elif(type == "break"):
		mood.happy  += -3.0
		mood.horror += 0.0
		mood.angry += 3.0
		mood.sorrow += 1.0
		mood.surprised += 3.0
		mood.shyness += 0.0
		result =  "break"
	elif(type == "positive"):
		mood.happy  += 5.0
		mood.horror += -3.0
		mood.angry += -2.0
		mood.sorrow += -1.0
		mood.surprised += 0.0
		mood.shyness += 1.0
		result =  "positive"
	elif(type == "negative"):
		mood.happy  += -3.0
		mood.horror += 3.0
		mood.angry += 3.0
		mood.sorrow += 3.0
		mood.surprised += 5.0
		mood.shyness += 2.0
		result =  "negative"
	elif(type == "joking"):
		mood.happy  += 1.0
		mood.horror += -1.0
		mood.angry += 1.0
		mood.sorrow += 0.0
		mood.surprised += 5.0
		mood.shyness += 3.0
		result =  "joking"
	elif(type == "disableMoving"):
		mood.stopMoving = True
		result = "disableMoving"
	elif(type == "enableMoving"):
		mood.stopMoving = False
		result = "enableMoving"
	else:
		mood.happy  += 0.0
		mood.horror += 0.0
		mood.angry += 0.0
		mood.sorrow += 0.0
		mood.surprised += 0.0
		mood.shyness += 0.0
		result =  type
	moodInit(mood)
	return result

def emotionSetting(mood):
	if(mood.happy > 10 and (mood.angry + mood.sorrow + mood.horror) < 5 and (mood.hate < mood.love)):
		return "cheerful"
	elif(mood.happy > 1 + (mood.angry + mood.sorrow + mood.horror)  and (mood.hate < mood.friendship)):
		return "happy"
	elif(mood.happy > 5 and 5 > (mood.angry + mood.sorrow + mood.horror) > 1):
		return "teasing"
	elif(mood.sorrow > mood.angry > 5 and mood.happy < 1):
		return "sad"
	elif(mood.angry > 5):
		return "angry"
	elif(mood.sorrow > 10 or mood.angry > 10 or mood.happy > 10):
		return "crying"
	elif(mood.surprised > 5):
		return "surprised"
	else:
		return "normal"

def relationSetting(mood):
	if(mood.familiar < 600):
		if(mood.hate > 100):
			return "enemy"
		return "strange"
	if(mood.friendship > 100):
		if(mood.love > 100):
			return "lover"
		else:
			return "friend"
	if(mood.hate > 100):
		return "enemy"
	if(mood.fear > 100):
		return "slave"
	return "normal"



def moodUpdate(mood):
	settingVariable(mood)
	mood.relation = relationSetting(mood)
	mood.emotion = emotionSetting(mood)
	mood.familiar += 1
	mood.friendship += mood.happy * 0.1 - mood.angry * 0.1 + mood.horror * 0.1 - 0.101
	mood.love += mood.happy * 0.01 - mood.angry * 0.1 +  mood.horror * 0.01 + 0.079
	mood.fear += mood.horror * 0.1 - mood.happy * 0.01 - 0.091
	mood.hate += mood.horror * 0.1 - mood.happy * 0.01 + mood.angry * 0.1 - 0.191
	mood.angry -= 0.5
	mood.happy -= 0.5
	mood.sorrow -= 0.5
	mood.horror -= 0.5
	mood.surprised -= 1.0
	mood.shyness -= 0.1
	mood.tired -= 1.0
	mood.interest += 0.05
	moodInit(mood)

