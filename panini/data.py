# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/9 21:27
# @Author  : Destiny_
# @File    : data.py
import json
import random


class randomData:

    def __init__(self):
        self.__firstName = ['段', '王', '魏', '徐', '朱', '吴', '李', '莫', '萧', '许', '何', '陈', '张', '章', '秦', '林', '范']
        self.__lastName = ['子', '伊', '岚', '卿', '轩', '佩', '伟', '焕', '浩', '彦', '天', '昊', '皓', '越', '静', '欧', '杰', '明',
                           '栋', '凡', '光', '邦', '一', '诺', '雨', '心', '亦']
        self.tels = ['', '', '', '', '', '', '']
        self.details = ['', '', '', '']

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

    def data(self, cmdtID, specID, count):
        model = {
            "DeliverCity": "宁波市",
            "SpecsID": specID,
            "DeliverArea": "海曙区",
            "DeliverProv": "浙江省",
            "DeliverMobile": self.randomTel(),
            "PreviewType": "1",
            "CommodityID": cmdtID,
            "Count": count,
            "CRID": "",
            "DeliverName": self.randomName(),
            "DeliverStreet": self.randomDetail()
        }
        model = json.dumps(model)
        return model
