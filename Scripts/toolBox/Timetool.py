# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# @author : Destiny_
# @file   : Timetool.py
# @time   : 2022/03/08
import time


def strToStamp(launchTime: str):
    timeArray = time.strptime(launchTime, '%Y-%m-%d %H:%M:%S')
    timeStamp = time.mktime(timeArray)
    return timeStamp


def stampToStr(launchTime: int):
    timeArray = time.localtime(launchTime)
    timeStr = time.strftime('%H:%M:%S', timeArray)
    return timeStr
