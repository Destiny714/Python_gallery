# coding : utf-8
import base64
import json
import random
import re
import threading
import requests
import time
import schedule
import datetime
from crypto.Cipher import AES
from crypto.Util.Padding import pad

x = True
have_stock_list = []
mode = input('输入抢购模式:定时==1 or 补货==2:')
url = 'https://minapp.peaksport.com/W6CauN1ZrC5ptdefbXVFup0nAqMhIpKE/6r4Od4C1Q1P0WbYd0VJ3Tx3GsOqcDkVL//minapp/tborder/createOrder'
users = ['1382355634777149442', '1394630247280152577', '1394631452991557633', '1394633829660364801',
         '1394634326261764098', '1298288177121243138', '1381782670197313538', '1399368350301556737',
         '1394650272443535361', '1391573773233115137', '1395192213951741954', '1399361547364675586',
         '1399361705212235777', '1382514479541440513', '1382514479541440513', '1399362211088117762',
         '1399361895215083521', '1399361129081606145', '1381785762611515393', '1399363203979661314',
         '1399362863268835329', '1399362659304026113', '1399363302934843393', '1399363754829156354',
         '1399365041970688002', '1399364263386230786', '1399365720231587841', '1399366175963688962',
         '1399371383422791681', '1399375020331241474', '1399367645469741058']
part_sku = 'E12833A10BJ'  # 'TE13901A1035'  # skucode的前缀
monitor_sku = 'E12833A'  # 'TE13901A'  # 监控用sku


def encrypt(txt):
    text = json.dumps(txt).replace(' ', '').replace('\n', '')
    key = b'KKOBKhVFC2QIrwMFWkkCxU0mcGv7UpSD'
    iv = b'B80sYtuLxg6YkyRs'
    aes = AES.new(key, AES.MODE_CBC, iv)
    text_pad = pad(text.encode('utf-8'), AES.block_size, style='pkcs7')
    encrypt_aes = aes.encrypt(text_pad)
    encrypted_text = base64.encodebytes(encrypt_aes).decode('utf-8')
    return encrypted_text.replace('\n', '')


def random_sku(part):
    # no_mean = str(part)
    # return 'TE13901A103542'
    return str(part + str(random.randint(39, 45)))


def get_have_stock_sku(sku_id):
    global have_stock_list
    detail_url = 'https://minapp.peaksport.com/W6CauN1ZrC5ptdefbXVFup0nAqMhIpKE/6r4Od4C1Q1P0WbYd0VJ3Tx3GsOqcDkVL//minapp/goods/spu/%s' % sku_id
    r = requests.get(url=detail_url)
    detail = r.json()
    sku_lists = detail['data']['skuList']
    if_on_shelf = detail['data']['activityResult']['data']['salesModelStatus']
    have_stock_list = []
    if if_on_shelf == 1:
        for sku_list in sku_lists:
            stock = sku_list['salesnumber']
            skucode = sku_list['skucode']
            if int(stock) > 0:
                have_stock_list.append(skucode)
    return have_stock_list


def get_monitor_cop_id():
    return have_stock_list[random.randint(0, len(have_stock_list) - 1)]


def peak_cop(token, size):
    headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x1800072a) NetType/WIFI Language/zh_CN',
        'referer': 'https://servicewechat.com/wxde74f6f446f4e1af/163/page-frame.html',
        'authorization': token,
        'accept-encoding': 'br, gzip, deflate',
        'content-type': 'application/json',
        'type': '1'
    }
    orgdata = {
        "userid": token,
        "postageCode": "",
        "remark": "",
        "fullDiscountCode": "",
        "addressId": "0",
        "refererParam": {
            "buyNumber": 1,
            "couponCode": "OptimalCouponCode",
            "fullDiscountCode": "OptimalFullDiscountCode",
            "integralId": "OptimalIntegralId",
            "postageCode": "",
            "shopcarIds": None,
            "skuCode": size,
            "preOrderId": None,
            "remark": ""
        },
        "referer": 1,
        "buyMoney": 1599,
        "source": "0"
    }
    data = json.dumps({
        "data": encrypt(orgdata)
    })
    # print(str(datetime.now()) + 'post_time')
    print('post_time', datetime.datetime.now())
    resp = requests.post(url=url, headers=headers, data=data)
    # print(str(datetime.now()) + 'back_time')
    txt = resp.text
    # print(txt)
    try:
        status = re.findall(r'"status".*?(\d+)', txt, re.DOTALL)[0]
        msg = re.findall(r'"message" : "(.*?)"', txt, re.DOTALL)[0]
        print('status = ' + status + '  ' + msg + '  ' + str(datetime.datetime.now()) + '初始下单')
        # time.sleep(0.1)
        if int(status) != 1:
            new_resp = requests.post(url=url, headers=headers, data=data)
            new_resp_status = re.findall(r'"status".*?(\d+)', new_resp.text, re.DOTALL)[0]
            new_msg = re.findall(r'"message" : "(.*?)"', new_resp.text, re.DOTALL)[0]
            print('status = ' + new_resp_status + '  ' + new_msg + '  ' + str(datetime.datetime.now()) + '重新下单')
    except IndexError as er:
        print(er)
        pass
    exit()


