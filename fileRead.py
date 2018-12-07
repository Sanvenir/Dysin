# -*- coding:utf-8 -*-

import sys

def fileReadNum(line, name):
	if(line.find(name) > -1):
		pos = line.find('=')
		if(pos > -1):
			num = line[pos + 1:]
			num = num.strip()
			try:
				return int(num)
			except ValueError:
				print("ValueError:", sys.exc_info()[1])
	return 0

def fileReadFloat(line, name):
	if(line.find(name) > -1):
		pos = line.find('=')
		if(pos > -1):
			num = line[pos + 1:]
			num = num.strip()
			try:
				return float(num)
			except ValueError:
				print("ValueError:", sys.exc_info()[1])
	return 0

def fileReadStr(line, name):
	if(line.find(name) > -1):
		pos = line.find('=')
		if(pos > -1):
			message = line[pos + 1:]
			return message.strip()
	return ""

def listReadFloat(list, name):
	for line in list:
		a = fileReadFloat(line, name)
		if(a):
			return a
	return 0.0

def listReadInt(list, name):
	for line in list:
		a = fileReadNum(line, name)
		if(a):
			return a
	return 0

def listReadStr(list, name):
	for line in list:
		a = fileReadStr(line, name)
		if(a):
			return a
	return ""

def lyricRead(fileName):
	try:
		f = open(fileName)
		list = []
		for line in f.readlines():
			time = line.split(']')[0]
			lyric = line.split(']')[1]
			time = time.strip('[')
			try:
				realTime = float(int(time.split(':')[0]) * 60) + float(time.split(':')[1])
				list.append([realTime, lyric.decode('gbk')])
			except:
				pass
		f.close()
		return list
	except IOError:
		return 0

def fileReadLines(start, end, file):
	file.seek(0)
	return listReadLines(start, end, file.readlines())

def listReadLines(start, end, list):
	startFlag = False
	context = []
	for line in list:
		line = line.strip()
		if(startFlag):
			if(end == line):
				return context
			context.append(line)
		elif(start == line):
			startFlag = True
	return context

def listReadAllLines(start, end, list):
	startFlag = False
	allContext = []
	context = []
	for line in list:
		line = line.strip()
		if(startFlag):
			if(end == line):
				allContext.append(context)
				context = []
				startFlag = False
			else:
				context.append(line)
		elif(start == line):
			startFlag = True
	return allContext


def fileToList(file):
	list = []
	for line in file.readlines():
		list.append(line)
	return list

def readGoto(line):
	pos = line.find(":")
	if(pos >= 0):
		goto = line[pos + 1:]
	else:
		goto = ""
	return goto.strip()

def fileReadVariable(filename):
	result = {}
	file = open(filename)
	for lines in file.readlines():
		if(lines.find("=") > 0):
			name = lines.split("=")[0].strip()
			context = lines.split("=")[1].strip()
		result[name] = context
	return result

def actionFrameSetting(list, name):
	frameList = listReadStr(list, name).split(',')
	result = []
	for i in frameList:
		result.append(int(i))
	return result