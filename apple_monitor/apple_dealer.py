# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/30 3:29 下午
# @Author  : Destiny_
# @File    : apple_dealer.py

import re
import time
import requests
import threading


headers = {
        'Authorization': '',
        'authorizer-appid': 'wxc7512a58761797da',
        'content-type': 'application/json',
        'Accept-Encoding': 'gzip,compress,br,deflate',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.14(0x18000e26) NetType/WIFI Language/zh_CN'
    }


def bark_pusher(title,content):
    url = f'https://api.day.app/{bark_id}/{title}/{content}'
    requests.get(url)


def get_stores(_city):
    url = f'https://aar.yuanyuanke.cn/api/h5app/wxapp/distributor/getdistributorstock?page=1&pageSize=40&goods_id=&lat=&lng=&sel_city={_city}&item_id={spu}&source_from=plantform&name=&company_id=1'
    res = requests.get(url=url, headers=headers)
    try:
        res = res.json()
        shop_list = res['data']['list']
        for shop_detail in shop_list:
            shop_name = shop_detail['name']
            store_list.append(shop_name)
            need_push_status[shop_name] = True
        if not store_list:
            print('城市无店铺')
            exit()
    except Exception as e:
        bark_pusher('城市错误',str(e))
        print('城市错误',e)
        exit()


def refresh_stock(_city, _sku):
    url = f'https://aar.yuanyuanke.cn/api/h5app/wxapp/distributor/getdistributorstock?page=1&pageSize=40&goods_id=&lat=&lng=&sel_city={_city}&item_id={_sku}&source_from=plantform&name=&company_id=1'
    try:
        res = requests.get(url=url, headers=headers)
        res = res.json()
        shop_list = res['data']['list']
        for shop_detail in shop_list:
            shop_name = shop_detail['name']
            is_have_store = shop_detail['is_have_store']
            if is_have_store:
                if shop_name in store_list:
                    available_store[shop_name].append(sku_name_map[_sku])
                else:
                    append_list.append(shop_name)
    except Exception as e:
        # bark_pusher('刷新店铺发生错误', str(e))
        print('刷新店铺发生错误,暂停30s', e)
        time.sleep(30)
        pass


def get_sku(_spu):
    url = f'https://aar.yuanyuanke.cn/api/h5app/wxapp/goods/items/{spu}?goods_id={_spu}&company_id=1'
    res = requests.get(url=url,headers=headers)
    try:
        res = res.json()
        items = res['data']['spec_items']
        item_name = res['data']['item_name']
        for item in items:
            good_sku = item['item_id']
            color = item['item_spec'][0]['spec_value_name']
            storage = item['item_spec'][1]['spec_value_name']
            if re.search(r'128|256',storage):
                device_name = f'{item_name} {color} {storage}'
                sku_name_map[good_sku] = device_name
    except Exception as e:
        bark_pusher('读取发生错误', str(e))
        print('读取发生错误', e)
        pass


def refresh_all():
    threads = []
    for sku in sku_name_map:
        thread = threading.Thread(target=refresh_stock, args=[city, sku])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    bark_pusher('授权店监控开启', '测试推送成功')
    bark_id = ''
    spu = 420
    city = '杭州市'
    store_list = []
    append_list = []
    sku_name_map = {}
    available_store = {}
    need_push_status = {}
    get_sku(spu)
    get_stores(city)
    while True:
        if append_list:
            for _ in append_list:
                if _ not in store_list:
                    store_list.append(_)
                    need_push_status[_] = True
        append_list = []
        available_store = {}
        for store in store_list:
            available_store[store] = []
        refresh_all()
        for valid_store in available_store:
            valid_device = available_store[valid_store]
            if need_push_status[valid_store]:
                if valid_device:
                    push_device = str(valid_device).replace('[','').replace(']','').replace("'","")
                    bark_pusher(str(valid_store),push_device)
                    need_push_status[valid_store] = False
                else:
                    pass
            else:
                if valid_device:
                    pass
                else:
                    need_push_status[valid_store] = True
        time.sleep(5)
