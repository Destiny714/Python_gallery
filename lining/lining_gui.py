import json
import time
import random
import requests
import datetime
import warnings
import threading
import lining_tokens
from tkinter import *

# man_weiwu = '3748293'
# woman_weiwu = '3723286'
# spuid_list = [['男款', man_weiwu], ['女款', woman_weiwu], ['test', '3980350']]
# print(spuid_list)
# spuid = spuid_list[int(input('选择监控第几个商品:')) - 1][1]

spuid = '3980350'
price = '119900'

num_list = {}
goods_map = []
success_list = []
available_list = []
user_address_map = []
have_create = True

warnings.filterwarnings("ignore")
token_list = lining_tokens.token_list
for _token in token_list:
    num_list[_token] = 1


def get_goods_map(spu_id):
    global goods_map, price, n
    goods_map = []
    detail_url = 'https://api.store.lining.com/goodsg/v1/goods-jh-query/spu/detail'
    headers = {
        'Host': 'api.store.lining.com',
        'Connection': 'keep-alive',
        'auth-token': '',
        'content-type': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip,compress,br,deflate',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x18000731) NetType/WIFI Language/zh_CN',
    }
    detail_data = {
        "spuId": spu_id,
        "saasId": "8324992625302181585",
        "source": "2"
    }
    detail_data = json.dumps(detail_data)
    try:
        r = requests.post(url=detail_url, headers=headers, data=detail_data, verify=False, timeout=2)
        r = r.json()
        name = r['data']['spuVO']['title']
        sku_list = r['data']['spuVO']['skuList']
        if_draw = r['data']['activityExtVO']
        if_on_shelf = r['data']['spuVO']['onShelf']
        if_available = r['data']['spuVO']['available']
        price = r['data']['spuVO']['spuPrice']['minSalePrice']
        can_buy = (not bool(if_draw)) and if_on_shelf and if_available
        for sku in sku_list:
            skuid_dict = {}
            skuid = sku['skuId']
            size = sku['skuSpecValueList'][0]['specValue']
            stock = sku['skuStock']['stockQuantity']
            skuid_dict['size'] = size
            skuid_dict['skuid'] = skuid
            skuid_dict['stock'] = stock
            goods_map.append(skuid_dict)
        if n == 0:
            if goods_map:
                text_box.insert(END, f'读取商品成功 \n{name} \n')
            else:
                text_box.insert(END, '读取商品失败，请重试 \n')
        n += 1
        # print(goods_map)
        return can_buy
    except Exception as error:
        print(error)
        return False


def get_available_and_have_stock_sku(spu_id):
    global available_list
    available_list = []
    available_stock = []
    if get_goods_map(spu_id):
        for _ in goods_map:
            if int(_['stock']) > 0:
                available_stock.append({_['size']: _['stock']})
                available_list.append(_['skuid'])
        if available_list:
            text_box.insert(END, ('有效商品:', str(available_stock).replace('{','').replace('}',''), datetime.datetime.now()))
            text_box.insert(END, '\n')
        else:
            text_box.insert(END, ('已上架,无库存,继续监控', datetime.datetime.now()))
            text_box.insert(END, '\n')
    else:
        text_box.insert(END, ('未满足下单条件,继续监控', datetime.datetime.now()))
        text_box.insert(END, '\n')


def random_sku():
    return available_list[random.randint(0, len(available_list) - 1)]


def get_address_map():  # 获取用户对应地址
    global user_address_map
    rubbish_list = []
    address_url = 'https://api.store.lining.com/tradeg/v2/settle/ln/getSettleDetail'
    for token in token_list:
        try:
            address_headers = {
                'auth-token': token,
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x18000731) NetType/WIFI Language/zh_CN',
                'accept-encoding': 'br, gzip, deflate',
                'referer': 'https://servicewechat.com/wxed8da13fbdfeb178/566/page-frame.html',
                'content-type': 'application/json;charset=utf-8'
            }
            add_data = {
                "settleScene": "INIT",
                "userAddress": {},
                "storeGoodsList": [{
                    "goodsList": [{
                        "spuId": spuid,
                        "skuId": goods_map[0]['skuid'],
                        "quantity": 1
                    }],
                    "saasId": "8324992625302181585"
                }],
                "marketingType": "NORMAL",
                "groupInfo": None,
                "ext": {},
                "saasId": "8324992625302181585",
                "source": "2"
            }
            address_data = json.dumps(add_data)
            res_address = requests.post(url=address_url, headers=address_headers, data=address_data, verify=False)
            address = res_address.json()
            if address['code'] != 'AUTH_FAIL':
                address_detail = address['data']['userAddress']
                user_address = {'token': token, 'address': address_detail}
                text_box.insert(END, (address_detail['phone'], address_detail['name']))
                text_box.insert(END, ' 读取地址成功 \n')
                user_address_map.append(user_address)
            else:
                rubbish_list.append(token)
        except Exception as e:
            text_box.insert(END, e)
            text_box.insert(END, '\n')
            rubbish_list.append(token)
    if rubbish_list:
        for rubbish in rubbish_list:
            token_list.remove(rubbish)


