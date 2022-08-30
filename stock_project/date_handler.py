# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/23 18:27
# @Author  : Destiny_
# @File    : date_handler.py

import time
import datetime
import sql_action

holidays = sql_action.SQL().holidays()
today_str = str(datetime.datetime.today()).split()[0]


def str2date(date: str):
    assert len(date) == 8
    year = date[:4]
    month = date[4:6]
    day = date[6:]
    new_date = f'{year}-{month}-{day}'
    format_date = time.strptime(new_date, '%Y-%m-%d')
    final_date = datetime.datetime(format_date[0], format_date[1], format_date[2])
    return final_date


def date2str(date: datetime.datetime):
    month = f'{0 if date.month < 10 else ""}{date.month}'
    day = f'{0 if date.day < 10 else ""}{date.day}'
    date_str = f'{date.year}-{month}-{day}'
    return date_str


def week_day(day: datetime.datetime):
    weekday = day.weekday() + 1
    return weekday


def trade_day(start: str, end: str):
    dates = []
    start = str2date(start)
    end = str2date(end)
    date = start
    while date <= end:
        dates.append(date)
        date += datetime.timedelta(days=1)
    no_trade_day = []
    for _ in dates:
        if week_day(_) in [6,7]:
            no_trade_day.append(_)
        else:
            if date2str(_) in holidays:
                no_trade_day.append(_)
    for d in no_trade_day:
        dates.remove(d)
    return dates


def last_trade_day(date, index):
    start = str2date(date) - datetime.timedelta(days=30)
    dates = trade_day(date2str(start), date)
    result = date2str(dates[-index])
    return result


def today():
    return last_trade_day(today_str, 1)


def yesterday():
    return last_trade_day(today_str, 2)


def to_yesterday(some_day: str):
    return last_trade_day(some_day, 2)


def to_today(some_day: str):
    return last_trade_day(some_day, 1)
