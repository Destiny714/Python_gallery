import datetime
import json
import random
import time
import args
import requests
from threading import Thread

product_code = ''
aim_buy_id = ''
goods_map = []
temp_id_list = []
have_stock_list = []
finished_list = []
buy_num = 1
monitor_size = ''
monitor_style = ''
monitor_price = ''
fee = ''
monitor_price_plus_fee = ''
x = True


def get_product_code():
    global product_code
    product_list = args.product_list
    for v, i in enumerate(product_list):
        print(v + 1, i[0])
    product_code = product_list[int(input('选择第几个商品:')) - 1][1]
    return product_code


def get_goods_map():
    global goods_map, aim_buy_id
    code = get_product_code()
    detail_url = 'https://i.uniqlo.cn/%s/product/i/product/spu/h5/query/%s/zh_CN' % (args.mode, code)
    detail = requests.get(detail_url, verify=False)
    resp = detail.json()['resp'][0]
    good_details = resp['rows']
    print('商品详情=====>>>>')
    for good_detail in good_details:
        styletext = good_detail['styleText']
        size = good_detail['size']
        product_id = good_detail['productId']
        good_map = [styletext, size, product_id]
        goods_map.append(good_map)
        print([styletext, size])


def get_have_stock_list():
    global have_stock_list
    aim_style = monitor_style
    aim_size_list = monitor_size.split(',')
    aim_sku_list = []
    have_stock_list = []
    for g in goods_map:
        if g[1] in aim_size_list and g[0] == aim_style:
            aim_sku_list.append(g[2])
    url = 'https://i.uniqlo.cn/%s/stock/stock/query/zh_CN' % args.mode
    get_stock_orgdata = {
        "productCode": product_code,
        "distribution": "EXPRESS",
        "type": "DETAIL"
    }
    data = json.dumps(get_stock_orgdata)
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
        'Connection': 'keep-alive',
        'Cookie': '',
        'X-Tingyun-Id': 'f28-GhFRwsA;r=559771775'
    }
    r = requests.post(url=url, headers=headers, data=data, verify=False)
    r = r.json()
    try:
        yes_or_no = r['resp'][0]['hasStock']
        if yes_or_no == 'Y':
            stock_list = r['resp'][0]['expressSkuStocks']
            for sku in stock_list:
                stock_num = int(stock_list[sku])
                if sku in aim_sku_list and stock_num > 0:
                    have_stock_list.append(sku)
            # print(have_stock_list)
        else:
            print('无库存--继续监控')
        return have_stock_list
    except KeyError as e:
        print(e)
        pass


def get_monitor_cop_id():
    return have_stock_list[random.randint(0, len(have_stock_list) - 1)]


def get_monitor_temp_id(user):
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
                "price": monitor_price,
                "productCode": product_code,
                "productId": get_monitor_cop_id(),
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
            return temp_id
        else:
            print(r['msg'])
            exit()
    except KeyError as e:
        print('can not find', e)
        finished_list.append(user)
        exit()


def create_order(user):
    global finished_list
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
            "tempId": get_monitor_temp_id(user),
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
        "totalAccount": "%s.00" % monitor_price_plus_fee,
        "flashCart": False
    }
    create_order_data = json.dumps(create_order_orgdata)
    create_order_url = 'https://i.uniqlo.cn/%s/hmall-od-service/order/createOrders' % args.mode
    res = requests.post(url=create_order_url, headers=headers, data=create_order_data, verify=False)
    j = res.json()
    end_time = datetime.datetime.now()
    use_time = float(str(end_time - start_time).split('.')[1]) / 1000
    print(res.json()['msg'], datetime.datetime.now(), '捡漏下单', '------', use_time, 'ms')
    if res.json()['msg'] == '超过限购数量!':
        finished_list.append(user)


def create_orders():
    global x
    if get_have_stock_list():
        threads = []
        if args.users:
            for user in args.users:
                t = Thread(target=create_order, args=[user])
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
        else:
            x = False
            print('\n', 'Cop Finished')
    else:
        print('无库存，监控中', datetime.datetime.now())


def main():
    global monitor_size, monitor_style, fee, monitor_price, monitor_price_plus_fee
    args.test_network()
    monitor_price = int(input('输入单价:'))
    fee = int(input('输入运费:'))
    if args.num <= 2:
        monitor_price_plus_fee = monitor_price * args.num + fee
    else:
        monitor_price_plus_fee = monitor_price * args.num
    get_goods_map()
    monitor_style = input('输入监控色号:')
    monitor_size = input('输入监控尺码:')
    while x:
        create_orders()
        for i in finished_list:
            if i in args.users:
                args.users.remove(i)
        time.sleep(1)
