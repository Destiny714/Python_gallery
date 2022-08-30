import requests
import json

user1 = 'c4e5782c76cfe388c47397216ac0fbbd'


def cop(user):
    url = 'https://wechat.palace-skateboards.cn/westore-palace-core/mini/order/add'
    headers = {
        'Host': 'wechat.palace-skateboards.cn',
        'Connection': 'keep-alive',
        'token': user,
        'content-type': 'application/json',
        # 'Accept-Encoding': 'gzip,compress,br,deflate',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x1800072f) NetType/WIFI Language/zh_CN',
        'Referer': 'https://servicewechat.com/wx696ff953a85e38f9/12/page-frame.html'
    }
    data = {
        "email": "test@test.com",
        "payFirstName": "test",
        "payLastName": "test",
        "payIdNum": "",
        "payerPhone": "",
        "deliveryFirstName": "test",
        "deliveryLastName": "test",
        "deliveryIdNum": "",
        "deliveryMobile": "",
        "province": "浙江",
        "city": "",
        "district": "",
        "postcode": "",
        "address": "test",
        "createOrderType": 1,
        "productId": 2296,
        "productSkuId": 7718
    }
    data = json.dumps(data)
    r = requests.post(url=url, headers=headers, data=data)
    print(r.text)


cop(user1)
