# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/2 00:01
# @Author  : Destiny_
# @File    : verify.py
import MACD
import multi
import api_get
import sql_action
import date_handler

stock_map = {}
verify_map = {}
some_day = '2021-11-25'  # input('输入验证日期:')
some_day = date_handler.to_today(some_day)
verifyNos = []
value_filter = []
price_filter = []
cross_filter = []
volume_filter = []
tenday_filter = []
stockNos = sql_action.SQL().tables()


def one_filter_data(no: str):
    sql = sql_action.SQL()
    _id = sql.select_id_by_date(some_day, no)
    if _id:
        details = sql.select_by_id_range_before(_id, no)
        stock_map[no] = details
    sql.close()


def one_verify_data(no: str):
    sql = sql_action.SQL()
    _id = sql.select_id_by_date(some_day, no)
    if _id:
        details = sql.select_by_id_range_after(_id, no)
        verify_map[no] = details
    sql.close()


def get_filter_data():
    global stock_map
    stock_map = {}
    pieces = api_get.cut(stockNos, 100)
    for piece in pieces:
        multi.multi(piece, one_filter_data)


def get_verify_data():
    global verify_map
    verify_map = {}
    pieces = api_get.cut(verifyNos, 100)
    for piece in pieces:
        multi.multi(piece, one_verify_data)


def refresh_stock_map():
    global stock_map
    new_map = {}
    for stockNo in stockNos:
        new_map[stockNo] = stock_map[stockNo]
    stock_map = new_map


def step2():  # 交易量筛选 昨日的交易量是前期（10日内）最高的交易量40%-60%，今日的交易量大于第一天80%
    global stock_map, stockNos, volume_filter
    volume_filter = []
    refresh_stock_map()
    for stock in stock_map:
        max_volume = 0
        stock_details = stock_map[stock]
        judge = True
        if len(stock_details) >= 11:
            last_10 = stock_details[-11:-1]
            for one_ in last_10:
                for _one in one_:
                    if _one == '--':
                        judge = False
            if judge:
                # start_volume = float(last_10[0][6])
                # end_volume = float(last_10[-1][6])
                for one_day in last_10:
                    one_day_volume = float(one_day[6])
                    if one_day_volume > max_volume:
                        max_volume = one_day_volume
                last2_volume = float(stock_details[-2][6])
                last_volume = float(stock_details[-1][6])
                if (last_volume > last2_volume * 0.8) and (
                        max_volume * 0.4 <= last2_volume <= max_volume * 0.6):  # (end_volume <= start_volume * 0.92)
                    volume_filter.append(stock)
    stockNos = volume_filter


def step3():  # 形态选股 昨日收盘价低于开盘价，跌幅不超过2%，今日的收盘价高于当天的开盘价，并且收盘价或者当天最高点超过昨日的最高点或开盘价。
    global stockNos,price_filter
    price_filter = []
    refresh_stock_map()
    for stock in stock_map:
        stock_details = stock_map[stock]
        if len(stock_details) >= 2:
            last2 = stock_details[-2]
            last = stock_details[-1]
            judge = True
            for _2 in last2:
                if _2 == '--':
                    judge = False
            for _2 in last:
                if _2 == '--':
                    judge = False
            if judge:
                if (float(last2[2]) * 0.98 <= float(last2[3]) < float(last2[2])) and (
                        float(last[3]) > float(last[2])) and (
                        max(float(last[3]), float(last[4])) > min(float(last2[2]), float(last2[4]))):
                    price_filter.append(stock)
    stockNos = price_filter


def step4():  # 选金叉 今日或昨日金叉
    global stockNos,cross_filter
    cross_filter = []
    err = []
    refresh_stock_map()
    for stock in stock_map:
        try:
            points = MACD.points(stock, some_day, paint=True)
            if points:
                cross_filter.append(stock)
        except Exception as e:
            err.append(e)
    stockNos = cross_filter


