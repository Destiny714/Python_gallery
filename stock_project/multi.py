# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/30 13:48
# @Author  : Destiny_
# @File    : multi.py

import time
import api_get
import threading
import data_read
import sql_action
import find_point
import date_handler
from concurrent.futures import ThreadPoolExecutor, as_completed

stock_map = {}
today = date_handler.today()


def thread_pool_executor(iterable, function):
    executor = ThreadPoolExecutor(max_workers=50)
    tasks = [executor.submit(function, one) for one in iterable]
    for task in as_completed(tasks):
        task.result()


def multi(piece, func, *args):
    threads = []
    for one in piece:
        thread = threading.Thread(target=func, args=[one, *args])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def multi_find_triangle(stock_maps):
    results = []

    def find_one_triangle(detail_list):
        print(detail_list[0])
        result = find_point.triangle(detail_list[1], today)
        if result:
            results.append(detail_list[0])

    new_list = []
    for stock in stock_maps:
        new_list.append([stock, stock_maps[stock]])
    thread_pool_executor(new_list, find_one_triangle)
    return results


def refresh_one_stock(no):
    new_sql = sql_action.SQL()
    r = new_sql.select(f'No{no}')
    stock_map[no] = r
    new_sql.close()


def refresh_stock_map(stocks: list):
    global stock_map
    print('正在读取股票每日数据……')
    start = time.time()
    stock_map = {}
    stocks_pieces = api_get.cut(stocks, 100)
    for stocks_piece in stocks_pieces:
        multi(stocks_piece, refresh_one_stock)
    use = int(time.time() - start)
    count = 0
    for _ in stock_map:
        d = stock_map[_]
        for __ in d:
            count += 1
    print(f'股票每日数据读取完毕,共{count}条数据,用时{use}秒')
    return stock_map


def update_detail(stock_detail):
    sql = sql_action.SQL()
    sql.update_detail(stock_detail)
    sql.db.commit()
    sql.close()


def update_all_detail(stock_details):
    pieces = api_get.cut(stock_details, 100)
    for piece in pieces:
        multi(piece, update_detail)


def insert_detail(stock_detail):
    sql = sql_action.SQL()
    sql.insert_detail(stock_detail)
    sql.db.commit()
    sql.close()


def insert_all_detail(stock_details):
    pieces = api_get.cut(stock_details, 100)
    for piece in pieces:
        multi(piece, insert_detail)


def read_excel_and_write_one(data, stockNos):
    sql = sql_action.SQL()
    try:
        if data['no'] in stockNos:
            r = sql.select(f'No{data["no"]}')
            if len(r) != 0:
                date = r[-1][1]
                if date == today:
                    sql.update_stock_data_from_excel(data)
                else:
                    sql.insert_stock_data_from_excel(data)
            else:
                sql.insert_stock_data_from_excel(data)
        else:
            sql.create_single_stock_db(f"{data['no']}")
            sql.insert_stock_data_from_excel(data)
        sql.db.commit()
        sql.close()
    except Exception as e:
        print(e)
        sql.db.rollback()


def read_excel_and_write():
    stockNos = sql_action.SQL().tables()
    datas = data_read.READ().excel_write_data(f'{today}.xlsx')
    pieces = api_get.cut(datas, 50)
    for piece in pieces:
        multi(piece, read_excel_and_write_one, stockNos)
