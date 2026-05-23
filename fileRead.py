# -*- coding:utf-8 -*-
"""文件读取工具模块"""

import sys


def fileReadNum(line, name):
    """从配置行读取整数"""
    if line.find(name) > -1:
        pos = line.find('=')
        if pos > -1:
            num = line[pos + 1:]
            num = num.strip()
            try:
                return int(num)
            except ValueError:
                print("ValueError:", sys.exc_info()[1])
    return 0


def fileReadFloat(line, name):
    """从配置行读取浮点数"""
    if line.find(name) > -1:
        pos = line.find('=')
        if pos > -1:
            num = line[pos + 1:]
            num = num.strip()
            try:
                return float(num)
            except ValueError:
                print("ValueError:", sys.exc_info()[1])
    return 0


def fileReadStr(line, name):
    """从配置行读取字符串"""
    if line.find(name) > -1:
        pos = line.find('=')
        if pos > -1:
            message = line[pos + 1:]
            return message.strip()
    return ""


def listReadFloat(lst, name):
    """从列表中查找浮点数配置"""
    for line in lst:
        a = fileReadFloat(line, name)
        if a:
            return a
    return 0.0


def listReadInt(lst, name):
    """从列表中查找整数配置"""
    for line in lst:
        a = fileReadNum(line, name)
        if a:
            return a
    return 0


def listReadStr(lst, name):
    """从列表中查找字符串配置"""
    for line in lst:
        a = fileReadStr(line, name)
        if a:
            return a
    return ""


def lyricRead(filename):
    """读取歌词文件 (.lrc)"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lst = []
            for line in f.readlines():
                if ']' not in line:
                    continue
                time_part, lyric = line.split(']', 1)
                time_part = time_part.strip('[')
                try:
                    minutes = int(time_part.split(':')[0])
                    seconds = float(time_part.split(':')[1])
                    real_time = minutes * 60 + seconds
                    lst.append([real_time, lyric.strip()])
                except (ValueError, IndexError):
                    pass
            return lst
    except IOError:
        return None


def fileReadLines(start, end, file_obj):
    """从文件对象中读取指定区间的行"""
    file_obj.seek(0)
    return listReadLines(start, end, file_obj.readlines())


def listReadLines(start, end, lst):
    """从列表中提取指定区间的行"""
    start_flag = False
    context = []
    for line in lst:
        line = line.strip()
        if start_flag:
            if end == line:
                return context
            if line:
                context.append(line)
        elif start == line:
            start_flag = True
    return context


def listReadAllLines(start, end, lst):
    """从列表中提取所有指定区间的行块"""
    start_flag = False
    all_context = []
    context = []
    for line in lst:
        line = line.strip()
        if start_flag:
            if end == line:
                if context:
                    all_context.append(context)
                context = []
                start_flag = False
            elif line:
                context.append(line)
        elif start == line:
            start_flag = True
    return all_context


def fileToList(file_obj):
    """将文件对象转换为列表"""
    return [line for line in file_obj.readlines()]


def readGoto(line):
    """读取跳转标签"""
    pos = line.find(":")
    if pos >= 0:
        goto = line[pos + 1:]
    else:
        goto = ""
    return goto.strip()


def fileReadVariable(filename):
    """读取变量配置文件 (key=value 格式)"""
    result = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            if '=' in line:
                name = line.split('=')[0].strip()
                context = line.split('=')[1].strip()
                result[name] = context
    return result


def actionFrameSetting(lst, name):
    """读取动作帧设置"""
    frame_list = listReadStr(lst, name).split(',')
    result = []
    for i in frame_list:
        result.append(int(i))
    return result
