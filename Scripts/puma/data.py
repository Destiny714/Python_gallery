# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/9 21:27
# @Author  : Destiny_
# @File    : data.py
import json
import random


class randomData:

    def __init__(self, num):
        self.num = num
        self.__firstName = ['段', '王', '魏', '徐', '朱', '吴', '李', '莫', '萧', '许', '何', '陈', '张', '章', '秦', '林', '范']
        self.__lastName = ['子', '伊', '岚', '卿', '轩', '佩', '伟', '焕', '浩', '彦', '天', '昊', '皓', '越', '静', '欧', '杰', '明',
                           '栋', '凡', '光', '邦', '一', '诺', '雨', '心', '亦']
        self.tels = ['', '', '', '', '', '', '']
        self.details = ['', '', '', '', '']
        self.test = ['1', '2', '3']

    def randomName(self):
        name = ''.join(
            [random.choice(self.__firstName), random.choice(self.__lastName), random.choice(self.__lastName)])
        return name

    def randomTel(self):
        tel = random.choice(self.tels)
        return tel

    def randomDetail(self):
        detail = random.choice(self.details)
        return detail

    def address(self):
        model = {
            "address": self.randomDetail(),
            "city": "330100",
            "cityName": "杭州市",
            "district": "330110",
            "districtName": "",
            "province": "330000",
            "provinceName": "浙江省",
            "familyName": "",
            "givenName": "",
            "mail": None,
            "mobile": self.randomTel(),
            "name": self.randomName(),
            "telephone": None,
            "zipCode": None,
            "validate": None
        }
        return model

    def buyData(self, init, skus):
        sku = random.choice(skus)
        data = {
            "uuid": None,
            "openId": "ox",
            "account": "",
            "amount": f"{init['price'] * self.num}",
            "coupon": 0,
            "discount": 0,
            "externalOrderId": "",
            "freePostage": 1,
            "freight": 0,
            "giftCard": 0,
            "isInvoice": 0,
            "memberLabelCode": 0,
            "orderActivityinfoInList": [],
            "orderDeductioninfoInList": [],
            "orderInvoiceIn": {
                "invoiceType": 31,
                "content": "明细",
                "type": "0",
                "taxCode": None,
                "company": "",
                "title": None
            },
            "orderProductInList": [
                {
                    "activityCode": "20301095990676505865",
                    "attribute": f"颜色:{init['color']}|尺码:法国码 {sku['size']}",
                    "brandCode": "BR2019032100000005",
                    "brandName": "PUMA&CN",
                    "categoryCode": "22021400000032",
                    "categoryName": "限时特惠专区",
                    "count": self.num,
                    "customReqDesc": "string",
                    "customReqImage": "string",
                    "groupId": "",
                    "image": init['img'],
                    "isGift": 0,
                    "lineCode": 0,
                    "mainSkuId": "",
                    "marketPrcie": init['price'],
                    "model": "",
                    "omsCode": "0",
                    "productTags": [],
                    "promoPrice": init['price'],
                    "restrictItem": 0,
                    "returnType": "11",
                    "sellPrice": init['price'],
                    "skuId": sku['sku'],
                    "skuName": init['name'],
                    "spuCode": init['spu'],
                    "staffItem": 0,
                    "tax": 0
                }
            ],
            "orderReceiptInfoIn": self.address(),
            "orderType": "11",
            "payMent": "weixin",
            "productAmount": init['price'] * self.num,
            "remarkBuyer": "",
            "tax": 0,
            "terminal": "51",
            "user": "",
            "userId": "",
            "wishCard": "",
            "storeCode": "2003164189",
            "channelCode": 100
        }
        return json.dumps(data)