def cop(token, address):  # 下单
    global have_create, num_list
    start_time = datetime.datetime.timestamp(datetime.datetime.now())
    url = 'https://api.store.lining.com/tradeg/v2/settle/ln/createOrder'
    headers = {
        'auth-token': token,
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x18000731) NetType/WIFI Language/zh_CN',
        'accept-encoding': 'br, gzip, deflate',
        'content-type': 'application/json;charset = utf-8'
    }
    data = {
        "userAddress": address,
        "storeGoodsList": [{
            "goodsList": [{
                "spuId": spuid,
                "skuId": random_sku(),
                "quantity": 1
            }],
            "saasId": "8324992625302181585",
            "couponList": []
        }],
        "marketingType": "NORMAL",
        "payAmount": price,
        "totalDeliveryFee": "800",
        "groupInfo": None,
        "invoiceRequest": None,
        "ext": {
            "lnOrderChannel": "12580",
            "lnOrderType": "NORMAL",
            "lnOrderSource": "8"
        },
        "scene": "NORMAL",
        "saasId": "8324992625302181585",
        "source": "2"
    }
    data = json.dumps(data)
    # print(data)
    req = requests.post(url=url, headers=headers, data=data, verify=False)
    txt = req.json()
    success = txt['success']
    end_time = datetime.datetime.timestamp(datetime.datetime.now())
    use_time = round(end_time - start_time, 3)
    if not success:
        while num_list[token] <= 3:
            if num_list[token] == 1:
                text_box.insert(END,f'{address["phone"]} 抢购状态 {success} 抢购结果: {txt["msg"]} {datetime.datetime.now()} \n')
            if num_list[token] <= 3:
                time.sleep(1)
                req = requests.post(url=url, headers=headers, data=data, verify=False)
                txt = req.json()
                success = txt['success']
                message = txt['msg']
                text_box.insert(END,f'{address["phone"]} 抢购状态 {success} 抢购结果: {message} {datetime.datetime.now()} 补单%d次 \n' % num_list[token])
                num_list[token] += 1
        else:
            text_box.insert(END, f'{address["name"]} 补单失败 \n')
            have_create = False
            exit()
    else:
        order_no = txt['data']['orderNo']
        success_list.append([order_no, token])
        text_box.insert(END,f'{address["phone"]} 抢购状态===>{success} 订单号===>{order_no} 用时===>{use_time}s //{datetime.datetime.now()} \n')
        exit()


def create_orders():
    global have_create
    threads = []
    for _ in user_address_map:
        thread = threading.Thread(target=cop, args=[_['token'], _['address']])
        thread.start()
        threads.append(thread)
    # for thread in threads:
    #     thread.join()
    have_create = False
    if success_list:
        text_box.insert(END,f'success:{len(success_list)} \n')
        with open('success.txt', 'a') as f:
            for success in success_list:
                f.write(str(success) + '\n')


def main_course():
    if goods_map and user_address_map:
        while have_create:
            get_available_and_have_stock_sku(spuid)
            if available_list:
                create_orders()
            time.sleep(1)
    else:
        text_box.insert(END, '请获取商品详情或者用户地址 \n')


if __name__ == '__main__':
    n = 0
    window = Tk()
    window.title('Lining_BOT')
    window.geometry('1000x800')
    button_get_map = Button(window, text='获取商品详情', fg='black',command=lambda: get_goods_map(spuid))
    button_get_address = Button(window, text='获取用户地址', fg='black',command=get_address_map)
    button_start_monitor = Button(window, text='开始监控', fg='black',command=main_course)
    button_exit = Button(window, text='退出', fg='black',command=exit)
    text_box = Text(window, width=75, height=23, bg='white', font='12')
    button_get_map.place(relx=0.01, rely=0.01)
    button_get_address.place(relx=0.01, rely=0.1)
    button_start_monitor.place(relx=0.01, rely=0.2)
    button_exit.place(relx=0.01,rely=0.9)
    text_box.place(relx=0.25, rely=0.029)
    window.mainloop()
