import os
import re
import time
import random
import requests
import datetime
import schedule
import warnings
import threading
from push import pusher

warnings.filterwarnings('ignore')
detail_list = []
finish_list = []
start_timestamp = ''
y = True
stock_proxies = {'http': 'http://121.201.49.230:16819', 'https': 'http://121.201.49.230:16819'}
address_proxy = {'http': 'http://121.201.49.230:16819', 'https': 'http://121.201.49.230:16819'}
ts = int(time.time_ns() / 1e6)
sku = 0
token_list = []
_token_list = []
expired_list = []


def get_address():
    url = 'https://boxonline.paquapp.com/xcx/receivingList?ts={}&sign='.format(ts)
    valid = 0
    for _ in token_list:
        try:
            res = requests.get(url, headers=header(_), verify=False, timeout=3)
            res = res.json()
            if res['code'] == 1:
                try:
                    user_name = res['data'][0]['name']
                    if not res['data'][0]['is_default']:
                        print(f"{user_name}未设置默认地址")
                        expired_list.append(_)
                    else:
                        print(user_name)
                        valid += 1
                except Exception as e:
                    print('无姓名', e)
                    expired_list.append(_)
            else:
                print(res)
                expired_list.append(_)
        except Exception as e:
            expired_list.append(_)
            print(e)
            pass
    if expired_list:
        for e in expired_list:
            token_list.remove(e)
    print('{}个号有效'.format(valid))
    print('{}个号无效'.format(len(expired_list)))


def scan_token():
    global _token_list, token_list
    old_len = len(token_list)
    token_list = []
    _token_list = []
    path = './token'
    files = os.listdir(path)
    file_list = []
    for file in files:
        if file.split('.')[1] == 'txt':
            file_list.append(file)
    for file in file_list:
        with open('{}/{}'.format(path, file), 'r') as f:
            data = f.read()
            for _ in data.split('\n'):
                if _ != '' and len(_) < 1000:
                    _token_list.append(_)
    for _ in _token_list:
        if _ not in token_list:
            if _ not in expired_list:
                token_list.append(_)
    if old_len != len(token_list):
        print('更新---{}个用户'.format(len(token_list)))


def header(auth):
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'authorization': auth,
        'accept-language': 'zh-cn',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
        'accept-encoding': 'gzip, deflate, br'
    }
    return headers


def create_order(auth, timeout, goodid):
    url = 'https://boxonline.paquapp.com/xcx/getShopPayInfo?shop_id=%d&count={}&room_id=null&ts=%d&sign='.format(
        num) % (goodid, ts)
    start = time.time()
    res = requests.get(url=url, headers=header(auth), verify=False, timeout=timeout)
    try:
        if res.status_code == 200 or 400:
            res = res.json()
            end = time.time()
            use = round((end - start) * 1000, 2)
            if re.search(r'order_no', str(res)):
                if res['code'] == 1:
                    order = res['data']['order_no']
                    msg = res['msg']
                    finish_list.append(auth)
                    print('用时{}ms  抢购状态:{} 订单号===>{}'.format(use, msg, order), datetime.datetime.now())
                    return use
                else:
                    print(res, '{}ms'.format(use), datetime.datetime.now())
                    return use
            else:
                end = time.time()
                use = round((end - start) * 1000, 2)
                if re.search(r'未授权', str(res)):
                    expired_list.append(auth)
                    print('登录过期', f'{use}ms')
                else:
                    print(res, f'{use}ms', datetime.datetime.now())
                return use
        else:
            end = time.time()
            use = round((end - start) * 1000, 2)
            print(res.text, f'{use}ms')
            return use
    except Exception as e:
        print(res, res.text, e)
        return False


def create_all_order(timeout):
    global finish_list
    threads = []
    for _token in token_list:
        thread = threading.Thread(target=create_order, args=[_token, timeout, good_id])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    if finish_list:
        for _token in finish_list:
            if _token in token_list:
                token_list.remove(_token)


def countdown():
    global y
    print('倒计时5s')
    x = True
    y = False
    while x:
        now = time.time()
        if (int(start_timestamp) - now) <= early_time:
            create_all_order(6)
            x = False


