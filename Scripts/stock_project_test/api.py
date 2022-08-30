# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/22 18:47
# @Author  : Destiny_
# @File    : api.py

import requests


def cut(full_list: list, piece: int):
    cut_list = []
    extra_num = len(full_list) % piece
    if extra_num != 0:
        extra = full_list[-extra_num:]
        full = full_list[:-extra_num]
    else:
        extra = []
        full = full_list
    for i in range(len(full) // piece):
        small_piece = full[piece * i:piece * (i + 1)]
        cut_list.append(small_piece)
    if extra:
        cut_list.append(extra)
    return cut_list


def year_data(stock, year):  # 0-open 1-close 2-high 3-close 4-volume 5-wave
    data_map = {}
    url = f'https://img1.money.126.net/data/hs/kline/day/history/{year}/{"0" if stock[0] == "6" else "1"}{stock}.json'
    res = requests.get(url)
    if res.status_code == 200:
        datas = res.json()['data']
        for data in datas:
            data_map[data[0]] = data[1:]
        return data_map
    else:
        print(f'{stock}.{year}.读取错误')
        return False
