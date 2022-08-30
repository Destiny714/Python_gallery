# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/26 16:28
# @Author  : Destiny_
# @File    : check_price.py

import api_get
import date_handler

path = '/Users/destiny/Desktop/PycharmProject/stock_project'
yesterday = date_handler.yesterday()


def read_file():
    stocks = []
    with open(f'{path}/steps/{yesterday}-result.txt', 'r') as f:
        li = f.read().split('\n')
        for _ in li:
            if len(_) == 6:
                stocks.append(_)
    return stocks


if __name__ == '__main__':
    stock = read_file()
    api_get.check_prices(stock,'2021-12-09')
