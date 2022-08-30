import json
import time
import random
import hashlib
import requests
import datetime
import warnings
import C_stores
import threading

warnings.filterwarnings('ignore')

proxies = {'http': 'http://103.21.143.119:16817', 'https': 'http://103.21.143.119:16817'}
salt = 'PopMartminiApp1117'
version = '3.0.31'
no_stock = True
available_store = []
finished_openid = []
invalid_users = []
finish_list = []
limited = []


def md5(s):
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()


def get_sign(request_data: dict, Method, timestamp):
    encryption_data = {}
    for key in sorted(request_data.keys()):
        if Method == 'POST':
            encryption_data[key] = request_data[key]
        else:
            encryption_data[key] = str(request_data[key])
    encryption_data['version'] = version
    encryption_str = json.dumps(encryption_data, separators=(',', ':'), ensure_ascii=False) + salt + timestamp
    sign = md5(encryption_str)
    encryption_data['time'] = timestamp
    encryption_data['sign'] = sign
    if Method == 'POST':
        return encryption_data
    elif Method == 'GET':
        return sign
    else:
        print('Method Error')
        exit()


def header(openID):
    headers = {
        'content-type': 'application/json;charset=utf-8',
        'identity_code': openID,
        'Accept-Encoding': 'gzip,compress,br,deflate',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.13(0x18000d2c) NetType/WIFI Language/zh_CN',
    }
    return headers


def get_detail_url(good_id):
    ts = str(int(time.time_ns() / 1e6))
    data = {'goods_spu_id': good_id}
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/goods/v2/detail?goods_spu_id={}&version={}&sign={}&time={}'.format(
        data['goods_spu_id'], version, get_sign(data, 'GET', ts), ts)
    return url


def get_sell_time(good_id):
    res = requests.get(get_detail_url(good_id), headers=header(''), verify=False)
    try:
        res = res.json()
        sell_time = str(res['data']['sg_goods_spu']['sell_at'])
        sell_time = sell_time.split('+')[0].replace('Z', '')
        name = res['data']['sg_goods_spu']['name']
        if sell_time.split('-')[0] == '0001':
            print('{} 已开售'.format(name))
            return False
        else:
            timeArray = time.strptime(sell_time, '%Y-%m-%dT%H:%M:%S')
            timestamp = int(time.mktime(timeArray))
            if timestamp <= time.time():
                print('{} 已开售'.format(name))
                return False
            else:
                print('{} 开售时间为'.format(name), sell_time)
                return timestamp
    except Exception as e:
        print('Error', e)
        exit()


def get_stock(good_id, store_id, open_ids, buy_num: int):
    ts = str(int(time.time_ns() / 1e6))
    oi = random.choice(open_ids)
    orgdata = {
        "sku_ids": [good_id],
        "store_id": store_id,
        "openid": oi,
    }
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/goods/skus_inventory'
    try:
        headers = header(oi)
        res = requests.post(url, data=json.dumps(get_sign(orgdata, 'POST', ts)).replace(' ', ''), headers=headers,
                            verify=False, timeout=5)
        if res.status_code == 200:
            res = res.json()
            stock = res['data']['sku_inventorys'][0]['total_inventory']
            print(f'{C_stores.stores[store_id]}:{stock}')
            if stock >= buy_num:
                available_store.append(store_id)
                return True
            else:
                return False
        else:
            print('Error', res.status_code, res.json()['message'])
            pass
    except Exception as e:
        print(e)
        pass


def new_get_stock(goodid, storeid, open_ids):
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/shopping_cart/adjust'
    oi = random.choice(open_ids)
    data = {
        "goods_sku_id": goodid,
        "adjust_num": 1,
        "store_id": storeid,
        "openid": oi,
    }
    ts = str(int(time.time_ns() / 1e6))
    data = get_sign(data, 'POST', ts)
    res = requests.post(url=url, headers=header(oi), data=json.dumps(data).replace(' ', ''),proxies=proxies)
    try:
        res = res.json()
        if res['code'] == 1:
            print('出现库存',datetime.datetime.now())
            return True
        else:
            print(res['msg'],datetime.datetime.now())
            return False
    except Exception as e:
        print(res,e,datetime.datetime.now())
        return False


def get_all_stock(good_id, store_ids, open_ids: list, buy_num: int):
    global available_store, no_stock
    perm_store = available_store
    available_store = []
    start = time.time()
    threads = []
    for store_id in store_ids:
        thread = threading.Thread(target=get_stock, args=[good_id, store_id, open_ids, buy_num])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    if available_store and no_stock:
        end = time.time()
        use = round((end - start), 2)
        prt = []
        for _ in available_store:
            prt.append(C_stores.stores[_])
        print('{}秒查询到{}个有库存店铺'.format(use, len(available_store)), prt)
        no_stock = False
        if available_store != perm_store:
            return available_store
        else:
            return False
    elif available_store and (no_stock is False):
        end = time.time()
        use = round((end - start), 2)
        prt = []
        for _ in available_store:
            prt.append(C_stores.stores[_])
        print('{}秒查询到{}个始终有库存店铺'.format(use, len(available_store)), prt)
        if available_store != perm_store:
            return available_store
        else:
            return False
    elif (not available_store) and (no_stock is False):
        print('无库存1，继续监控', datetime.datetime.now())
        no_stock = True
        return False
    else:
        print('无库存2，继续监控', datetime.datetime.now())
        return False


