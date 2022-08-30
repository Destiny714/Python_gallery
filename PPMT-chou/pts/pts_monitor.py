import json
import time
import tokens
import requests
import warnings
import datetime
import schedule
import threading

warnings.filterwarnings('ignore')

ts = int(time.time_ns() / 1e6)
sell_start_time = None
success_buy_list = []
sell_timestamp = 0
address_dict = {}
expired_list = []
_token_list = []
token_list = []


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


def get_detail(goodid):
    global sell_start_time, sell_timestamp
    url = 'https://boxonline.paquapp.com/pts/xcx/getPtsShopDetails?pts_shop_id={}&ts={}&sign='.format(
        goodid,ts)
    res = requests.get(url, headers=header(token_list[0]),verify=False).json()
    state = res['data']['state']
    stock = res['data']['inventory']
    scratch_card = res['data']['scratch_card']
    sell_start_time = res['data']['sell_start_time']
    if sell_start_time:
        sell_time = f"2021:{sell_start_time}:00"
        sell_timesArray = time.strptime(sell_time,'%Y:%m月%d日 %H:%M:%S')
        sell_timestamp = time.mktime(sell_timesArray)
        if sell_timestamp > time.time():
            print('定时上架未开售', datetime.datetime.now())
            return 5  # 定时上架
        else:
            if stock > 0:
                print('定时上架已开售有库存', datetime.datetime.now())
                return 2
            else:
                print('定时上架已开售无库存', datetime.datetime.now())
                return 3
    if state == 1:
        if scratch_card == 1:
            print('刮刮卡已上架',datetime.datetime.now())
            return 1  # 刮刮卡上架==1
        else:
            if stock > 0:
                print('抢购已上架,有库存',datetime.datetime.now())
                return 2  # 抢购上架有库存==2
            else:
                print('抢购已上架，无库存，捡漏中',datetime.datetime.now())
                return 3  # 抢购上架无库存
    else:
        if scratch_card == 1:
            print('刮刮卡下架状态',datetime.datetime.now())
            return 4  # 刮刮卡下架==4
        else:
            print('抢购已下架',datetime.datetime.now())
            return 0  # 抢购的下架==0


def scratch(goodid,auth):
    url = 'https://boxonline.paquapp.com/pts/xcx/openScratchCard?shop_id={}&ts={}&sign='.format(goodid,ts)
    start = time.time()
    res = requests.get(url,headers=header(auth),verify=False).json()
    end = time.time()
    use = round((end - start) * 1000, 2)
    if res['code'] == 1:
        if res['data']['reward'] != 0:
            print('=====>>{}抽中了<<====={}ms'.format(address_dict[auth]['name'],use),datetime.datetime.now())
        else:
            print('{}没抽中===={}ms'.format(address_dict[auth]['name'],use),datetime.datetime.now())


def scratch_all():
    global x
    threads = []
    for token in token_list:
        thread = threading.Thread(target=scratch,args=[good_id,token])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    x = False


def scan_token():
    global _token_list,token_list
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


def get_address():
    url = 'https://boxonline.paquapp.com/xcx/receivingList?ts={}&sign='.format(ts)
    for token in token_list:
        _address_dict = {}
        res = requests.get(url, headers=header(token)).json()
        if res['code'] == 1:
            address_info = res['data']
            if address_info:
                address_info = address_info[0]
                _address_dict['name'] = address_info['name']
                _address_dict['tel'] = address_info['tel']
                _address_dict['address'] = address_info['address']
                _address_dict['province'] = address_info['region1']
                _address_dict['city'] = address_info['region2']
                _address_dict['area'] = address_info['region3']
                address_dict[token] = _address_dict
            else:
                expired_list.append(token)
        else:
            expired_list.append(token)
    if expired_list:
        for e in expired_list:
            token_list.remove(e)
    print('{}个号有效'.format(len(address_dict)))
    print('{}个号无效'.format(len(expired_list)))


def create_order(auth, address, goodid):
    url = 'https://boxonline.paquapp.com/pts/xcx/getPayInfo'
    data = {
        'shop_id': goodid,
        'count': buy_num,
        'activity_key': 'pts_20210917',
        'name': address['name'],
        'tel': address['tel'],
        'province': address['province'],
        'city': address['city'],
        'area': address['area'],
        'address': address['address'],
        'api_info': 'ptsGetPayInfo',
        'checkOrderApi': 'ptsCheckOrder',
        'ts': ts,
        'sign': ''
    }
    data = json.dumps(data)
    start = time.time()
    res = requests.post(url=url, data=data, headers=header(auth))
    try:
        res = res.json()
        end = time.time()
        use = round((end - start) * 1000, 2)
        if res['code'] == 1:
            if res['msg'] == 'success':
                success_buy_list.append(auth)
                print('{}抢购成功===={}ms'.format(address_dict[auth]['name'],use),datetime.datetime.now())
            else:
                print('{}抢购失败  原因:{}===={}ms'.format(address_dict[auth]['name'],res['msg'],use),datetime.datetime.now())
        else:
            print(res)
    except Exception as e:
        print(res,e)


def create_orders():
    global x
    threads = []
    for _user in token_list:
        thread = threading.Thread(target=create_order,args=[_user,address_dict[_user],good_id])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    if success_buy_list:
        for _ in success_buy_list:
            token_list.remove(_)
    x = False


def count():
    global x
    x = False
    y = True
    while y:
        if sell_timestamp - time.time() <= 0.4:
            create_orders()
            y = False


if __name__ == '__main__':
    scan_token()
    get_address()
    while True:
        x = True
        good_id = input('goodid:')
        buy_num = int(input('buynum:'))
        while x and token_list:
            scan_token()
            result = get_detail(good_id)
            if result == 1:
                scratch_all()
            elif result == 2:
                create_orders()
            elif result == 5:
                pre_time = time.strftime('%H:%M:%S', time.localtime(sell_timestamp - 5))
                schedule.every().day.at(pre_time).do(count)
                while x:
                    schedule.run_pending()
                    print(f'倒计时{int(sell_timestamp - time.time())}s')
                    time.sleep(1)
            time.sleep(1)
