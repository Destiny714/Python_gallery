import requests
import json
import datetime
import re
from threading import Thread
import random
import time
import schedule

x = True
y = False
z = True
# word = input('输入关键词')
word = 'VANS'
token = input('输入用户')
headers = {
    'Host': 'wechat.palace-skateboards.cn',
    'Connection': 'keep-alive',
    'token': token,
    'content-type': 'application/json',
    # 'Accept-Encoding': 'gzip,compress,br,deflate',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x1800072f) NetType/WIFI Language/zh_CN',
    'Referer': 'https://servicewechat.com/wx696ff953a85e38f9/12/page-frame.html'
}
skus = []
good_map = []
buy_list = []
aim_dict = {}


def get_skus(i):
    global skus
    global good_map
    good_url = 'https://wechat.palace-skateboards.cn/westore-palace-core/mini/product/query/{}'.format(i)
    req = requests.get(url=good_url, headers=headers)
    aim_detail = req.json()
    skus = aim_detail['data']['productSkuResults']
    sku_map = []
    for index, sku in enumerate(skus):
        product_id = sku['id']
        sku_map.append(product_id)
    # print(sku_map)
    good_map.append(sku_map)


def get_args():
    global buy_list, aim_dict, word
    aim_list = []
    order = []
    start_time = datetime.datetime.timestamp(datetime.datetime.now())
    url = 'https://wechat.palace-skateboards.cn/westore-palace-core/mini/product/queryAll'
    data = {
        "categoryId": 18,
        "pageSize": 20,
        "pageNum": 1
    }
    data = json.dumps(data)
    r = requests.post(url=url, headers=headers, data=data)
    query = r.json()
    if query['success'] is True:
        goods = query['data']['result']
        # print(goods)
        for good in goods:
            name = good['name']
            # print(name)
            key = re.findall(r'%s' % word, name)
            # print(key)
            if key:
                aim_list.append(good['id'])
        # print(aim_list)
        if aim_list:
            threads = []
            for good_id in aim_list:
                thread = Thread(target=get_skus, args=[good_id])
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
            # print(good_map)
            for index, value in enumerate(aim_list):
                aim_dict[aim_list[index]] = good_map[index]
            # print(aim_dict)
            for i in aim_dict:
                order.append([i, aim_dict[i][random.randint(0, len(aim_dict[i]) - 1)]])
            print('下单参数:', order)
            end_time = datetime.datetime.timestamp(datetime.datetime.now())
            _delta = end_time - start_time
            print('Search Finished in', _delta, 'sec')
            # print('下单参数为:', good_map)
        else:
            print('未找到商品，继续搜索', datetime.datetime.now())
    else:
        print('错误:', query['message'])
        exit()
    return order


def cop(product_id, sku_id):
    start = datetime.datetime.timestamp(datetime.datetime.now())
    url = 'https://wechat.palace-skateboards.cn/westore-palace-core/mini/order/add'
    data = {  # 自己改参数
        "email": "",
        "payFirstName": "",
        "payLastName": "",
        "payIdNum": "",
        "payerPhone": "",
        "deliveryFirstName": "",
        "deliveryLastName": "",
        "deliveryIdNum": "",
        "deliveryMobile": "",
        "province": "",
        "city": "",
        "district": "",
        "postcode": "",
        "address": "",
        "createOrderType": 1,
        "productId": product_id,
        "productSkuId": sku_id
    }
    data = json.dumps(data)
    r = requests.post(url=url, headers=headers, data=data)
    if r.json()["success"] is True:
        end = datetime.datetime.timestamp(datetime.datetime.now())
        use_time = end - start
        print(r.text, 'Cop Finished in', use_time, 'sec')
        exit()
    else:
        print(r.json()["message"])


def main_start():
    time_start = datetime.datetime.timestamp(datetime.datetime.now())
    ths = []
    orders = get_args()
    if orders:
        for _ in orders:
            th = Thread(target=cop, args=[_[0], _[1]])
            th.start()
            ths.append(th)
        for th in ths:
            th.join()
        time_end = datetime.datetime.timestamp(datetime.datetime.now())
        time_use = time_end - time_start
        print('Main Finished in', time_use, 'sec')
    # else:
    #     print('无可下单目标')


while x:
    z = False
    time1 = datetime.datetime(2021, 7, 3, 11, 00, 00)
    tm1 = datetime.datetime.timestamp(time1)
    time2 = datetime.datetime.now()
    tm2 = datetime.datetime.timestamp(time2)
    delta = tm1 - tm2
    if delta <= 5:
        x = False
        y = True

while y:
    main_start()
    time.sleep(1)


# print('倒计时开始')
# schedule.every().day.at('10:59:50').do(set_time)
# while z:
#     schedule.run_pending()
#     time.sleep(1)