def main_varify():
    global stockNos, verifyNos
    win = 0
    win2 = 0
    win3 = 0
    win4 = 0
    win5 = 0
    try_time = 0
    try_time2 = 0
    try_time3 = 0
    try_time4 = 0
    try_time5 = 0
    percent_all = 0
    percent_all2 = 0
    percent_all3 = 0
    percent_all4 = 0
    percent_all5 = 0
    stockNos = sql_action.SQL().tables()
    get_filter_data()
    stockNos = [_ for _ in stock_map]
    step2()
    step3()
    step4()
    verifyNos = stockNos
    get_verify_data()
    if verifyNos:
        for verify_sample in verifyNos:
            verify_details = verify_map[verify_sample]
            if len(verify_details) >= 2:
                print('----------------------------------------')
                try_time += 1
                first_day = verify_details[0]
                secd_day = verify_details[1]
                init_price = float(first_day[3])
                finish_price = float(secd_day[4])
                percent = (finish_price / init_price) - 1
                percent_all += percent
                print(f'\n{verify_sample}   次日  {"涨幅" if percent > 0 else "跌幅"}   {"-" if percent < 0 else ""}{round(abs(percent) * 100,3)}%')
                if percent * 100 > 0.5:
                    win += 1
                if len(verify_details) >= 6:
                    try_time2 += 1
                    try_time3 += 1
                    try_time4 += 1
                    try_time5 += 1
                    day2 = verify_details[2]
                    day3 = verify_details[3]
                    day4 = verify_details[4]
                    day5 = verify_details[5]
                    day2high = float(day2[4])
                    day3high = float(day3[4])
                    day4high = float(day4[4])
                    day5high = float(day5[4])
                    day2percent = (day2high / init_price) - 1
                    day3percent = (day3high / init_price) - 1
                    day4percent = (day4high / init_price) - 1
                    day5percent = (day5high / init_price) - 1
                    percent_all2 += day2percent
                    percent_all3 += day3percent
                    percent_all4 += day4percent
                    percent_all5 += day5percent
                    if day2percent * 100 >= 0.5:
                        win2 += 1
                    if day3percent * 100 >= 0.5:
                        win3 += 1
                    if day4percent * 100 >= 0.5:
                        win4 += 1
                    if day5percent * 100 >= 0.5:
                        win5 += 1
                    print(f'{verify_sample}   两天  {"涨幅" if day2percent > 0 else "跌幅"}   {"-" if day2percent < 0 else ""}{round(abs(day2percent) * 100, 3)}%')
                    print(f'{verify_sample}   三天  {"涨幅" if day3percent > 0 else "跌幅"}   {"-" if day3percent < 0 else ""}{round(abs(day3percent) * 100, 3)}%')
                    print(f'{verify_sample}   四天  {"涨幅" if day4percent > 0 else "跌幅"}   {"-" if day4percent < 0 else ""}{round(abs(day4percent) * 100, 3)}%')
                    print(f'{verify_sample}   五天  {"涨幅" if day5percent > 0 else "跌幅"}   {"-" if day5percent < 0 else ""}{round(abs(day5percent) * 100, 3)}%')
                # elif len(verify_details) == 4:
                #     try_time3 += 1
                #     day3 = verify_details[3]
                #     day3high = float(day3[4])
                #     day3percent = (day3high / init_price) - 1
                #     percent_all3 += day3percent
                #     if day3percent * 100 >= 0.5:
                #         win3 += 1
                #     print(f'{verify_sample}   三天  {"涨幅" if day3percent > 0 else "跌幅"}   {"-" if day3percent < 0 else ""}{round(abs(day3percent) * 100, 3)}%')
                # elif len(verify_details) == 5:
                #     try_time4 += 1
                #     _day4 = verify_details[4]
                #     _day4high = float(_day4[4])
                #     _day4percent = (_day4high / init_price) - 1
                #     percent_all4 += _day4percent
                #     if _day4percent * 100 >= 0.5:
                #         win4 += 1
                #     print(f'{verify_sample}   四天  {"涨幅" if _day4percent > 0 else "跌幅"}   {"-" if _day4percent < 0 else ""}{round(abs(_day4percent) * 100, 3)}%')
    else:
        print('无结果')
    if try_time != 0:
        print(f'{some_day}次日分析----------------------------------------')
        win_percent = win / try_time
        avg_win = (percent_all * 100) / try_time
        print(f'次日胜利：{win}/总共样本：{try_time}')
        print(f'如果全部平均买入,次日{"赚" if avg_win > 0 else "亏"}{"-" if avg_win < 0 else ""}{round(avg_win,3)}%')
        print(f'{some_day}筛选出的   次日胜率{round(win_percent * 100, 3)}%\n')
    if try_time2 != 0:
        print(f'{some_day}两日分析----------------------------------------')
        win2_percent = win2 / try_time2
        avg_win2 = (percent_all2 * 100) / try_time2
        print(f'两日胜利：{win2}/总共样本：{try_time2}')
        print(f'如果全部平均买入,两日{"赚" if avg_win2 > 0 else "亏"}{"-" if avg_win2 < 0 else ""}{round(avg_win2,3)}%')
        print(f'{some_day}筛选出的   两日胜率{round(win2_percent * 100, 3)}%\n')
    if try_time3 != 0:
        print(f'{some_day}三日分析----------------------------------------')
        win3_percent = win3 / try_time3
        avg_win3 = (percent_all3 * 100) / try_time3
        print(f'三日胜利：{win3}/总共样本：{try_time3}')
        print(f'如果全部平均买入,三日{"赚" if avg_win3 > 0 else "亏"}{"-" if avg_win3 < 0 else ""}{round(avg_win3,3)}%')
        print(f'{some_day}筛选出的   三日胜率{round(win3_percent * 100, 3)}%\n')
    if try_time4 != 0:
        print(f'{some_day}四日分析----------------------------------------')
        win4_percent = win4 / try_time4
        avg_win4 = (percent_all4 * 100) / try_time4
        print(f'四日胜利：{win4}/总共样本：{try_time4}')
        print(f'如果全部平均买入,四日{"赚" if avg_win4 > 0 else "亏"}{"-" if avg_win4 < 0 else ""}{round(avg_win4,3)}%')
        print(f'{some_day}筛选出的   四日胜率{round(win4_percent * 100, 3)}%\n')
    if try_time5 != 0:
        print(f'{some_day}五日分析----------------------------------------')
        win5_percent = win5 / try_time5
        avg_win5 = (percent_all5 * 100) / try_time5
        print(f'五日胜利：{win5}/总共样本：{try_time5}')
        print(f'如果全部平均买入,五日{"赚" if avg_win5 > 0 else "亏"}{"-" if avg_win5 < 0 else ""}{round(avg_win5,3)}%')
        print(f'{some_day}筛选出的   五日胜率{round(win5_percent * 100, 3)}%\n')


def roll():
    ranges = date_handler.trade_day('2021-11-10', '2021-12-05')
    return [date_handler.date2str(r) for r in ranges]


def date_roll():
    global some_day
    print('以大于0.5%为有感知胜利')
    for date in roll():
        some_day = date
        print(f'---------------{some_day}------------------')
        main_varify()


date_roll()