def check_rate():
    print('测试延迟')
    sum_time = 0
    suc_count = 0
    for i in range(3):
        use_time = create_order(random.choice(token_list), 1, 760)
        if use_time:
            sum_time += use_time / 1000
            suc_count += 1
        time.sleep(2)
    avg_time = round((sum_time / suc_count), 3) + 0.1
    print(f'提前{avg_time}s提交')
    return avg_time


def get_start_time():
    global sku
    url = 'https://boxonline.paquapp.com/shopgroup/getShopDetails?shop_group_id=%s&ts=%d&sign=' % (main_id, ts)
    res = requests.get(url=url, headers=header(token_list[0]), verify=False)
    while res.status_code != (200 or 400):
        res = requests.get(url=url, headers=header(token_list[0]), verify=False)
    res = res.json()
    if res['code'] == 1:
        sell_start_time = res['data']['sell_start_time']
        name = res['data']['brand_name']
        sku = res['data']['shopList'][0]['id']
        if sell_start_time:
            timeArray = time.strptime((sell_start_time + '2021'), "%m.%d %H:%M%Y")
            timestamp = int(time.mktime(timeArray))
            print('{} 开售时间为'.format(name), sell_start_time)
            return timestamp
        else:
            print('{} 已开售'.format(name))
            return False
    else:
        print('登录过期,查询开售时间失败')


def get_valid_sku():
    global detail_list
    url = 'https://boxonline.paquapp.com/shopgroup/getShopDetails?shop_group_id=%s&ts=%d&sign=' % (main_id, ts)
    try:
        res = requests.get(url=url, headers=header(token_list[0]), verify=False, timeout=2)
        if res.status_code == 200 or 400:
            res = res.json()
            if res['code'] == 1:
                shoplist = res['data']['shopList']
                detail_list = []
                for good in shoplist:
                    _good_id = good['id']
                    stock = good['inventory']
                    print(f'stcok:{stock}')
                    if stock >= num:
                        detail_list.append({'good_id': _good_id, 'stock': stock})
            else:
                token_list.remove(token_list[0])
                print('登录过期，查询失败')
        else:
            print(res.text)
    except Exception as e:
        print(e)


def user_info(auth):
    try:
        url = 'https://boxonline.paquapp.com/xcx/getUserInfo?ts={}&sign='.format(ts)
        res = requests.get(url, headers=header(auth), verify=False, timeout=3).json()
        try:
            name = res['data']['user']['nickname']
            print(f'{name}==>去付钱')
            return name
        except Exception as e:
            print(f'{e}==>去付钱')
            return 'null'
    except Exception as e:
        print(f'{e}==>去付钱')
        return 'null'


if __name__ == '__main__':
    scan_token()
    token_list = token_list[:]
    print('本任务{}个用户'.format(len(token_list)))
    get_address()

    main_id = 1102  # 1102/1116
    num = 1
    check_rate()
    if token_list:
        start_timestamp = get_start_time()
        good_id = sku
    else:
        print('没有账号,退出')
        exit()

    if start_timestamp:
        print('倒计时模式===>')
        early_time = check_rate()
        pre_time = time.strftime('%H:%M:%S', time.localtime(start_timestamp - 5))
        schedule.every().day.at(pre_time).do(countdown)
        while y:
            schedule.run_pending()
            print('倒计时{}秒'.format(int(start_timestamp - time.time())))
            time.sleep(1)
        if finish_list:
            print('success:{}'.format(len(finish_list)))
            for token in finish_list:
                push_name = user_info(token)
                pusher(f'下单成功', str(time.ctime()).split()[3])
    else:
        print('补货模式===>')
        while token_list:
            scan_token()
            get_valid_sku()
            if detail_list:
                print('库存{}个'.format(detail_list[0]['stock']))
                create_all_order(3)
            else:
                print('无库存,继续监控', datetime.datetime.now())
            time.sleep(0.8)
        if finish_list:
            print('success:{}'.format(len(finish_list)))
            for token in finish_list:
                push_name = user_info(token)
                pusher(f'下单成功', str(time.ctime()).split()[3])
