# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/2 00:01
# @Author  : Destiny_
# @File    : verify.py
import MACD
import numpy
import multi
import api_get
import sql_action
import date_handler

stock_map = {}
verify_map = {}
some_day = ''
start_day = input('输入验证日期:')
day_range = date_handler.trade_day(start_day, date_handler.today())
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
    pieces = api_get.cut(stockNos, 100)
    for piece in pieces:
        multi.multi(piece, one_filter_data)


def get_verify_data():
    pieces = api_get.cut(verifyNos, 100)
    for piece in pieces:
        multi.multi(piece, one_verify_data)


def refresh_stock_map():
    global stock_map
    new_map = {}
    for stockNo in stockNos:
        new_map[stockNo] = stock_map[stockNo]
    stock_map = new_map


def step2():  # 交易量筛选 昨日的交易量是前期（10日内）最高的交易量40%-60%，今日的交易量大于第一天%80-90，--前10天的交易量跌幅超过8%
    global stock_map, stockNos, volume_filter
    volume_filter = []
    print('交易量筛选开始……')
    refresh_stock_map()
    for _ in stock_map:
        max_volume = 0
        stock_details = stock_map[_]
        if len(stock_details) >= 11:
            last_10 = stock_details[-11:-1]
            judge = True
            for o in last_10:
                for p in o:
                    if p == '--':
                        judge = False
            # start_volume = float(last_10[0][6])
            # end_volume = float(last_10[-1][6])
            if judge:
                for one_day in last_10:
                    one_day_volume = float(one_day[6])
                    if one_day_volume > max_volume:
                        max_volume = one_day_volume
                last2_volume = float(stock_details[-2][6])
                last_volume = float(stock_details[-1][6])
                if (last_volume > last2_volume) and (
                        max_volume * 0.4 <= last2_volume <= max_volume * 0.6):  # (end_volume <= start_volume * 0.92)
                    volume_filter.append(_)
    stockNos = volume_filter
    print(len(volume_filter))


def step3():  # 形态选股 昨日收盘价低于开盘价，跌幅不超过2%||5%，今日的收盘价高于当天的开盘价，并且收盘价或者当天最高点超过昨日的最高点或开盘价。
    global price_filter, stockNos, price_filter
    price_filter = []
    print('形态选股开始……')
    refresh_stock_map()
    for stock in stock_map:
        stock_details = stock_map[stock]
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
            if judge:
                if (float(last2[2]) * 0.98 <= float(last2[3]) < float(last2[2])) and (
                        float(last[3]) > float(last[2])) and (
                        max(float(last[3]), float(last[4])) > min(float(last2[2]), float(last2[4]))):
                    price_filter.append(stock)
    stockNos = price_filter
    print(len(price_filter))


def step4():  # 选金叉 今日或昨日金叉
    global stockNos, cross_filter
    cross_filter = []
    err = []
    print('金叉选股开始……')
    refresh_stock_map()
    for stock in stock_map:
        try:
            points = MACD.points(stock, some_day, paint=False)
            if points:
                cross_filter.append(stock)
        except Exception as e:
            err.append(e)
    stockNos = cross_filter


def triangle_one(range1=5, range2=20):
    if range1 > range2:
        new = range2
        range2 = range1
        range1 = new
    triangle_filter = []
    for stock in stock_map:
        if stock[0] == '3':
            stock_details = stock_map[stock]
            judge = True
            for _ in stock_details[-2 - range2:]:
                if _[3] == '--':
                    judge = False
            if judge:
                day1_range1 = stock_details[-2 - range1:-2]
                day2_range1 = stock_details[-1 - range1:-1]
                day1_range2 = stock_details[-2 - range2:-2]
                day2_range2 = stock_details[-1 - range2:-1]
                day1_avg_range1 = numpy.mean([float(_day[3]) for _day in day1_range1])
                day2_avg_range1 = numpy.mean([float(_day[3]) for _day in day2_range1])
                day1_avg_range2 = numpy.mean([float(_day[3]) for _day in day1_range2])
                day2_avg_range2 = numpy.mean([float(_day[3]) for _day in day2_range2])
                if day1_avg_range1 < day1_avg_range2 and day2_avg_range1 > day2_avg_range2:
                    triangle_filter.append(stock)

    return triangle_filter


def main_varify():
    global stockNos, verifyNos
    stockNos = sql_action.SQL().tables()
    get_filter_data()
    stockNos = [_ for _ in stock_map]
    # step2()
    step3()
    step4()
    verifyNos = stockNos
    print(verifyNos)
    print(f'共{len(verifyNos)}个票')
    get_verify_data()
    if verifyNos:
        win_map = {}
        high_map = {}
        dont_map = False
        for verify_sample in verifyNos:
            verify_details = verify_map[verify_sample]
            if not dont_map:
                for i, v in enumerate(verify_details[1:]):
                    win_map[i] = 0
                    high_map[i] = 0
                dont_map = True
            first_day = verify_details[0]
            last_day = verify_details[-1]
            init_price = float(first_day[3])
            for i, _ in enumerate(verify_details[1:]):
                close = float(_[3])
                high = float(_[4])
                low = float(_[5])
                one_day_percent = round(((close / init_price) - 1) * 100, 3)
                high_percent = round(((high / init_price) - 1) * 100, 3)
                low_percent = round(((low / init_price) - 1) * 100, 3)
                print(f'第{i + 1}日--{verify_sample}--{"跌" if one_day_percent < 0 else "涨"}--{abs(one_day_percent)}%')
                print(f'高点---第{i + 1}日--{verify_sample}--{"跌" if high_percent < 0 else "涨"}--{abs(high_percent)}%')
                print(f'低点---第{i + 1}日--{verify_sample}--{"跌" if low_percent < 0 else "涨"}--{abs(low_percent)}%')
                if one_day_percent > 0:
                    win_map[i] += 1
                if high_percent > 0:
                    high_map[i] += 1
            print('\n')
        for _ in win_map:
            win_time = win_map[_]
            win_percent = (win_time / len(verifyNos)) * 100
            print(f'持仓{_ + 1}日胜率--{win_percent}%')
        for _ in high_map:
            win_time = high_map[_]
            win_percent = (win_time / len(verifyNos)) * 100
            print(f'高点---持仓{_ + 1}日胜率--{win_percent}%')
    else:
        print('无结果')


if __name__ == '__main__':
    some_day = start_day
    get_filter_data()
    print(triangle_one())
    # for day in day_range:
    #     some_day = date_handler.date2str(day)
    #     print(some_day)
    #     main_varify()
    #     print('\n')