def create_order(good_id, open_id, store_id, buy_num, timeout):
    orgdata = {
        "each_store_info": [{
            "settle_goods_list": [{
                "goods_sku_id": good_id,
                "settle_num": buy_num
            }],
            "ship_way": 3,
            "store_id": store_id,
            "user_address_id": 0
        }],
        "position": 1,
        "share_phone": "18766889666",
        "openid": open_id,
    }
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/order/create_v2'
    start = time.time()
    ts = str(int(time.time_ns() / 1e6))
    try:
        headers = header(open_id)
        res = requests.post(url, data=json.dumps(get_sign(orgdata, 'POST', ts)).replace(' ', ''), headers=headers,
                            verify=False, timeout=timeout)
        end = time.time()
        use = round((end - start) * 1000, 2)
        if res.status_code == 200 or 400:
            res = res.json()
            if res['code'] == 1:
                order_id = res['data']['source_order_no']
                finish_list.append([open_id, order_id, str(time.ctime()).split()[3], C_stores.stores[store_id]])

                # finished_openid.append(open_id)

                print('{}下单成功 in {}ms'.format(C_stores.stores[store_id], use), 'order_id-->', order_id,
                      datetime.datetime.now())
                return use
            elif res['code'] == 10015 and res['msg'] != ('订单内商品库存不足,请您重新核对' and '部分商品已下架'):

                # finished_openid.append(open_id)

                print(open_id, res['code'], res['msg'], datetime.datetime.now(), '{}ms'.format(use))
                return use
            else:
                print(open_id, res['code'], res['msg'], datetime.datetime.now(), '{}ms'.format(use))
                return use
        else:
            print(res.text)
            return None
    except Exception as e:
        print('Error', e)
        pass


def get_user_info(user_id):
    ts = str(int(time.time_ns() / 1e6))
    data = {
        'user_id': user_id
    }
    url = 'https://popvip.paquapp.com/miniapp/v2/wechat/getUserInfo/?user_id={}&sign={}&time={}&version={}'.format(
        data['user_id'], get_sign(data, 'GET', ts), ts, version)
    res = requests.get(url, headers=header(''), verify=False).json()['data']
    tel = res['phone']
    wxid = res['nickname']
    return {'电话': tel, '微信名': wxid}


def get_address(open_id):
    ts = str(int(time.time_ns() / 1e6))
    data = {'openid': open_id}
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/address/default?openid={}&version={}&sign={}&time={}'.format(
        data['openid'], version, get_sign(data, 'GET', ts), ts)
    res = requests.get(url, headers=header(open_id), verify=False, timeout=2)
    if res.status_code == 200:
        res = res.json()
        if res['code'] == 1:
            res = res['data']
            if res:
                user_info = {'tel': res['receiving_tel'], 'name': res['receiving_name'], 'id': res['user_id']}
                print(get_user_info(user_info['id']))
                return user_info
            else:
                print('无默认地址')
                return '无默认地址'
        else:
            print(res)
            invalid_users.append(open_id)
            return open_id
    else:
        if res.status_code == 429:
            invalid_users.append(open_id)
            limited.append(open_id)
            print('限流')
        else:
            print(res.text, res)


def get_order_info(open_id, order_no):
    ts = str(int(time.time_ns() / 1e6))
    data = {
        'source_order_no': order_no,
        'openid': open_id
    }
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/order/detail?source_order_no={}&openid={}&sign={}&time={}&version={}'.format(
        data['source_order_no'], data['openid'], get_sign(data, 'GET', ts), ts, version)
    res = requests.get(url, headers=header(open_id), verify=False).json()
    if res['data']['paid_order']:
        d = '已支付'
        return d
    else:
        create_time = str(res['data']['wait_pay_order']['sg_source_order']['created_at']).split('+')[0].replace('T',
                                                                                                                ' ')
        end_time = str(res['data']['wait_pay_order']['sg_source_order']['expect_cancel_at']).split('+')[0].replace('T',
                                                                                                                   ' ')
        timeArray = time.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        timestamp = int(time.mktime(timeArray))
        if timestamp > int(time.time()):
            status = '待付款'
        else:
            status = '已过期'
        mall = res['data']['wait_pay_order']['sg_order_list'][0]['store_name']
        mall_id = res['data']['wait_pay_order']['sg_order_list'][0]['store_id']
        d = {'订单生成时间': create_time, '订单过期时间': end_time, '提货商场': (mall_id, mall), '订单状态': status}
        return d


def cancel_orders(open_id, order_no):
    ts = str(int(time.time_ns() / 1e6))
    data = {
        "cancel_select_reason": 1,
        "is_readd_shopping_cart": True,
        "source_order_no": order_no,
        "openid": open_id,
    }
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/order/waiting_pay/cancel'
    data = json.dumps(get_sign(data, 'POST', ts)).replace(' ', '')
    res = requests.post(url, data=data, verify=False).json()
    if res['code'] == 1:
        print('{}取消成功'.format(order_no))
