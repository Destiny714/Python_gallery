# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/22 18:47
# @Author  : Destiny_
# @File    : api_get.py

import time
import requests
import threading
import sql_action

caches = []


def check_price(stock: str, yesterday):
    if stock[0] == '6':
        _stock = f'0{stock}'
    else:
        _stock = f'1{stock}'
    url = f'http://img1.money.126.net/data/hs/time/today/{_stock}.json'
    r = requests.get(url).json()['data']
    prices = [float(_[1]) for _ in r]
    high_price = max(prices)
    open_price = sql_action.SQL().select_yesterday_close_price(yesterday, stock)
    close_price = r[-1][1]
    percent = (close_price / open_price - 1) * 100
    percent = round(percent, 3)
    high_percent = (high_price / open_price - 1) * 100
    high_percent = round(high_percent, 3)
    if percent >= 0:
        print(f'现价---{stock}---涨---%{percent}')
    elif percent < 0:
        print(f'现价---{stock}---跌---%{-percent}')
    if high_percent >= 0:
        print(f'高点---{stock}---涨---%{high_percent}')
    elif high_percent < 0:
        print(f'高点---{stock}---跌---%{-high_percent}')


def check_prices(stocks: list, yesterday):
    for stock in stocks:
        print(stock)
        check_price(stock, yesterday)


def get_range(no, start, end):
    print(f'downloading---{no[1:]}---ing')
    url = f'http://quotes.money.163.com/service/chddata.html?code={no}&start={start}&end={end}&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
    r = requests.get(url, stream=True)
    caches.append({'no': no[1:], 'content': r.content})
    print(f'downloading---{no[1:]}---down')


def get_one_day(no, day: str):
    url = f'http://img1.money.126.net/data/hs/kline/day/history/2021/{"0" if no[0] == "6" else "1"}{no}.json'
    r = requests.get(url)
    if r.status_code == 200:
        r = r.json()['data']
        for one in r:
            if one[0] == day.replace('-', ''):
                _open = one[1]
                close = one[2]
                high = one[3]
                low = one[4]
                volume = one[5]
                data = {'date': day, 'open': _open, 'close': close, 'high': high, 'low': low, 'volume': volume}
                return data
    else:
        print(f'{no} {r.status_code}')


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


def multi_download(items: list, start: str, end: str):
    threads = []
    for item in items:
        thread = threading.Thread(target=get_range, args=(item, start, end))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def download(piece: int):
    global caches
    sql = sql_action.SQL()
    full_list = sql.download_nos()
    big_list = cut(full_list, piece)
    for small_list in big_list:
        new_list = []
        for _ in small_list:
            new_list.append(_)
        multi_download(new_list, '20210915', '20211209')
        if len(caches) >= 20:
            for cache in caches:
                with open(f'data/{cache["no"]}.csv', 'wb') as f:
                    print(f'write---{cache["no"]}')
                    f.write(cache['content'])
            caches = []
        time.sleep(1)


def formal_trade_day():
    url = 'http://img1.money.126.net/data/hs/kline/day/times/1399001.json'
    r = requests.get(url).json()
    dates = r['times']
    return dates


def get_holiday(year: str):
    # 0 工作日 1 假日 2 节日
    sql = sql_action.SQL()
    cursor = sql.cursor
    url = f'http://tool.bitefu.net/jiari?back=json&d={year}'
    r = requests.get(url).json()
    holiday_map = r[year]
    for _ in holiday_map.keys():
        date = f'{year}-{str(_)[:2]}-{str(_)[2:]}'
        cursor.execute(f'INSERT INTO holiday (holiday) VALUES ("{date}")')
    sql.db.commit()
