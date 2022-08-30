from captcha import get_validates as cp
from decrypt import encrypt_sign as es
from decrypt import encrypt as en
import threading
import datetime
import schedule
import requests
import warnings
import pymysql
import random
import time
import json
import re

n = 0
count = []
details = {}
skus_map = []
aim_infos = []
token_list = []
count_list = []
target_list = []
captcha_list = []
create_infos = []
expired_list = []
success_list = []
skus_list_map = []
key_detail_list = []
finished_token_list = []
dangerous = False
print_init = True
need_to_buy = True
have_not_buy = True
have_not_searched = True
warnings.filterwarnings('ignore')
# proxies = {'http':'http://122.114.206.62:16817','https':'http://122.114.206.62:16817'}

mode = input('1.定时 2.货号 3.监控 4.TEST 5.DETAIL ======>>')

cmdt_id = '63c5d1c2723b4361bf44e514145e60e3'  # 监控单个商品id/586fd458d55842509871bc00e8ec300b
cmdt_ids = []  # 监控多个商品id
aim_list = ['42']  # 监控选定尺码，默认留空等于全码
shop = 'NKSY66'  # 限定店铺搜索
shop_name_filter = ' '  # 不用时打空格
shop_No_filter = []
keys = []  # 监控多个货号
key = ''  # 监控单个货号


def get_tokens():  # 从mysql读取token
    db = pymysql.connect(host='localhost', port=3306, user='root', password='1301207030Aa', database='topsports_decrypt')
    cursor = db.cursor()
    global token_list
    token_sql = 'select token from users'
    cursor.execute(token_sql)
    tokens = cursor.fetchall()
    for token in tokens:
        token_list.append(token[0])
    cursor.close()
    db.close()


def confirm_captchas():  # 从mysql读取验证码并确定验证码有效期，删除过期验证码
    db = pymysql.connect(host='localhost', port=3306, user='root', password='1301207030Aa', database='topsports_decrypt')
    cursor = db.cursor()
    global captcha_list
    captcha_list = []
    captcha_sql = 'select challenge,validate,No,create_time from captcha1'
    cursor.execute(captcha_sql)
    captchas = cursor.fetchall()
    for captcha in captchas:
        if int(time.time()) - int(str(captcha[3])) <= 360:
            captcha_list.append({'challenge': captcha[0], 'validate': captcha[1], 'No': captcha[2]})
        else:
            print('delete')
            delete_sql = f'delete from captcha1 where No = "{captcha[2]}"'
            cursor.execute(delete_sql)
            db.commit()
    cursor.close()
    db.close()


def del_captcha(vali):
    db = pymysql.connect(host='localhost', port=3306, user='root', password='1301207030Aa', database='topsports_decrypt')
    cursor = db.cursor()
    captcha_sql = f'DELETE FROM captcha1 WHERE validate="{vali}"'
    cursor.execute(captcha_sql)
    db.commit()
    cursor.close()
    db.close()


def check_captcha_num():  # 下单前检查验证码数量，不够就自动生成
    confirm_captchas()
    if len(captcha_list) < len(token_list):
        print('有效验证码个数为', len(captcha_list), ' 用户个数为', len(token_list), ' ====== 重新生成验证码')
        while len(captcha_list) < len(token_list):
            cp(len(token_list) - len(captcha_list))
            confirm_captchas()
            time.sleep(1)
        else:
            print('验证码重新生成完毕')


# api后缀
get_detail = '/shopCommodity/queryShopCommodityDetail/'
get_cart = '/shoppingcart/index'
add_cart = '/shoppingcart'
pre_order = '/order/confirmationOrder'
create_order = '/order/create'
get_addresslist = '/wxmall/address/queryAddressList'


