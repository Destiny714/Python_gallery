# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/19 19:29
# @Author  : Destiny_
# @File    : thread_loop.py

import api
import time
import threading
import threadpool
from concurrent.futures import ThreadPoolExecutor, as_completed


def count(some):
    start = time.time()
    some()
    use = time.time() - start
    print(f'{str(some)}用时{use}ms')


def thread_pool(func, iterator, *args, thread_num=50):
    pool = threadpool.ThreadPool(thread_num)
    tasks = threadpool.makeRequests(func, iterator, *args)
    [pool.putRequest(_) for _ in tasks]
    pool.wait()


def thread_pool_executor(func, iterator, *args, thread_num=50):
    executor = ThreadPoolExecutor(max_workers=thread_num)
    tasks = [executor.submit(func, _, *args) for _ in iterator]
    for task in as_completed(tasks):
        task.result()


def multi(func, iterator, *args, thread_num=50):
    pieces = api.cut(iterator, thread_num)
    for piece in pieces:
        threads = []
        for one in piece:
            thread = threading.Thread(target=func, args=[one, *args])
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
