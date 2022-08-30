import requests
import json
import time
import args
import schedule
import datetime
from threading import Thread

x = True
y = True
good_price = 99
product_code = ''
aim_buy_id = ''
sell_time = ''
goods_map = []
temp_id_list = []


def get_product_code():
    global product_code
    product_list = args.product_list
    for v, i in enumerate(product_list):
        print(v + 1, i[0])
    product_code = product_list[int(input('选择第几个商品:')) - 1][1]
    return product_code


def get_goods_map():
    global goods_map, aim_buy_id, sell_time, good_price
    code = get_product_code()
    detail_url = 'https://i.uniqlo.cn/%s/product/i/product/spu/h5/query/%s/zh_CN' % (args.mode, code)
    detail = requests.get(detail_url, verify=False)
    resp = detail.json()['resp'][0]
    good_details = resp['rows']
    sell_time = resp['summary']['planOnDate']
    good_price = resp['summary']['originPrice']
    print('商品详情=====>>>>')
    for good_detail in good_details:
        styletext = good_detail['styleText']
        size = good_detail['size']
        product_id = good_detail['productId']
        good_map = [styletext, size, product_id]
        goods_map.append(good_map)
        print(good_map)


def get_aim_buy_id():
    get_goods_map()
    global aim_buy_id
    color = input('输入色号:')
    style = input('输入尺码:')
    for _ in goods_map:
        if _[0] == color and _[1] == style:
            aim_buy_id = _[2]


def get_temp_id():
    bg = datetime.datetime.now()
    global temp_id_list, y
    for user in args.users:
        try:
            if args.num <= 2:
                fee = int(str(args.get_express_fee(user)).split('.')[0]) + good_price * args.num
                price = '%s.00' % fee
            else:
                fee = good_price * args.num
                price = '%s.00' % fee
        except KeyError as e:
            print(user, 'without', e, '//expired')
            continue
        headers = {
            'Accept': '*/*',
            'Authorization': user,
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
            'Connection': 'keep-alive',
            'Cookie': '',
            'X-Tingyun-Id': 'f28-GhFRwsA;r=559771775'
        }
        if aim_buy_id:
            get_temp_id_url = 'https://i.uniqlo.cn/%s/hmall-od-service/order/createTempOrders/zh_CN' % args.mode
            get_temp_id_orgdata = {
                "map": {
                    "activities": [],
                    "continueCreate": "Y",
                    "creationTime": int(time.time()) * 1000,
                    "fromSiteId": "",
                    "products": [{
                        "addressId": "",
                        "distribution": "EXPRESS",
                        "distributionId": "",
                        "presaleActivityId": "",
                        "price": good_price,
                        "productCode": product_code,
                        "productId": aim_buy_id,
                        "quantity": args.num,
                        "revisions": [],
                        "caseFlag": "N"
                    }],
                    "saleChannel": "APPLET",
                    "saleEquipment": ""
                }
            }
            get_temp_id_data = json.dumps(get_temp_id_orgdata)
            r = requests.post(url=get_temp_id_url, headers=headers, data=get_temp_id_data, verify=False)
            r = r.json()
            try:
                success = r['success']
                if success is True:
                    temp_id = r['resp'][0]['tempIds'][0]
                    temp_id_list.append({'user': user, 'temp_id': temp_id, 'price': price})
                else:
                    print(r['msg'])
                    exit()
            except KeyError as error:
                print(user, 'without', error)
                continue
        else:
            print('输入商品信息有误,退出')
            exit()
    ed = datetime.datetime.now()
    us_tm = int(str(ed - bg).split('.')[1]) / 1000
    if temp_id_list:
        print('Temp_Id Read Success in', us_tm, 'ms', '------', datetime.datetime.now())
        print('15秒后开始抢购')
    else:
        print('Temp_Id Read Failed')
        exit()
    y = False


def create_order(user, tempid, price):
    start_time = datetime.datetime.now()
    headers = {
        'Accept': '*/*',
        'Authorization': user,
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
        'Connection': 'keep-alive',
        'Cookie': '',
        'X-Tingyun-Id': 'f28-GhFRwsA;r=559771775'
    }
    create_order_orgdata = {
        "orderInfos": [{
            "tempId": tempid,
            "couponsId": "",
            "deliveryTime": "",
            "currency": "CNY",
            "saleChannel": "APPLET",
            "buyerMessage": "",
            "buyerMemo": "",
            "activities": [{
                "isGiftActivity": "N",
                "activityName": "7.30-8.1 会员周末安心购（门店急送订单及部分商品除外）",
                "isFreeExpressActivity": "Y",
                "id": 12308
            }],
            "gifts": [],
            "markDesc": "",
            "deliveryDate": ""
        }],
        "creationTime": int(time.time()) * 1000,
        "invoice": {
            "needInvoice": False,
            "type": "N",
            "title": "",
            "content": "",
            "taxpayerId": "",
            "isCreate": False
        },
        "totalAccount": price,
        "flashCart": False
    }
    create_order_data = json.dumps(create_order_orgdata)
    create_order_url = 'https://i.uniqlo.cn/%s/hmall-od-service/order/createOrders' % args.mode
    res = requests.post(url=create_order_url, headers=headers, data=create_order_data, verify=False)
    end_time = datetime.datetime.now()
    use_time = int(str(end_time - start_time).split('.')[1]) / 1000
    print(res.json()['success'], res.json()['msg'], '------', datetime.datetime.now(), '------', 'Finished in',
          use_time, 'ms')


def create_orders():
    threads = []
    for _ in temp_id_list:
        t = Thread(target=create_order, args=[_['user'], _['temp_id'], _['price'] * args.num])
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


def set_time_start():
    global x
    while x:
        time_now = datetime.datetime.timestamp(datetime.datetime.now())
        delta = int(sell_time) / 1000 - time_now
        if delta <= 0.1:
            create_orders()
            x = False


def main():
    args.test_network()
    get_aim_buy_id()
    print('开售时间为', str(datetime.datetime.fromtimestamp(int(sell_time) / 1000)))
    print('========定时抢购模式倒计时开始========')
    schedule.every().day.at(
        str(datetime.datetime.fromtimestamp(int(sell_time) / 1000) - datetime.timedelta(seconds=15)).split()[1]).do(
        get_temp_id)
    schedule.every().day.at(
        str(datetime.datetime.fromtimestamp(int(sell_time) / 1000) - datetime.timedelta(seconds=5)).split()[1]).do(
        set_time_start)
    while x:
        schedule.run_pending()
        time.sleep(1)
        if y:
            print('倒计时', int(int(sell_time) / 1000 - time.time()), 's')