def peak_monitor(token, size):
    headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x1800072a) NetType/WIFI Language/zh_CN',
        'referer': 'https://servicewechat.com/wxde74f6f446f4e1af/163/page-frame.html',
        'authorization': token,
        'accept-encoding': 'br, gzip, deflate',
        'content-type': 'application/json',
        'type': '1'
    }
    orgdata = {
        "userid": token,
        "postageCode": "",
        "remark": "",
        "fullDiscountCode": "",
        "addressId": "0",
        "refererParam": {
            "buyNumber": 1,
            "couponCode": "OptimalCouponCode",
            "fullDiscountCode": "OptimalFullDiscountCode",
            "integralId": "OptimalIntegralId",
            "postageCode": "",
            "shopcarIds": None,
            "skuCode": size,
            "preOrderId": None,
            "remark": ""
        },
        "referer": 1,
        "buyMoney": 719,
        "source": "0"
    }
    data = json.dumps({
        "data": encrypt(orgdata)
    })
    # print(str(datetime.now()) + 'post_time')
    resp = requests.post(url=url, headers=headers, data=data)
    # print(str(datetime.now()) + 'back_time')
    txt = resp.text
    # print(txt)
    try:
        status = re.findall(r'"status".*?(\d+)', txt, re.DOTALL)[0]
        msg = re.findall(r'"message" : "(.*?)"', txt, re.DOTALL)[0]
        print('status = ' + status + '  ' + msg + '  ' + str(datetime.datetime.now()) + '捡漏下单')
    except IndexError as er:
        print(er)
        pass
    exit()


def monitor(u):
    if get_have_stock_sku(monitor_sku):
        print(have_stock_list)
        threads = []
        for user in users[:u]:
            thread = threading.Thread(target=peak_monitor, args=[user, get_monitor_cop_id()])
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
    else:
        print('无库存,继续监控')


def start_threads(i):
    threads = []
    for user in users[:i]:
        thread = threading.Thread(target=peak_cop, args=[user, random_sku(part_sku)])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def set_time_start():
    global x
    while x:
        time1 = datetime.datetime(2021, month, day, hour, minutes, sec)
        tm1 = datetime.datetime.timestamp(time1)
        time2 = datetime.datetime.now()
        tm2 = datetime.datetime.timestamp(time2)
        delta = tm1 - tm2
        if delta <= delay:
            start_threads(n)
            x = False


if mode == '1':
    month = int(input('输入开始月份，不需要补0:'))
    day = int(input('输入开始日，不需要补0:'))
    hour = int(input('输入开始小时，不需要补0:'))
    minutes = int(input('输入开始分钟，需要补0:'))
    sec = int(input('输入开始秒，需要补0:'))
    n = int(input('输入打开任务数量:'))
    delay = float(input('输入提前开始时间,s:'))

    schedule_time = str(datetime.datetime(year=2021,month=month,day=day,hour=hour, minute=minutes, second=sec) - datetime.timedelta(seconds=3)).split(' ')[1]
    print('============开始时间为%s点%s分%s秒，提前%s秒，倒计时等待抢购============' % (str(hour), str(minutes), str(sec), str(delay)))
    schedule.every().day.at(schedule_time).do(set_time_start)
    while x:
        schedule.run_pending()
        print(datetime.datetime.now())
        time.sleep(1)


elif mode == '2':
    user_amount = int(input('输入监控任务数:'))
    print('===========监控开启===========')
    while True:
        monitor(user_amount)
        time.sleep(2)
