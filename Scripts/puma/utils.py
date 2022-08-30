# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# @author : Destiny_
# @file   : utils.py
# @time   : 2022/02/19
import time


def header(token=''):
    headers = {
        'Host': 'api-cn.puma.com',
        'Content-Type': 'application/json;charset=UTF-8',
        'invoke-source': 'https://cn.puma.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'unexUserToken': token,
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
        'Referer': 'https://servicewechat.com/wxa1a24b17bce3f64f/76/page-frame.html',
        'Accept-Language': 'zh-cn'
    }
    return headers


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
