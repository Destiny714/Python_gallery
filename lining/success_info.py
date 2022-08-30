import time
import requests
import warnings
import json

warnings.filterwarnings('ignore')

success_orders = []

with open('success.txt', 'r') as f:
    all_success = f.read()
    for success in all_success.split('\n'):
        if success != '':
            success_orders.append(eval(success))


def search_order(order_no,auth):
    url = 'https://api.store.lining.com/tradec/v1/orderquery/detail'
    headers = {
        'Host': 'api.store.lining.com',
        'Connection': 'keep-alive',
        'auth-token': auth,
        'content-type': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip,compress,br,deflate',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x18000731) NetType/WIFI Language/zh_CN',
    }
    data = json.dumps({
        "orderNo": order_no,
        "needGoodsComment": True,
        "saasId": "8324992625302181585",
        "source": "2"
    })
    res = requests.post(url=url, data=data, headers=headers, verify=False).json()
    status = res['data']['orderBaseVO']['orderStatusName']
    createtime = int(res['data']['orderBaseVO']['createTime'])
    lifetime = int((3600 - (time.time() - createtime/1000))/60)
    tel = res['data']['logistics']['receiverPhone']
    name = res['data']['logistics']['receiverName']
    ordername = res['data']['orderItemVOS'][0]['goodsName']
    ordersize = res['data']['orderItemVOS'][0]['specifications'][1]['specValue']
    print('订单状态:{}  付款时间:{}分钟  姓名:{}  电话:{}  商品:{}  尺码:{}'.format(status,lifetime,name,tel,ordername,ordersize))


if __name__ == '__main__':
    for success in success_orders:
        search_order(success[0],success[1])
