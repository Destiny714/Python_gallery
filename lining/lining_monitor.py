import json
import time
import random
import requests
import datetime
import warnings
import threading
import lining_tokens

high = '4876571'
low = '4896552'
spuid_list = [['高帮', high], ['低帮', low], ['test', '3980350']]
print(spuid_list)
spuid = spuid_list[int(input('选择监控第几个商品:')) - 1][1]

price = '129900'

num_list = {}
goods_map = []
success_list = []
available_list = []
user_address_map = []
have_create = True
n = 0

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
        sku_list = r['data']['spuVO']['skuList']
        name = r['data']['spuVO']['title']
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
        if goods_map:
            if n == 0:
                prt_stock = []
                for _ in goods_map:
                    if _['stock'] > 0:
                        prt_stock.append(f"{_['size']}:{_['stock']}")
                print(f'读取商品成功\n{name}\n库存:{prt_stock}\n')
            else:
                pass
        else:
            print('读取商品失败，请重试\n')
        n += 1
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
            if not limit_size:
                if int(_['stock']) > 0:
                    available_stock.append(f"{_['size']}: {_['stock']}")
                    available_list.append(_['skuid'])
            else:
                if int(_['stock']) > 0 and _['size'] in limit_size:
                    available_stock.append(f"{_['size']}: {_['stock']}")
                    available_list.append(_['skuid'])
        if available_list:
            print('有效商品:', str(available_stock).replace("'",""), datetime.datetime.now())
        else:
            print('已上架,无库存,继续监控', datetime.datetime.now())
    else:
        print('未满足下单条件,继续监控', datetime.datetime.now())


def random_sku():
    return available_list[random.randint(0, len(available_list) - 1)]


def get_address_map():  # 获取用户对应地址
    global user_address_map
    rubbish_list = []
    print('读取用户地址\n')
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
                print(address_detail['phone'], address_detail['name'], address_detail['provinceName'],
                      address_detail['cityName'], address_detail['districtName'], address_detail['detailAddress'])
                user_address_map.append(user_address)
            else:
                rubbish_list.append(token)
        except Exception as e:
            print(e)
            rubbish_list.append(token)
    if rubbish_list:
        for rubbish in rubbish_list:
            token_list.remove(rubbish)
    print(f'\nRead {len(user_address_map)} Address Finished\n')


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
                print(f'{address["phone"]} 抢购状态 {success} 抢购结果: {txt["msg"]} {datetime.datetime.now()}')
            if num_list[token] <= 3:
                time.sleep(1)
                req = requests.post(url=url, headers=headers, data=data, verify=False)
                txt = req.json()
                success = txt['success']
                message = txt['msg']
                print(f'{address["phone"]} 抢购状态 {success} 抢购结果: {message} {datetime.datetime.now()} 补单%d次' % num_list[token])
                num_list[token] += 1
        else:
            print(f'{address["name"]} 补单失败')
            have_create = False
            exit()
    else:
        order_no = txt['data']['orderNo']
        success_list.append([order_no, token])
        print(f'{address["phone"]} 抢购状态===>{success} 订单号===>{order_no} 用时===>{use_time}s //{datetime.datetime.now()}')
        exit()


def create_orders():
    global have_create
    threads = []
    for _ in user_address_map:
        thread = threading.Thread(target=cop, args=[_['token'], _['address']])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    have_create = False
    if success_list:
        with open('success.txt', 'a') as f:
            for success in success_list:
                f.write(str(success) + '\n')


if __name__ == '__main__':

    limit_size = []

    get_goods_map(spuid)
    get_address_map()
    print('========== Monitor On ==========')
    while have_create:
        get_available_and_have_stock_sku(spuid)
        if available_list:
            create_orders()
        time.sleep(0.8)
