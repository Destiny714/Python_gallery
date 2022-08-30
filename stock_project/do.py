# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/9 23:05
# @Author  : Destiny_
# @File    : do.py
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor
import threadpool
import talib
import pandas
import date_handler
import sql_action
import find_point


def MA(stock):
    stock_detail = sql_action.SQL().select(f'No{stock}')
    stock_data = pandas.DataFrame(stock_detail)
    mas = [5, 10, 20]
    for ma in mas:
        stock_data[f'ma{ma}'] = talib.MA(stock_data[3], timeperiod=ma)
    stock_data = stock_data.dropna()
    ma_data = pandas.DataFrame([stock_data[1],stock_data['ma5'],stock_data['ma10'],stock_data['ma20']]).transpose()
    return ma_data.iterrows()


def insert_ma(stock):
    sql = sql_action.SQL()
    ma_data = MA(stock)
    for _ in ma_data:
        data = _[1]
        print(f'{stock}.{data[1]}')
        sql.update_ma(stock,data)


def triangle(stock,today):
    avgs = {}
    dates = {}
    stock_detail = sql_action.SQL().select(f'No{stock}')
    if len(stock_detail) >= 20:
        stock_data = pandas.DataFrame(stock_detail)
        mas = [5, 10, 20]
        for ma in mas:
            stock_data[f'ma{ma}'] = talib.MA(stock_data[3], timeperiod=ma)
        stock_data = stock_data[19:]
        for value in stock_data.values:
            data = {'date': value[1], 5: value[-3], 10: value[-2], 20: value[-1]}
            avgs[value[1]] = data
        for _i, __ in enumerate([_key for _key in avgs.keys()]):
            dates[_i] = avgs[__]['date']
        x = [index for index in range(len(dates))]
        five_y = [_data[5] for _data in [_value for _value in avgs.values()]]
        ten_y = [_data[10] for _data in [_value for _value in avgs.values()]]
        twenty_y = [_data[20] for _data in [_value for _value in avgs.values()]]
        result5_10 = find_point.get_point(x, five_y, x, ten_y, atol=five_y[-1] / 200)
        result5_20 = find_point.get_point(x, five_y, x, twenty_y, atol=twenty_y[-1] / 100)
        result10_20 = find_point.get_point(x, ten_y, x, twenty_y, atol=ten_y[-1] / 100)
        final5_10 = [_5_10 for _5_10 in result5_10 if
                     avgs[dates[int(_5_10[0])]][5] < avgs[dates[int(_5_10[0])]][10] and avgs[dates[int(_5_10[0]) + 1]][
                         5] >
                     avgs[dates[int(_5_10[0]) + 1]][10]]
        final5_20 = [_5_20 for _5_20 in result5_20 if
                     avgs[dates[int(_5_20[0])]][5] < avgs[dates[int(_5_20[0])]][20] and avgs[dates[int(_5_20[0]) + 1]][
                         5] >
                     avgs[dates[int(_5_20[0]) + 1]][20]]
        final10_20 = [_10_20 for _10_20 in result10_20 if
                      avgs[dates[int(_10_20[0])]][10] < avgs[dates[int(_10_20[0])]][20] and
                      avgs[dates[int(_10_20[0]) + 1]][
                          10] >
                      avgs[dates[int(_10_20[0]) + 1]][20]]
        if final5_10 and final5_20 and final10_20:
            if final5_10[-1][0] < final5_20[-1][0] < final10_20[-1][0]:
                # print(dates[int(final5_10[-1][0]) + 1], final5_10[-1])
                # print(dates[int(final5_20[-1][0]) + 1], final5_20[-1])
                # print(dates[int(final10_20[-1][0]) + 1], final10_20[-1])
                if dates[int(final10_20[-1][0]) + 1] in [today, date_handler.to_yesterday(today),
                                                         date_handler.last_trade_day(today, 3)]:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False


def thread_pool_executor(func,iterable,thread_num=50):
    executor = ThreadPoolExecutor(max_workers=thread_num)
    tasks = [executor.submit(func, _) for _ in iterable]
    for task in ALL_COMPLETED(tasks):
        task.result()


def thread_pool(func,iterable,thread_num=50):
    pool = threadpool.ThreadPool(thread_num)
    tasks = threadpool.makeRequests(func, iterable)
    [pool.putRequest(_) for _ in tasks]
    pool.wait()


if __name__ == '__main__':
    stocks = sql_action.SQL().stock_Nos()
    thread_pool(insert_ma,stocks)
