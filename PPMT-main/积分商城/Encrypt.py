import json
import time
import hashlib
import requests
import datetime
import threading
import warnings

warnings.filterwarnings('ignore')

headers = {'Accept-Encoding': 'gzip',
           'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
           'content-type': 'application/json;charset=utf-8'}
ts = str(int(time.time_ns() / 1e6))
salt = 'PopMartminiApp1117'
version = '3.0.14'
available_store = []
finished_openid = []
invalid_users = []
finish_list = []


def md5(s):
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()


def get_sign(request_data: dict, Method):
    encryption_data = {}
    for key in sorted(request_data.keys()):
        if Method == 'POST':
            encryption_data[key] = request_data[key]
        else:
            encryption_data[key] = str(request_data[key])
    encryption_data['version'] = version
    encryption_str = json.dumps(encryption_data, separators=(',', ':'), ensure_ascii=False) + salt + ts
    sign = md5(encryption_str)
    encryption_data['time'] = ts
    encryption_data['sign'] = sign
    if Method == 'POST':
        return encryption_data
    elif Method == 'GET':
        return sign
    else:
        print('Method Error')
        exit()


def get_detail_url(good_id):
    data = {'goods_spu_id': good_id}
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/goods/v2/detail?goods_spu_id={}&version={}&sign={}&time={}'.format(
        data['goods_spu_id'], version, get_sign(data, 'GET'), ts)
    return url


def get_sell_time(good_id):
    res = requests.get(get_detail_url(good_id), headers=headers, verify=False).json()
    sell_time = str(res['data']['sg_goods_spu']['sell_at'])
    if sell_time.split('-')[0] == '0001':
        print('已开售')
        return False
    else:
        sell_time = sell_time.split('+')[0]
        timeArray = time.strptime(sell_time, '%Y-%m-%dT%H:%M:%S')
        timestamp = int(time.mktime(timeArray))
        print('开售时间为', sell_time)
        return timestamp


def get_stock(good_id, store_id, open_id):
    orgdata = {
        "sku_ids": [good_id],
        "store_id": store_id,
        "openid": open_id,
    }
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/goods/skus_inventory'
    res = requests.post(url, data=json.dumps(get_sign(orgdata, 'POST')), headers=headers, verify=False).json()
    stock = res['data']['sku_inventorys'][0]['total_inventory']
    if stock > 0:
        available_store.append(store_id)
        return True
    else:
        return False


def get_all_stock(good_id, store_ids, open_ids: list):
    start = time.time()
    threads = []
    for i, store_id in enumerate(store_ids):
        thread = threading.Thread(target=get_stock, args=[good_id, store_id, open_ids[i]])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    if available_store:
        end = time.time()
        use = round((end - start), 2)
        print('{}秒查询到{}个有库存店铺'.format(use, len(available_store)))
        return available_store
    else:
        return False


def create_order(good_id, open_id, store_id, buy_num):
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
        "share_phone": "66666666666",
        "openid": open_id,
    }
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/order/create_v2'
    res = requests.post(url, data=json.dumps(get_sign(orgdata, 'POST')), headers=headers, verify=False).json()
    if res['code'] == 1:
        order_id = res['data']['source_order_no']
        finish_list.append([open_id, order_id])
        print('下单成功', 'order_id-->', order_id, datetime.datetime.now())
    elif res['code'] == 10015:
        finished_openid.append(open_id)
        print(open_id, res['msg'], datetime.datetime.now())
    else:
        print(open_id, res['msg'], datetime.datetime.now())


def get_user_info(user_id):
    data = {
        'user_id': user_id
    }
    url = 'https://popvip.paquapp.com/miniapp/v2/wechat/getUserInfo/?user_id={}&sign={}&time={}&version={}'.format(
        data['user_id'], get_sign(data, 'GET'), ts, version)
    res = requests.get(url, headers=headers, verify=False).json()['data']
    tel = res['phone']
    wxid = res['nickname']
    return {'电话': tel, '微信名': wxid}


def get_address(open_id):
    data = {'openid': open_id}
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/address/default?openid={}&version={}&sign={}&time={}'.format(
        data['openid'], version, get_sign(data, 'GET'), ts)
    res = requests.get(url, headers=headers, verify=False).json()
    if res['code'] == 1:
        res = res['data']
        if res:
            user_info = {'tel': res['receiving_tel'], 'name': res['receiving_name'], 'id': res['user_id']}
            return user_info
        else:
            return '无默认地址'
    else:
        invalid_users.append(open_id)


def get_order_info(open_id, order_no):
    data = {
        'source_order_no': order_no,
        'openid': open_id
    }
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/order/detail?source_order_no={}&openid={}&sign={}&time={}&version={}'.format(
        data['source_order_no'], data['openid'], get_sign(data, 'GET'), ts, version)
    res = requests.get(url, headers=headers, verify=False).json()
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
    data = {
        "cancel_select_reason": 1,
        "is_readd_shopping_cart": True,
        "source_order_no": order_no,
        "openid": open_id,
    }
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/order/waiting_pay/cancel'
    data = json.dumps(get_sign(data, 'POST'))
    res = requests.post(url, data=data, verify=False).json()
    if res['code'] == 1:
        print('{}取消成功'.format(order_no))
