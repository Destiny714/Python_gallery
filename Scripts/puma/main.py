# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# @author : Destiny_
# @file   : main.py
# @time   : 2022/02/18
import time
import json
import data
import utils
import warnings
import requests
import schedule
import datetime
import threading

warnings.filterwarnings('ignore')


class detail:
    def __init__(self, spu):
        self.inits = {'spu': spu}
        self.skus = []
        self.url = 'https://api-cn.puma.com/pumacn/product/get/item/detail/by/spu.do'
        self.data = {
            "spuCode": spu,
            "storeCode": "2003164189",
            "channelCode": 100
        }

    def refresh(self):
        res = requests.post(url=self.url, data=json.dumps(self.data), headers=utils.header(), verify=False)
        if res.status_code == 200:
            res = res.json()['data']
            self.inits['price'] = res['spuSalePrice']
            self.inits['img'] = res['spuImageList'][0]['mediaUrl']
            self.inits['name'] = res['spuTitle']
            self.inits['color'] = res['spuAttrSaleList'][0]['attributeValueList'][0]['attributeValueName']
            skuList = res['skuList']
            for skuDetail in skuList:
                if skuDetail['skuNetQty'] >= num:
                    size = float(skuDetail['attrSaleList'][1]['attributeValueList'][0]['attributeValueName'])
                    if minSize <= size <= maxSize:
                        self.skus.append(
                            {'size': float(skuDetail['attrSaleList'][1]['attributeValueList'][0]['attributeValueName']),
                             'sku': skuDetail['skuCode'],
                             'stock': skuDetail['skuNetQty']})
        else:
            print(f'商品读取{res.status_code}错误')
            exit()


class cop:
    def __init__(self):
        self.url = 'https://api-cn.puma.com/pumacn/mall/trade/createOrder'

    def createOrder(self, init, skus, token):
        buyData = data.randomData(num=num).buyData(init=init, skus=skus)
        header = utils.header(token=token)
        res = requests.post(url=self.url, data=buyData, headers=header, verify=False)
        if res.status_code == 200:
            res = res.json()
            code = res['code']
            if code == '0':
                schedule.clear()
                print(f'下单成功,下单时间:{res["data"]["orderTime"]}')
                exit()
            else:
                print(f'下单失败,原因:{res["message"]}')
        else:
            print(f'下单失败:{res.status_code}错误--{res.text}')

    def multiBuy(self, init, skus):
        threads = []
        for token in tokens:
            thread = threading.Thread(target=self.createOrder, args=[init, skus, token])
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def countDown(self, init, skus):
        onCount = True
        while onCount:
            diff = startTimeStamp - time.time()
            if diff <= lagTime:
                onCount = False
                self.multiBuy(init, skus)

    def prepare(self, init, skus):
        schedule.every().day.at(utils.toTimeStr(startTimeStamp - 5)
                                ).do(self.countDown, init, skus)
        schedule.every().day.at(utils.toTimeStr(startTimeStamp + 3)
                                ).do(self.countDown, init, skus)
        while time.time() < startTimeStamp + 5:
            schedule.run_pending()
            print(f'{"倒计时" if time.time() < startTimeStamp else "开售"}{abs(int(startTimeStamp - time.time()))}秒')
            time.sleep(1)


if __name__ == '__main__':
    tokens = [
        'e48758af82907b00004903f6ac0644948f736c5cf',
        'ae8878088ba08607d04a0de68f07d078dc3efe388',
        '208b682a82002705c04203e68e054bfa17bd61c28',
        '4a8a787b8e70d10bd0470c56a800c698b06729033',
        # '1a8a68798390a00c3040009680067009a2e1444a0',
        # '8e8c08a682101709e04a09068402ec8b3f9826906'
    ]
    # tokens = [
    #     '3a81f81e8ae0a60ae04305d6bd0c68676ede13333',
    #     'db8358e28640eb01004d0b268a0ffe0260a51183b',
    #     '4a8898798db0ce08a04c0b26aa003994787b1f54a',
    # ]
    startTime = '2022-02-19 10:00:00'
    startTimeStamp = utils.toTimeStamp(startTime)
    lagTime = 0.35
    minSize = 43
    maxSize = 46
    num = 1
    spuCode = '37668201'
    info = detail(spuCode)
    cop = cop()
    info.refresh()
    print(info.inits)
    if startTimeStamp > time.time():
        print('倒计时模式')
        cop.prepare(info.inits, info.skus)
    else:
        print('补货模式')
        while True:
            info.refresh()
            if len(info.skus) > 0:
                print(info.skus)
                cop.multiBuy(info.inits, info.skus)
                break
            else:
                print(f'正在刷新商品----{datetime.datetime.now()}')
            time.sleep(0.5)
