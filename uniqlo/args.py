import json
import time

import requests

users = ['bearer44bc0868-d5a1-42b1-a980-2bb890e271d8',
         'bearered59e8de-df22-40e0-918c-e467b306f826',
         'bearerb643bcc9-0d86-4280-8ce8-8546a5331034',
         'bearerdf83cd55-e060-4cd9-b798-d65c2a68bdd7',
         'bearerec3bb31f-1922-4acb-a7b6-d83113176578']
m_or_p = {'1': 'm', '2': 'p'}
mobile_or_pc = m_or_p[input('1.小程序登录 2.浏览器登录====>')]
mode = mobile_or_pc
num = int(input('输入购买数量:'))
product_list = [['短袖', 'u0000000028562'], ['托特包', 'u0000000028561'], ['test', 'u0000000029222']]


def get_state(user):
    url = 'https://i.uniqlo.cn/%s/hmall-ur-service/customer/address/list/zh_CN' % mode
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
    r = requests.get(url=url, headers=headers, verify=False)
    js = r.json()
    state = js['resp'][0]['state']
    return state


def get_express_fee(user):
    url = 'https://i.uniqlo.cn/%s/hmall-bd-service/zoneDeliveryModeValue/selectForSumFrees/zh_CN' % mode
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
    data = json.dumps({
        "orders": [{
            "orderNum": 1,
            "city": get_state(user),
            "areaType": 2,
            "expressCompany": "DEFAULT",
            "additionalCost": 0,
            "products": [{
                "freightTemplateId": 10001,
                "quantity": 1
            }]
        }]
    })
    r = requests.post(url=url, headers=headers, data=data, verify=False)
    r = r.json()
    fee = r['resp'][0]['totalAmount']
    return fee


def test_network():
    url = 'https://i.uniqlo.cn/%s/hmall-favorite-service/customer/favorite/list/zh_CN' % mode
    headers = {
        'Accept': '*/*',
        'Authorization': users[0],
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
        'Connection': 'keep-alive',
        'Cookie': '',
        'X-Tingyun-Id': 'f28-GhFRwsA;r=559771775'
    }
    start = time.time()
    requests.get(url=url, headers=headers, verify=False)
    end = time.time()
    use = round((end - start) * 1000, 2)
    print('Network response in', use, 'ms')


def rf(tks: list):
    for tk in tks:
        url = 'https://d.uniqlo.cn/%s/hmall-ur-service/token/refreshAccessToken' % mode
        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'Accept': 'application/json',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
            'Content-Type': 'application/json',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.uniqlo.cn/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Authorization': 'Bearer ' + tk[0] if mode == 'p' else 'bearer' + tk[0]
        }
        data = json.dumps({"refreshToken": tk[1]})
        r = requests.post(url=url, headers=headers, data=data, verify=False)
        r = r.json()
        new_token = r['access_token']
        tk[0] = new_token
    return tks
