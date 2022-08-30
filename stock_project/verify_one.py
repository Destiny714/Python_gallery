# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/7 21:28
# @Author  : Destiny_
# @File    : verify_one.py

import sql_action

sql = sql_action.SQL()

date = '2021-12-08'
stock = '601238'

stock_details = sql.select(f'No{stock}')

max_volume = 0
judge = True
if len(stock_details) >= 11:
    last_10 = stock_details[-11:-1]
    print(len(last_10))
    for one in last_10:
        for _ in one:
            if _ == '--':
                judge = False
    if judge:
        print('judge pass')
        # start_volume = float(last_10[0][6])
        # end_volume = float(last_10[-1][6])
        for one_day in last_10:
            one_day_volume = float(one_day[6])
            if one_day_volume > max_volume:
                max_volume = one_day_volume
        last2_volume = float(stock_details[-2][6])
        last_volume = float(stock_details[-1][6])
        if last_volume > last2_volume:
            print('volume1 pass')
        print(max_volume)
        if max_volume * 0.4 <= last2_volume <= max_volume * 0.6:
            print('volume2 pass')
        if (last_volume > last2_volume) and (
                max_volume * 0.4 <= last2_volume <= max_volume * 0.6):  # (end_volume <= start_volume * 0.92)
            print(True)
        else:
            print(False)


if len(stock_details) >= 2:
    last2 = stock_details[-2]
    last = stock_details[-1]
    judge = True
    for _ in last2:
        if _ == '--':
            judge = False
    for _ in last:
        if _ == '--':
            judge = False
            print(False)
    if judge:
        if (float(last2[2]) * 0.98 <= float(last2[3]) < float(last2[2])) and (
                float(last[3]) > float(last[2])) and (max(float(last[3]),float(last[4])) > min(float(last2[2]),float(last2[4]))):
            print(True)
        else:
            print(False)
    else:
        print('judge')
