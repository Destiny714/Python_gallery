import threading
import warnings
import schedule
import requests
import random
import time

warnings.filterwarnings('ignore')
headers = {
    'accept': '*/*',
    'accept-language': 'zh-cn',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
    'accept-encoding': 'gzip, deflate, br',
    'content-type': 'application/x-www-form-urlencoded',
    'referer': 'https://servicewechat.com/wx68722a6e91328103/150/page-frame.html'
}
goodid = '93851'
tokens = [
    # tokens
]
user_id_map = {}
expire_list = []
goods_detail_list = []


def get_available_goods_detail():
    global goods_detail_list
    url = 'https://wechat.fishfay.com/gatepath/wechat.goods.online.getSku'
    data = {'id_goods':goodid,'session3rd':'','id_shop': '18'}
    r = requests.post(url=url,headers=headers,data=data,verify=False)
    r = r.json()['data']
    for good in r:
        sku_id = good['id_sku']
        stock = good['stock']
        if int(stock) > 0:
            goods_detail_list.append([sku_id,stock])
    print(goods_detail_list)


def random_sku():
    return random.choice(goods_detail_list)[0]


def get_temp_cart(token):
    url = 'https://wechat.fishfay.com/gatepath/wechat.trade.cartnormal.buynow'
    data = {'id_sku': random_sku(),'add_num': '1','session3rd': token,'id_shop': '18'}
    requests.post(url=url, headers=headers, data=data,verify=False)


def user_get():
    global user_id_map
    url = 'https://wechat.fishfay.com/gatepath/wechat.address.user.get'
    for token in tokens:
        data = {'session3rd': token,'id_shop': '18'}
        r = requests.post(url=url,headers=headers,data=data,verify=False)
        r = r.json()
        if r['status'] != -1:
            id_ud = r['data'][0]['id_ud']
            user_id_map[token] = id_ud
        else:
            expire_list.append(token)
    if expire_list:
        for _ in expire_list:
            print(_)
            tokens.remove(_)


def pre_buy(token):
    url = 'https://wechat.fishfay.com/gatepath/wechat.trade.bill.buynow'
    data = {'id_ud':user_id_map[token],'session3rd':token,'id_shop': '18'}
    requests.post(url=url,headers=headers,data=data,verify=False)


def final_buy(token):
    url = 'https://wechat.fishfay.com/gatepath/wechat.trade.bill.buynowtake'
    data = {'id_ud':user_id_map[token],'session3rd':token,'id_shop': '18'}
    r = requests.post(url=url,headers=headers,data=data,verify=False).json()
    print(r)


def prepare():
    user_get()
    get_available_goods_detail()


def buy(token):
    get_temp_cart(token)
    pre_buy(token)
    final_buy(token)


def buy_threads():
    threads = []
    for token in tokens:
        thread = threading.Thread(target=buy, args=[token])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def set_time_buy():
    global sched
    count = True
    sched = False
    while count:
        if sell_time - time.time() <= 0.1:
            buy_threads()
            count = False


if __name__ == '__main__':
    sched = True
    sell_time = 1630720800
    prepare()
    print(f'共有{len(tokens)}个账号')
    schedule.every().day.at('09:59:55').do(set_time_buy)
    while sched:
        schedule.run_pending()
        print(f'倒计时{int(sell_time - time.time())}秒')
        time.sleep(1)
    # prepare()
    # buy(tokens[0])



