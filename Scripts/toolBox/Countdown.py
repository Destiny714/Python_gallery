# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# @author : Destiny_
# @file   : Countdown.py
# @time   : 2022/03/08

import time
import schedule
import Timetool


def preCount(some, launchTime: int, *args):
    launchTimeStr = Timetool.stampToStr(launchTime - 5)
    schedule.every().day.at(launchTimeStr).do(some, *args)
    while time.time() <= launchTime - 3:
        print(f'last {launchTime - int(time.time())} second')
        schedule.run_pending()
        time.sleep(1)


def countDown(some, launchTime: int, lag, *args):
    while 1:
        if time.time() >= launchTime - lag:
            some(*args)
            break


def finalCountDown(lag, launchTime: int, some, *args):
    preCount(countDown, launchTime, some, launchTime, lag, *args)
