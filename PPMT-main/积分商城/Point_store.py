import time
import json
import requests
import datetime
import schedule
import warnings
import threading
from Encrypt import get_sign as s

warnings.filterwarnings('ignore')
version = '3.0.14'
ts = str(int(time.time_ns() / 1e6))
headers = {'Accept-Encoding': 'gzip',
           'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
           'content-type': 'application/json;charset=utf-8'}
code_map = {
    '西湖区': {'nationalCode': '330106', 'postalCode': '310013'},
    '余杭区': {'nationalCode': '330110', 'postalCode': '311100'},
    '梁溪区': {'nationalCode': '320213', 'postalCode': '214400'},
    '东城区': {'nationalCode': '110101', 'postalCode': '100010'}
}
user_list = {
    'oZdQ347vtZUQZqFYi1dz7xlkAGKQ': 436,
    'oZdQ34_AWQXMSoW75j5uFn-LSP3w': 436,
    'oZdQ34zpJSxuUHK3AkgCqeGWpvkY': 436,
    'oZdQ34_4YrSKMTyl7tN0vaR8CIbI': 437,
    'oZdQ343IWASNJN7fvncFcdrgkRic': 437,
    'oZdQ34yHOpO6hPKdmjrFQ2nfrleU': 437,
    'oZdQ34yuqd1XKXJ5fGFgXPY--r0Y': 437
}
address_dict = {}
finish_list = []


def get_stock(goodid):
    data = {'goods_spu_id': goodid}
    url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/goods/v2/detail?goods_spu_id={}&version={}&sign={}&time={}'.format(
        data['goods_spu_id'], version, s(data, 'GET'), ts)
    res = requests.get(url=url, headers=headers, verify=False).json()
    stock = res['data']['data']['inventory']
    if stock > 0:
        print('库存{}'.format(stock), datetime.datetime.now())
        return True
    else:
        print('无库存', datetime.datetime.now())
        return False


def create_order(auth, address, goodid):
    url = 'https://popvip.paquapp.com/miniapp/v2/seckill/order_create'
    data = {
        "buy_dict": {
            str(goodid): 1
        },
        "address": {
            "nationalCodeFull": "{}000".format(address['nationalCode']),
            "telNumber": address['tel'],
            "userName": address['name'],
            "nationalCode": address['nationalCode'],
            "postalCode": address['postalCode'],
            "provinceName": address['province'],
            "cityName": address['city'],
            "countyName": address['district'],
            "streetName": "",
            "detailInfoNew": address['address'],
            "detailInfo": address['address']
        },
        "coupon_dict": {},
        "uc_id": {},
        "mailing_type": 0,
        "openid": auth,
    }
    data = json.dumps(s(data, 'POST'), ensure_ascii=False).encode('utf-8')
    start = time.time()
    res = requests.post(url=url, headers=headers, data=data, verify=False)
    end = time.time()
    use = round((end - start) * 1000, 2)
    print(address_dict[auth]['name'], '{}ms'.format(use), res.json(), datetime.datetime.now())


def create_orders():
    threads = []
    for open_id in user_list:
        thread = threading.Thread(target=create_order, args=[open_id, address_dict[open_id], user_list[open_id]])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    if finish_list:
        for i in finish_list:
            del user_list[i]


def get_address():
    for open_id in user_list:
        data = {'openid': open_id}
        _address_dict = {}
        url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/address/default?openid={}&version={}&sign={}&time={}'.format(
            data['openid'], version, s(data, 'GET'), ts)
        res = requests.get(url, verify=False)
        if res.json()['code'] == 1:
            data = res.json()['data']
            if data:
                _address_dict['user_id'] = data['user_id']
                _address_dict['province'] = data['province']
                _address_dict['city'] = data['municipality']
                _address_dict['district'] = data['district']
                _address_dict['address'] = data['address']
                _address_dict['name'] = data['receiving_name']
                _address_dict['tel'] = data['receiving_tel']
                _address_dict['nationalCode'] = code_map[_address_dict['district']]['nationalCode']
                _address_dict['postalCode'] = code_map[_address_dict['district']]['postalCode']
                address_dict[open_id] = _address_dict
                print(_address_dict)
            else:
                print('无默认地址')


def count():
    global y
    x = True
    y = False
    while x:
        if sell_time - time.time() <= 0.3:
            create_orders()
            x = False


if __name__ == '__main__':
    y = True
    sell_time = 1629252000
    schedule.every().day.at('09:59:00').do(get_address)
    schedule.every().day.at('09:59:55').do(count)
    while y:
        schedule.run_pending()
        print('倒计时{}秒'.format(int(sell_time - time.time())))
        time.sleep(1)

    # while user_list:
    #     if get_stock(437):
    #         create_orders()
    #     time.sleep(0.5)
    #  补货记得删掉重复下单
    # get_address()
    # create_orders()
