# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/19 19:29
# @Author  : Destiny_
# @File    : thread_loop.py

import time
import multi
import api_get
import threadpool
import sql_action
from concurrent.futures import ThreadPoolExecutor, as_completed

stocks = sql_action.SQL().tables()


def count(some):
    start = time.time()
    some()
    use = time.time() - start
    print(use)


def query(stock):
    sql = sql_action.SQL()
    sql.select(f'No{stock}')
    print(f'{stock} done')
    sql.close()


def thread_pool():
    pool = threadpool.ThreadPool(50)
    querys = threadpool.makeRequests(query, stocks)
    [pool.putRequest(sql) for sql in querys]
    pool.wait()


def thread_pool_executor(func,iterable,thread_num=50):
    executor = ThreadPoolExecutor(max_workers=thread_num)
    tasks = [executor.submit(func, _) for _ in iterable]
    for task in as_completed(tasks):
        task.result()


@count
def threading():
    pieces = api_get.cut(stocks, 50)
    for piece in pieces:
        multi.multi(piece, query)
