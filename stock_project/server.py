# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/8 09:41
# @Author  : Destiny_
# @File    : server.py
import json
import verify
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    msg = {'type':'string','msg':'Hello World!'}
    msg = json.dumps(msg)
    return msg


@app.route('/start')
def start():
    if verify.status in ['init','finish']:
        verify.main_varify()
        msg = {'type': 'string', 'msg': '运行完毕'}
        msg = json.dumps(msg)
        return msg
    else:
        msg = {'type': 'string', 'msg': '正在运行'}
        msg = json.dumps(msg)
        return msg


@app.route('/result')
def result():
    if verify.status == 'finish':
        msg = {'type':'list','msg':verify.stockNos}
        msg = json.dumps(msg)
        return msg
    elif verify.status == 'init':
        msg = {'type': 'string', 'msg': '请先运行程序'}
        msg = json.dumps(msg)
        return msg
    else:
        msg = {'type': 'string', 'msg': '正在运行'}
        msg = json.dumps(msg)
        return msg


if __name__ == '__main__':
    app.run()
