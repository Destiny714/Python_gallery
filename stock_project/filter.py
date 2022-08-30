# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/2 16:50
# @Author  : Destiny_
# @File    : filter copy.py

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/25 16:08
# @Author  : Destiny_
# @File    : filter.py

import os
import MACD
import multi
import numpy
import warnings
import data_read
import data_write
import sql_action
import date_handler

warnings.filterwarnings('ignore')

sql = sql_action.SQL()
path = '/Users/destiny/Desktop/MyCode/Python/stock_project'

excel_path = f'{path}/excel'
excels = os.listdir(excel_path)
steps = os.listdir(f'{path}/steps')
today = date_handler.today()
print(today)


def write_file(file_name, filter_list):
    with open(f'{path}/steps/{today}-{file_name}.txt', 'w') as f:
        for _ in filter_list:
            f.write(f'{_}\n')
    print(f'{today}-{file_name}.txt---写入成功')


def refresh_stock_map(stocks):
    new_map = {}
    for stock in stocks:
        new_map[stock] = stock_map[stock]
    return new_map


def volume(stocks):  # 交易量筛选 昨日的交易量是前期（10日内）最高的交易量40%-60%，今日的交易量大于第一天，--前10天的交易量跌幅超过8%
    volume_filter = []
    print('交易量筛选开始……')
    _stock_map = refresh_stock_map(stocks)
    for _ in _stock_map:
        max_volume = 0
        stock_details = _stock_map[_]
        if len(stock_details) >= 11:
            last_10 = stock_details[-11:-1]
            judge = True
            for o in last_10:
                for p in o:
                    if p == '--':
                        judge = False
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
    return volume_filter


def shape(stocks):  # 形态选股 昨日收盘价低于开盘价，跌幅不超过2%||5%，今日的收盘价高于当天的开盘价，并且收盘价或者当天最高点超过昨日的最高点或开盘价。
    price_filter = []
    print('形态选股开始……')
    _stock_map = refresh_stock_map(stocks)
    for stock in _stock_map:
        stock_details = _stock_map[stock]
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
    return price_filter


def goldX(stocks):  # 选金叉 今日或昨日金叉
    cross_filter = []
    print('金叉选股开始……')
    for stock in stocks:
        points = MACD.points(stock, today, paint=False)
        if points:
            cross_filter.append(stock)
    return cross_filter


def triangle(stocks):
    _stock_map = refresh_stock_map(stocks)
    triangle_filter = multi.multi_find_triangle(_stock_map)
    return triangle_filter


def triangle_one(stocks, range1=5, range2=10):
    if range1 > range2:
        new = range2
        range2 = range1
        range1 = new
    triangle_filter = []
    _stock_map = refresh_stock_map(stocks)
    for stock in _stock_map:
        stock_details = _stock_map[stock]
        judge = True
        for _ in stock_details[-2 - range2:]:
            if _[3] == '--':
                judge = False
        if judge:
            day1_range1 = stock_details[-2 - range1:-2]
            day2_range1 = stock_details[-1 - range1:-1]
            day1_range2 = stock_details[-2 - range2:-2]
            day2_range2 = stock_details[-1 - range2:-1]
            day1_avg_range1 = numpy.mean(
                [float(_day[3]) for _day in day1_range1])
            day2_avg_range1 = numpy.mean(
                [float(_day[3]) for _day in day2_range1])
            day1_avg_range2 = numpy.mean(
                [float(_day[3]) for _day in day1_range2])
            day2_avg_range2 = numpy.mean(
                [float(_day[3]) for _day in day2_range2])
            if day1_avg_range1 < day1_avg_range2 and day2_avg_range1 > day2_avg_range2:
                triangle_filter.append(stock)

    return triangle_filter


if __name__ == '__main__':
    if f'{today}.xlsx' not in excels:
        print('请导入今日数据')
        exit(0)
    else:
        print(f'导入数据---{today}.xlsx')

    check = data_read.READ().check_excel_format(f'{today}.xlsx')
    if not check:
        print('格式错误')
        exit(0)
    else:
        print('插入数据格式检查完毕')

        data_write.update_details()
        data_write.read_excel_and_write()
        stockNos = sql.tables()
        print(f'共{len(stockNos)}支股票')
        stock_map = multi.refresh_stock_map(stockNos)

        result = goldX(volume(shape(stockNos)))
        print(f'共{len(result)}支')
        for one in result:
            print(f'{one}.{sql.select_stock_name(one)}')
