# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# @author : Destiny_
# @file   : Concurrent.py
# @time   : 2022/03/08
import threadpool


def multi(some, arg):
    pool = threadpool.ThreadPool(20 if len(arg) > 20 else len(arg))
    tasks = threadpool.makeRequests(some, arg)
    [pool.putRequest(task) for task in tasks]
    pool.wait()
