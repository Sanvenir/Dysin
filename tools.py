# -*- coding:utf-8 -*-

import time, random, math
import setting

def showSpeakTime(text):
    return 5 * len(str(text)) + 20

def getTimePeriod():
    hour = int(time.ctime().split()[3].split(':')[0])
    if(5 <= hour <= 8):
            return "早上"
    elif(hour <= 10):
            return "上午"
    elif(hour <= 12):
            return "中午"
    elif(hour <= 18 ):
            return "下午"
    else:
            return "晚上"

def replaceText(line):
        line = line.replace("_TIMEPERIOD_", getTimePeriod())
        line = line.replace("_CALLING_", setting.text_calling)
        line = line.replace("_SECONDCALLING_", setting.text_secondCalling)
        line = line.replace("_NAME_", setting.text_name)
        line = line.replace("_TRAYNAME_", setting.text_trayName)
        return line


def showFace(self):
        if(self.happy > 5 and (self.angry + self.sorrow + self.horror) < 1):
                return "cheerful"
        elif(self.happy > 5 * (self.angry + self.sorrow + self.horror)):
                return "happy"
        elif(self.happy > 5 and 5 > (self.angry + self.sorrow + self.horror) > 1):
                return "teasing"
        elif(self.sorrow > self.angry > 5 and self.happy < 1):
                return "sad"
        elif(self.surprised > 5):
                return "surprised"
        elif(self.sorrow > 10 or self.angry > 10 or self.happy > 10):
                return "crying"
        elif(self.angry > 5):
                return "angry"
        else:
                return "normal"
            
def ActionSetting(mood, type = ""):
	if(type == "talk"):
		mood.happy  += 1
		mood.horror += -1
		mood.angry += -1
		mood.sorrow += -1
		mood.surprised += 0
		mood.shyness += 0
	elif(type == "break"):
		mood.happy  += -3
		mood.horror += 0
		mood.angry += 3
		mood.sorrow += 1
		mood.surprised += 3
		mood.shyness += 0
	elif(type == "positive"):
		mood.happy  += 5
		mood.horror += -3
		mood.angry += -2
		mood.sorrow += -1
		mood.surprised += 0
		mood.shyness += 1
	elif(type == "negative"):
		mood.happy  += -3
		mood.horror += 3
		mood.angry += 3
		mood.sorrow += 3
		mood.surprised += 5
		mood.shyness += 2
	elif(type == "joking"):
		mood.happy  += 1
		mood.horror += -1
		mood.angry += 1
		mood.sorrow += 0
		mood.surprised += 5
		mood.shyness += 3
	else:
		mood.happy  += 0
		mood.horror += 0
		mood.angry += 0
		mood.sorrow += 0
		mood.surprised += 0
		mood.shyness += 0

