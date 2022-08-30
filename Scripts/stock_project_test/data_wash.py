# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/12 19:46
# @Author  : Destiny_
# @File    : data_wash.py

import api
import sql_action
import thread_loop


def muti_find_null():
    nulls = {}
    stocks = sql_action.SQL().stocks()

    def find_null(stock):
        sql = sql_action.SQL()
        res = sql.find_null(stock)
        if res:
            res = set(res)
            print(f'{stock}.{res}')
            null2021 = [_ for _ in res if _[:4] == '2021']
            null2022 = [_ for _ in res if _[:4] == '2022']
            nulls[stock] = {'2021': null2021, '2022': null2022}

    thread_loop.thread_pool_executor(func=find_null, iterator=stocks)
    return nulls


def fix_null(nulls):
    for stock in nulls:
        null = nulls[stock]
        null2021 = null['2021']
        null2022 = null['2022']
        if null2021:
            new_data = api.year_data(stock, 2021)
            if new_data:
                for date in null2021:
                    if date in new_data.keys():
                        print(f'fix {stock} {date}')
                        sql_action.SQL().update_from_126data(stock, date, new_data[str(date).replace('-', '')])
        if null2022:
            new_data = api.year_data(stock, 2022)
            if new_data:
                for date in null2022:
                    if date in new_data.keys():
                        print(f'fix {stock} {date}')
                        sql_action.SQL().update_from_126data(stock, date, new_data[str(date).replace('-', '')])


def ma5(stock):
    datas = sql_action.SQL().select(f'No{stock}')
    print(datas)


if __name__ == '__main__':
    ma5('000001')
