# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/13 22:57
# @Author  : Destiny_
# @File    : utils.py

import time

headers = {
    'Connection': 'keep-alive',
    'content-type': 'application/json',
    'Accept-Encoding': 'gzip,compress,br,deflate',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.16(0x18001034) NetType/4G Language/zh_CN'
}


def toTimeStamp(launchTime: str):
    timeArray = time.strptime(launchTime, '%Y-%m-%d %H:%M:%S')
    timeStamp = time.mktime(timeArray)
    return timeStamp


def toTimeStr(launchTime):
    timeArray = time.localtime(launchTime)
    timeStr = time.strftime('%H:%M:%S', timeArray)
    return timeStr


def isStart(launchTime: str):
    nowTime = time.time()
    timeStamp = toTimeStamp(launchTime)
    if nowTime >= timeStamp:
        return True
    else:
        return False


def countDown(start, onCall, lag: float = 0.3):
    count = True
    while count:
        diff = start - time.time()
        if diff <= lag:
            count = False
            onCall()
