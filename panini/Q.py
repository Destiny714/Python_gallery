# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# @author : Destiny_
# @file   : Q.py
# @time   : 2022/03/04

import json
import time
import utils
import random
import requests
import threading


class question:
    def __init__(self):
        self.QBID = QBID
        self.headers = utils.headers

    def getQuestion(self, sessionKey):
        url = f'https://panini.xcx-x.com/shop/Api/Commodity/GetOneQuestion?SessionKey={sessionKey}'
        res = requests.post(url=url, headers=self.headers, data=json.dumps({"QBID": self.QBID}))
        if res.status_code == 200:
            res = res.json()
            QBQID = res['data']['QBQID']
            options = res['data']['OptionList']
            option = random.choice(options)['OptionID']
            return {'QBQID': QBQID, 'option': option}
        else:
            return None

    def answerQuestion(self, sessionKey):
        url = f'https://panini.xcx-x.com/shop/Api/Commodity/QuestionBankRecord?SessionKey={sessionKey}'
        answer = self.getQuestion(sessionKey)
        answerData = {
            "OptionID": answer['option'],
            "QBID": self.QBID,
            "QBQID": answer['QBQID'],
            "CommodityID": cmdtid
        }
        res = requests.post(url=url, headers=self.headers, data=json.dumps(answerData))
        if res.status_code != 200:
            print(f'答题出错了,{res.status_code}')
            return False
        else:
            if res.json()['code'] != 0:
                print(f'答题错误:{res.json()["message"]}')
                time.sleep(0.5)
                self.answerQuestion(sessionKey)
            else:
                print('答题正确')
                return True

    def multiAnswer(self):
        for sessionKey in sessionKeys:
            thread = threading.Thread(target=self.answerQuestion, args=[sessionKey])
            thread.start()


if __name__ == '__main__':
    QBID = '585374640935796752'
    cmdtid = '584656432696131592'
    sessionKeys = [  # users
        'S_Panini_Shop_afcb02f3-b9c7-4d61-8f90-d2294402a624'
    ]
    question().multiAnswer()
