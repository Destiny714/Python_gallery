# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/30 3:29 下午
# @Author  : Destiny_
# @File    : apple_dealer.py

import time
import requests
import warnings
import datetime
from push import bark_pusher
warnings.filterwarnings('ignore')


def refresh_store(_models:list):
    global normal
    url = 'https://www.apple.com.cn/shop/fulfillment-messages?pl=true&mt=compact&searchNearby=true&store=R531'
    for no,_model in enumerate(_models):
        url += f'&parts.{no}={_model}'
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        'accept-language': 'zh-cn'
    }
    try:
        res = requests.get(url=url, headers=headers, verify=False,timeout=15)
        if res.status_code != 200:
            bark_pusher('监控出现问题',res.status_code)
        r = res.json()
        stores_info = r['body']['content']['pickupMessage']['stores']
        for store_info in stores_info:
            store_name = store_info['storeName']
            device_list = store_info['partsAvailability']
            for device_model in device_list:
                device_info = device_list[device_model]
                device_model_name_map[device_model] = device_info['storePickupProductTitle']
                pickup_status = device_info['pickupDisplay']
                if pickup_status == 'available':
                    available_store[device_model].append(store_name)
    except Exception as e:
        print(e)
        bark_pusher('监控出现错误', str(e))
        pass


if __name__ == '__main__':
    bark_pusher('官网监控开启', '测试推送成功')
    normal = True
    models = ['MLHG3CH/A', 'MLHC3CH/A', 'MLHL3CH/A', 'MLH83CH/A', 'MLHD3CH/A', 'MLHH3CH/A', 'MLH93CH/A', 'MLHE3CH/A', 'MLHJ3CH/A', 'MLHA3CH/A', 'MLHF3CH/A', 'MLHK3CH/A']
    need_push_status = {}
    for model in models:
        need_push_status[model] = True
    while normal:
        available_store = {}
        device_model_name_map = {}
        for model in models:
            available_store[model] = []
        refresh_store(models)
        try:
            for _device_model in available_store:
                name = device_model_name_map[_device_model]
                stores = available_store[_device_model]
                if need_push_status[_device_model]:
                    if stores:
                        print(f'{name}---{stores}---{datetime.datetime.now()}')
                        bark_pusher(name,str(stores).replace('[','').replace(']','').replace("'",""))
                        need_push_status[_device_model] = False
                    else:
                        pass
                else:
                    if stores:
                        pass
                    else:
                        need_push_status[_device_model] = True
        except Exception as error:
            bark_pusher('监控出现错误',error)
            pass
        time.sleep(2)
