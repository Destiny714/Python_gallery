import lining_tokens
import threading
import datetime
import schedule
import requests
import warnings
import random
import json
import time

warnings.filterwarnings('ignore')
y = True

token_list = lining_tokens.token_list

sku_dict = {}
sku_list = []
success_list = []
user_address_map = {}
price = ''


def header(auth):
    headers = {
        'Host': 'api.store.lining.com',
        'Connection': 'keep-alive',
        'auth-token': auth,
        'content-type': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip,compress,br,deflate',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x18000731) NetType/WIFI Language/zh_CN',
    }
    return headers


def get_detail():
    global price
    url = 'https://api.store.lining.com/goodsg/v1/goods-jh-query/spu/detail'
    data = json.dumps({
        "spuId": spuid,
        "saasId": "8324992625302181585",
        "source": "2"
    })
    res = requests.post(url, data, headers=header(''), verify=False).json()
    goods_list = res['data']['spuVO']['skuList']
    name = res['data']['spuVO']['title']
    print(name)
    if not goods_list[0]['skuPromotionInfo']:
        price = res['data']['spuVO']['spuPrice']['minSalePrice']
    else:
        price = goods_list[0]['skuPromotionInfo']['promotionPrice']
    for good_detail in goods_list:
        sku = good_detail['skuId']
        stock = good_detail['skuStock']['stockQuantity']
        size = good_detail['skuSpecValueList'][0]['specValue']
        if stock > 0:
            sku_list.append(sku)
            sku_dict[sku] = size


def random_sku():
    return sku_list[random.randint(0, len(sku_list) - 1)]


def get_address_map():  # 获取用户对应地址
    global user_address_map
    expire_list = []
    print('Read Address \n')
    address_url = 'https://api.store.lining.com/tradeg/v2/settle/ln/getSettleDetail'
    for token in token_list:
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
                    "skuId": sku_list[0],
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
        try:
            address_detail = address['data']['userAddress']
            print(address_detail['phone'], address_detail['name'], address_detail['provinceName'],
                  address_detail['cityName'], address_detail['districtName'], address_detail['detailAddress'])
            user_address_map[token] = address_detail
        except:
            print(address)
            expire_list.append(token)

    if expire_list:
        for _ in expire_list:
            token_list.remove(_)
        print('{}个账号过期或没地址'.format(len(expire_list)))
    print('Read Address Finished\n')


def create_order(auth):
    url = 'https://api.store.lining.com/tradeg/v2/settle/ln/createOrder'
    sku = random_sku()
    data = json.dumps({
        "userAddress": user_address_map[auth],
        "storeGoodsList": [{
            "goodsList": [{
                "spuId": spuid,
                "skuId": sku,
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
    })
    try:
        res = requests.post(url, data, headers=header(auth), verify=False).json()
        status = res['success']
        message = res['msg']
        n = 1
        while not status and n <= 3:
            print('抢购状态:{}  错误信息:{}  重新下单{}次'.format(status,message,n))
            res = requests.post(url, data, headers=header(auth), verify=False).json()
            status = res['success']
            message = res['msg']
            n += 1
            time.sleep(1)
        else:
            if n < 3:
                order_no = res['data']['orderNo']
                success_list.append([order_no,auth])
                print('抢购状态:', status, '订单号===>', order_no,'尺码:{} 用户:{}'.format(sku_dict[sku], user_address_map[auth]['name']), datetime.datetime.now())
            else:
                print('{}次下单失败,退出'.format(n))
                exit()
    except:
        pass


def create_orders():
    threads = []
    for token in token_list:
        thread = threading.Thread(target=create_order,args=[token])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    if success_list:
        with open('success.txt','a') as f:
            for success in success_list:
                f.write(str(success) + '\n')


def countdown():
    global y
    y = False
    x = True
    while x:
        if start_timestamp - time.time() <= 0.4:
            create_orders()
            x = False


if __name__ == '__main__':
    start_time = '2021,8,21,09,14,00'
    spuid = '2342871'
    start_timestamp = time.mktime(time.strptime(start_time, '%Y,%m,%d,%H,%M,%S'))
    pre_time = time.strftime('%H:%M:%S', time.localtime(start_timestamp - 5))
    print('抢购时间:{}'.format(time.strftime('%m-%d %H:%M:%S',time.localtime(start_timestamp))))
    get_detail()
    get_address_map()
    schedule.every().day.at(pre_time).do(countdown)
    while y:
        schedule.run_pending()
        print('倒计时{}秒'.format(int(start_timestamp - time.time())))
        time.sleep(1)