def header(auth):  # 返回用户header
    headers = {
        'Authorization': '' + auth,
        'Content-Type': 'application/json',
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': '*/*',
        'appId': 'wx71a6af1f91734f18',
        'Referer': 'https://servicewechat.com/wx71a6af1f91734f18/87/page-frame.html',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac'
    }
    return headers


def match(txt):
    result = re.search(r'[Jj]ordan|[Dd]unk|[Rr]etro|JORDAN|DUNK|[Aa][Jj]|欧文|[Kk]yrie|35|[Cc][Uu][Tt]', txt)
    if result:
        return True
    else:
        return False


def search_match_id(url):  # 搜索对应货号返回匹配列表
    global target_list
    headers = header('')
    new_url = url + es('/search/shopCommodity/list')
    try:
        r = requests.get(url=new_url, headers=headers, verify=False, timeout=10).json()
        new_list = r['data']['spu']['list']
        target_list = []
        for new in new_list:
            new_code = new['productCode']
            shop_No = new['shopNo']
            # new_shop = new['shopName']
            # is_filter = re.search(shop_name_filter,new_shop)
            if keys and shop_No not in shop_No_filter:
                if new_code in keys:
                    target_list.append(new['id'])
            else:
                if new_code == key and shop_No not in shop_No_filter:
                    target_list.append(new['id'])
    except Exception as e:
        print(e)
        pass


def filter_():  # 搜索对应货号返回匹配列表
    global count
    count = []
    headers = header('')
    _keyword = ''
    pagesize = '20'
    _shop = ''
    url = 'https://wxmall.topsports.com.cn/search/shopCommodity/list?searchKeyword={}&current=1&pageSize={}&sortColumn=upShelfTime&sortType=desc&filterIds=TS100101%2CTS300301&shopNo={}&tssign='.format(
        _keyword, pagesize, _shop) + es('/search/shopCommodity/list')
    try:
        r = requests.get(url=url, headers=headers, verify=False, timeout=10).json()
        good_list = r['data']['spu']['list']
        for good_detail in good_list:
            good_id = good_detail['id']
            good_code = good_detail['productCode']
            real_price = good_detail['salePrice']
            tag_price = good_detail['tagPrice']
            count_num = round((real_price / tag_price), 4) * 10
            good_name = good_detail['productName'].replace('#', '')
            if match(good_name):
                is_match = True
            else:
                is_match = False
            good_shop = good_detail['shopName']
            good_count = good_detail['proName']
            if good_count:
                if (re.search(r'5折', good_count) or count_num <= 0.6) and good_id not in count_list and is_match:
                    count_list.append(good_id)
                    count.append(
                        {'name': good_name, 'shop': good_shop, 'id': good_id, 'count': f'{count_num}折--{good_count}', 'price': real_price, 'code': good_code})
            else:
                if count_num <= 0.6 and good_id not in count_list and is_match:
                    count_list.append(good_id)
                    count.append(
                        {'name': good_name, 'shop': good_shop, 'id': good_id, 'count': count_num, 'price': real_price, 'code': good_code})
    except Exception as e:
        print(e)
        pass
    return count


def get_target_info(url):  # 搜索匹配列表，返回有效skuid
    global have_not_searched, aim_infos, cmdt_id
    search_match_id(url)
    if target_list:
        choose_key = target_list[random.randint(0, len(target_list) - 1)]
        cmdt_id = choose_key
        get_goods_map(choose_key)
        try:
            if aim_list:
                if skus_map[0]['all_stock'] > 0:
                    for _sku in skus_map[1:]:
                        if _sku['stock'] > 0 and _sku['sizeEur'] in aim_list:
                            aim_infos.append(_sku)
                else:
                    shop_No_filter.append(skus_map[0]['shopNo'])
            else:
                if skus_map[0]['all_stock'] > 0:
                    for _sku in skus_map[1:]:
                        if _sku['stock'] > 0:
                            aim_infos.append(_sku)
                else:
                    shop_No_filter.append(skus_map[0]['shopNo'])
        except Exception as e:
            print(e)
            pass
    if target_list:
        if aim_infos:
            stock_list = []
            for _ in aim_infos:
                if _['stock'] > 0:
                    stock_list.append('{}:{}'.format(_['sizeEur'], _['stock']))
            print('搜索到下单目标==>{}==>{}'.format(skus_map[0]['shopName'], stock_list), datetime.datetime.now())
            have_not_searched = False
        else:
            try:
                print('搜索到目标{} {}，无库存，继续监控'.format(skus_map[0]['shopName'], skus_map[0]['shopNo']),
                      datetime.datetime.now())
            except Exception as e:
                print(e)
                print('搜索到目标，无库存，继续监控', datetime.datetime.now())
            time.sleep(1)
    else:
        print('无匹配目标,继续搜索', datetime.datetime.now())
        time.sleep(1)


def get_goods_map(com_id):
    global skus_list_map  # 读取商品所有详情
    print('读取商品详情')
    global skus_map, details, n
    skus_map = []
    details = {}
    url = en(get_detail + com_id)
    headers = header('')
    try:
        res = requests.get(url=url, headers=headers, verify=False, timeout=10).json()
        res = res['data']
        productCode = res['productCode']
        productNo = res['productNo']
        productName = res['productName']
        salePrice = res['salePrice']
        shopNo = res['shopNo']
        shopName = res['shopName']
        all_stock = res['stock']
        status = res['status']
        # activity_detail = res['proList'][0]
        details = {
            'productCode': productCode,
            'productNo': productNo,
            'productName': productName,
            'salePrice': salePrice,
            'shopNo': shopNo,
            'all_stock': all_stock,
            'status': status,
            'shopName': shopName,
            # 'activity': {'activity_type': activity_detail['activityType'], 'activity_str': activity_detail[
            #     'activityTypeStr'], 'template_no': activity_detail['templateNo']}
        }
        skus_map.append(details)
        skuList = res['skuList']
        for one_sku in skuList:
            skuid = one_sku['id']
            skuNo = one_sku['skuNo']
            stock = one_sku['stock']
            sizeNo = one_sku['sizeNo']
            sizeCode = one_sku['sizeCode']
            sizeEur = one_sku['sizeEur']
            sku_map = {'skuid': skuid,
                       'skuNo': skuNo,
                       'sizeNo': sizeNo,
                       'sizeCode': sizeCode,
                       'sizeEur': sizeEur,
                       'stock': stock}
            skus_map.append(sku_map)
        skus_list_map = [skus_map]
        if n == 0:
            stock_List = []
            for _ in skus_map[1:]:
                stock_List.append({_['sizeEur']: _['stock']})
            print(productName)
            print(str(stock_List).replace('{', '').replace('}', ''))
        n += 1
    except Exception as e:
        res = requests.get(url=url, headers=headers, verify=False)
        print('detail {} {}error'.format(res, e))
        pass


def get_good_list_map():  # 如果监控多个商品id，用这个返回详情
    threads = []
    for good_id in cmdt_ids:
        thread = threading.Thread(target=get_goods_map, args=[good_id])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def get_aim_info():  # 获取需要的skuid
    global aim_infos
    if aim_list:
        for _ in skus_map[1:]:
            if _['sizeEur'] in aim_list and _['stock'] > 0:
                aim_infos.append(_)
    else:
        for _ in skus_map[1:]:
            if _['stock'] > 0:
                aim_infos.append(_)
    if not aim_infos:
        print('无指定尺码，退出')
        exit()


def check_stock():  # 监控id模式校验库存，返回有效skuid
    global aim_infos
    if cmdt_ids:
        get_good_list_map()
    else:
        get_goods_map(cmdt_id)
        # print(details)
    for _skus_map in skus_list_map:
        if _skus_map[0]['status'] == 3:
            if aim_list:
                for _ in _skus_map[1:]:
                    if _['stock'] > 0 and _['sizeEur'] in aim_list:
                        aim_infos.append(_)
            else:
                for _ in _skus_map[1:]:
                    if _['stock'] > 0:
                        aim_infos.append(_)
    if skus_list_map[0][0]['status'] == 3:
        if aim_infos:
            prt_infos = []
            for i in aim_infos:
                prt_infos.append({i['sizeEur']: i['stock']})
            print('满足下单条件', prt_infos, datetime.datetime.now())
            return True
    else:
        if aim_infos:
            print('已下架，继续监控', datetime.datetime.now())
            time.sleep(1)
            return False
        else:
            print('下架无库存，继续监控', datetime.datetime.now())
            time.sleep(1)
            return False


def add_to_cart(user):  # 程序开始前提前加车，确保购物车id存在
    url = en(add_cart)
    headers = header(user)
    data = json.dumps({
        "shopNo": "NKNJA7",
        "productCode": "CW2289-111",
        "productSkuNo": "20201130009139",
        "productSizeCode": "8",
        "productSkuId": "44bff1d434534197ae9d9d4372b624aa",
        "shopCommodityId": "7eb2b4b19497435780cc948fc2da2c02",
        "brandNo": "NK",
        "num": 1,
        "merchantNo": "TS",
        "liveType": 0,
        "roomId": "",
        "roomName": ""
    })
    try:
        requests.post(url=url, headers=headers, data=data, verify=False, timeout=10)
    except Exception as e:
        print(e)
        requests.post(url=url, headers=headers, data=data, verify=False)


def all_add_cart():  # 所有账号加车
    start = time.time()
    threads = []
    for t in token_list:
        thread = threading.Thread(target=add_to_cart, args=[t])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    end = time.time()
    use = round((end - start) * 1000, 2)
    print('Pre Add_cart Finished in', use, 'ms')


def get_address(user):  # 获取账号地址，也用来验证账号是否掉登录，掉登录则加入过期账户列表
    global create_infos, expired_list
    url = en(get_addresslist)
    headers = header(user)
    try:
        rr = requests.get(url=url, headers=headers, verify=False, timeout=10).json()
    except Exception as e:
        print(e)
        rr = requests.get(url=url, headers=headers, verify=False).json()
    if_available = rr['bizCode']
    if if_available == 49999:
        expired_list.append(user)
        return None
    else:
        address_list = rr['data']['list']
        shippingId = address_list[0]['shippingId']
        return shippingId


def filter_expired():  # 用获取地址接口清理过期账户
    global token_list
    threads = []
    for i in token_list:
        thread = threading.Thread(target=get_address, args=[i])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    db = pymysql.connect(host='localhost', port=3306, user='root', password='1301207030Aa', database='topsports_decrypt')
    cursor = db.cursor()
    for p in expired_list:
        token_list.remove(p)
        sql = 'delete from users where token = "%s"' % str(p)
        cursor.execute(sql)
        db.commit()
    cursor.close()
    db.close()
    if expired_list:
        print('清理过期用户', len(expired_list), '个')


def get_create_infos():  # 获取创建订单所需的关键参数
    global create_infos
    start = time.time()
    for user in token_list:
        url = en(get_cart)
        headers = header(user)
        try:
            res = requests.get(url=url, headers=headers, verify=False, timeout=10)
        except Exception as e:
            print(e)
            res = requests.get(url=url, headers=headers, verify=False)
        if res.json()['data']['willBuyList']:
            shoppingcartId = re.findall(r'"shoppingcartId":"(.*?)",', res.text, re.DOTALL)[0]
            shippingId = get_address(user)
            user_info = {'user': user,
                         'shoppingcartId': shoppingcartId,
                         'shippingId': shippingId}
            create_infos.append(user_info)
    end = time.time()
    use = round((end - start) * 1000, 2)
    print('Shoppingcart Info Finished in', use, 'ms')


def create(create_info: dict, validate, challenge):  # 创建订单
    global dangerous
    _validate = str(validate).replace("'", '')
    _challenge = str(challenge).replace("'", '')
    start = time.time()
    url = en(create_order)
    aim_info = aim_infos[random.randint(0, len(aim_infos) - 1)]
    shoppingcartId = create_info['shoppingcartId']
    shippingId = create_info['shippingId']
    headers = header(create_info['user'])
    data = {
        "merchantNo": "TS",
        "rid": "",
        "shippingId": str(create_info['shippingId']),
        "subOrderList": [{
            "shopNo": str(skus_map[0]['shopNo']),
            "shopName": "",
            "mdmShopName": "",
            "shopAddress": "",
            "totalNum": 1,
            "totalPrice": None,
            "source": None,
            "virtualShopFlag": 0,
            "expressType": 2,
            "remark": '',
            "fullDiscountAmount": None,
            "fullReductionAmount": None,
            "couponAmount": "0.00",
            "commodityList": [{
                "map": {},
                "filterRules": None,
                "orderByClause": None,
                "shoppingcartId": str(shoppingcartId),
                "paterId": None,
                "productCode": str(skus_map[0]['productCode']),
                "productNo": str(skus_map[0]['productNo']),
                "colorNo": "00",
                "colorName": "默认",
                "categoriesNo": "410101",
                "sizeNo": str(aim_info['sizeNo']),
                "sizeCode": str(aim_info['sizeCode']),
                "sizeEur": str(aim_info['sizeEur']),
                "productName": "",
                "picPath": "",
                "brandDetailNo": "NK01",
                "proNo": None,
                "proName": None,
                "proNameApp": None,
                "assignProNo": "0",
                "skuId": str(aim_info['skuid']),
                "skuNo": str(aim_info['skuNo']),
                "shopCommodityId": str(cmdt_id),
                "salePrice": 999,
                "tagPrice": 999,
                "num": 1,
                "status": 3,
                "itemFlag": 0,
                "usedTicket": None,
                "activityType": 0,
                "activityTypeStr": None,
                "usedTickets": None,
                "liveType": 0,
                "roomId": None,
                "roomName": "",
                "zoneQsLevel": "S",
                "templateNo": None,
                "live_type": 0,
                "room_id": "",
                "room_name": ""
            }],
            "ticketCodes": None,
            "vipPrefAmount": "0.00",
            "prefAmount": "0.00",
            "ticketDtos": [],
            "unTicketDtos": [],
            "orderTickets": None,
            "ticketPresentDtos": None,
            "expressAmount": "0.00",
            "expressAmountStr": "包邮",
            "cashOnDelivery": 0,
            "salePriceAmount": "999.00",
            "promotionAmount": "0.00",
            "subOrderNo": None
        }],
        "purchaseType": 2,
        "usedPlatformCouponList": [],
        "verificationType": 2,
        "userLatitude": 30.27415,
        "userLongitude": 120.15515,
        "validate": _validate,
        "seccode": _validate+'|jordan',
        "challenge": _challenge
    }
    data = json.dumps(data, ensure_ascii=False).replace(' ', '').encode('utf-8')
    post_time = datetime.datetime.now()
    res = requests.post(url=url, headers=headers, data=data, verify=False).json()
    end = time.time()
    shop_No_filter.append(skus_map[0]['shopNo'])
    success_list.append({'token': create_info['user']})
    # code = res['bizCode']
    # if res['bizMsg'] == '成功':
    #     exit()
    # if code == 20000:
    #     order_no = res['data']['mainOrderNo']
    #     success_list.append({'token': create_info['user'], 'order_no': order_no})
    # elif code == 1:
    #     success_list.append({'token': create_info['user'], 'order_no': res['bizMsg']})
    use = round((end - start) * 1000, 2)
    print('status:', res['bizMsg'], '====== ', 'Post in', post_time,
          '====== {} Cop Finished in'.format(aim_info['sizeEur']), use, 'ms', '======',
          'Response in', datetime.datetime.now())
    del_captcha(validate)


def create_many():  # 并发创建订单
    global need_to_buy
    threads = []
    for no, create_info in enumerate(create_infos):
        thread = threading.Thread(target=create,
                                  args=[create_info,
                                        captcha_list[no]['validate'],
                                        captcha_list[no]['challenge']])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    need_to_buy = False


def output_success():  # 导出成功订单
    db = pymysql.connect(host='localhost', port=3306, user='root', password='1301207030Aa', database='topsports_decrypt')
    cursor = db.cursor()
    all_success = []
    url = en('/members/memberCenterQuery')
    for success in success_list:
        res = requests.get(url=url, headers=header(success['token']), verify=False).json()
        name = res['data']['nickName']
        one_success = {'name': name, 'order_no': success['order_no']}
        all_success.append(one_success)
    for one in all_success:
        add_sql = 'insert into success(No,name, order_no, time) values(null,%s,%s,%s)'
        cursor.execute(add_sql, (one['name'], one['order_no'], str(datetime.datetime.now())))
        db.commit()
    cursor.close()
    db.close()
    print('success:', len(success_list))


def prepare_work():  # 定时抢购准备工作
    get_tokens()
    time.sleep(1)
    all_add_cart()
    time.sleep(1)
    filter_expired()
    check_captcha_num()
    get_create_infos()


def set_time():  # 定时抢购倒计时
    global have_not_buy, print_init
    print_init = False
    while have_not_buy:
        start = time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
        now = time.time()
        ddl = start - now
        if ddl <= 0.3:
            create_many()
            have_not_buy = False


if __name__ == '__main__':

    if mode == '1':  # 定时
        start_time = '{} {}'.format(str(datetime.datetime.today()).split()[0], input('hh:mm:ss==>'))
        pre_time = time.strftime('%H:%M:%S',
                                 time.localtime(time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S')) - 30))
        _start_time = time.strftime('%H:%M:%S',
                                    time.localtime(time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S')) - 5))
        get_goods_map(cmdt_id)
        get_aim_info()
        schedule.every().day.at(pre_time).do(prepare_work)
        schedule.every().day.at(_start_time).do(set_time)
        while need_to_buy:
            schedule.run_pending()
            if print_init:
                print('倒计时 %s sec' % int(time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S')) - time.time()))
            time.sleep(1)

    if mode == '2':  # 监控货号
        brand_list = {'nk': '100101', 'ad': '100103'}
        if keys:
            search_url = 'https://wxmall.topsports.com.cn/search/shopCommodity/list?searchKeyword=&current=1&pageSize=20&sortColumn=upShelfTime&sortType=desc&filterIds=TS%s&shopNo=%s&tssign=' % (
                brand_list[input('nk or ad==>')], shop)
        else:
            search_url = 'https://wxmall.topsports.com.cn/search/shopCommodity/list?searchKeyword=%s&current=1&pageSize=20&sortColumn=upShelfTime&sortType=desc&filterIds=TS%s&shopNo=%s&tssign=' % (
                key, brand_list[input('nk or ad==>')], shop)
        get_tokens()
        confirm_captchas()
        filter_expired()
        all_add_cart()
        get_create_infos()
        while have_not_searched:
            get_target_info(search_url)
            confirm_captchas()
            if aim_infos:
                check_captcha_num()
                create_many()
        else:
            have_not_searched = True
            all_add_cart()
            get_create_infos()

    if mode == '3':  # 监控已有链接
        get_tokens()
        confirm_captchas()
        filter_expired()
        all_add_cart()
        get_create_infos()
        while token_list and not dangerous:
            if check_stock():
                check_captcha_num()
                create_many()
                if success_list:
                    for _ in success_list:
                        token_list.remove(_['token'])
        # output_success()

    if mode == '4':  # 直接下单测试
        print('\n', 'TEST MODE', '====================', '\n')
        get_goods_map(cmdt_id)
        prepare_work()
        create_many()
        # output_success()

    if mode == '5':  # 没写好 上新筛选模式-------
        get_tokens()
        confirm_captchas()
        filter_expired()
        all_add_cart()
        get_create_infos()
        while token_list:
            _count = filter_()
            if _count:
                choose_id = random.choice(count)['id']
                get_goods_map(choose_id)
                check_captcha_num()

    if mode == '6':  # 商品详情
        get_goods_map(cmdt_id)
        check_captcha_num()
        print(details)
        for sku in skus_map[1:]:
            print(sku)
