# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/9 20:52
# @Author  : Destiny_
# @File    : main.py

import json
import time
import data
import utils
import random
import datetime
import schedule
import requests
import warnings
import threading

warnings.filterwarnings('ignore')


class info:
    def __init__(self, sessionKey):
        self.inits = {}
        self.infos = {}
        self.QBID = None
        self.start = False
        self.answer = False
        self.available = []
        self.sellTime = None
        self.startTime = None
        self.headers = utils.headers
        self.detailUrl = f'https://panini.xcx-x.com/shop/Api/Commodity/GetCommodityInfo?SessionKey={sessionKey}'

    def detail(self, cmdtID):
        self.inits = {}
        self.infos = {}
        self.available = []
        detailData = {"CommodityID": cmdtID}
        response = requests.post(url=self.detailUrl, data=json.dumps(detailData), headers=self.headers, verify=False,
                                 timeout=30)
        if response.status_code == 200:
            response = response.json()
            if response['code'] != 0:
                print(f'请求错误---{response["message"]}')
                exit()
            else:
                response = response['data']
                units = response['SpecsList']
                self.inits['name'] = response['Name']
                self.inits['cmdtID'] = response['CommodityID']
                self.inits['vipBuy'] = response['IsPriorityBuy']

                self.QBID = response['QBID']
                self.answer = response['IsQuestionRight']
                self.start = utils.isStart(response['LaunchTime'])
                self.startTime = utils.toTimeStamp(response['LaunchTime'])
                self.sellTime = utils.toTimeStamp(response['LastCanBuyTime'])
                self.startTime = max(self.startTime, self.sellTime)
                self.inits['limitBuy'] = response['QuotaCount'] if response['QuotaCount'] < count else count
                for unit in units:
                    unitInfo = {'specID': unit['ID'], 'canBuy': unit['IsCanBuy'], 'name': unit['Name'], 'price': unit[
                        'UnitPrice'], 'stock': unit['MaxCount']}
                    if unitInfo['stock'] > 0:
                        self.available.append(unitInfo['specID'])
                    self.infos[unitInfo['specID']] = unitInfo
        else:
            print(f'解析错误---{response.status_code}')
            print(response.text)
            exit()


class cop:

    def __init__(self, cmdtID, users: list):
        self.count = count
        self.users = users
        self.cmdtID = cmdtID
        self.headers = utils.headers
        self.buyUrl = 'https://panini.xcx-x.com/shop/Api/Order/OrderConfirm?SessionKey='

    def url(self, sessionKey):
        return f'{self.buyUrl}{sessionKey}'

    def buy(self, sessionKey, specID):
        start = time.time()
        buyData = data.randomData().data(
            cmdtID=self.cmdtID, specID=specID, count=self.count)
        response = requests.post(url=self.url(
            sessionKey), data=buyData, headers=self.headers, verify=False, timeout=30)
        use = time.time() - start
        if response.status_code == 200:
            response = response.json()
            code = response['code']
            message = response['message']
            print(
                f'抢购响应--{code}---抢购结果--{message}--下单时间--{datetime.datetime.now()}--用时--{round(use * 1000, 3)}ms')
        else:
            print(f'抢购结果解析错误---{response.status_code}')
            print(response.text)

    def multiBuy(self, specID):
        threads = []
        for user in self.users:
            thread = threading.Thread(target=self.buy, args=[user, specID])
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def countDown(self, start, specID):
        onCount = True
        while onCount:
            diff = start - time.time()
            if diff <= lagTime:
                onCount = False
                self.multiBuy(specID)

    def prepare(self, start, specID):
        schedule.every().day.at(utils.toTimeStr(start - 5)
                                ).do(self.countDown, start, specID)
        while True:
            schedule.run_pending()
            print(f'倒计时{int(start - time.time())}秒')
            time.sleep(1)


if __name__ == '__main__':
    index = 0
    count = 1  # limitBuy
    lagTime = 0.1
    cmdtid = '584656432696131592'  # spu
    sessionKeys = [  # users
        'S_Panini_Shop_afcb02f3-b9c7-4d61-8f90-d2294402a624',
        'S_Panini_Shop_2f47a7bf-4c8f-42f7-8018-10f709870b89',
        'S_Panini_Shop_ceb8c239-f637-47a6-94ff-4b22374c0749',
        'S_Panini_Shop_a5bc431d-eb1c-4ae9-9fcb-ccc05c722be0',
    ]
    info = info(sessionKeys[0])
    cop = cop(cmdtID=cmdtid, users=sessionKeys)
    QBID = info.QBID
    info.detail(cmdtid)
    print(f'下单数量:{info.inits["limitBuy"]}')
    if info.start:
        print('已开售---补货模式')
        while True:
            info.detail(cmdtid)
            if info.available:
                for one in info.available:
                    print(
                        f'{info.infos[one]["name"]}:{info.infos[one]["stock"]}')
                if index:
                    specid = info.available[index - 1]
                else:
                    specid = random.choice(info.available)
                cop.multiBuy(specid)
            else:
                print(f'不满足下单条件---{info.infos}')
            time.sleep(1)
    else:
        print('未开售---倒计时模式')
        print(f'开售时间{utils.toTimeStr(info.startTime)}')
        if len(info.infos) > 1:
            for oneInfo in info.infos:
                print(info.infos[oneInfo])
            index = int(input('选择第几项:')) - 1
        else:
            print(info.infos)
            index = 0
        cop.prepare(info.startTime, info.available[index])
