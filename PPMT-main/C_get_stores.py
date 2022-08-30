# import requests
# import time
# import json
# import encrypt as e
#
# ts = str(int(time.time_ns() / 1e6))
# proxies = {'http': 'http://121.201.49.230:16818', 'https': 'http://121.201.49.230:16818'}
# data = {
#     'query_type': 1
# }
# url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/store/cities?query_type={}&sign={}&time={}&version={}'.format(
#     data['query_type'], e.get_sign(data, 'GET'), ts, e.version)
# r = requests.get(url, proxies=proxies)
# r.encoding = 'utf-8'
# r = r.json()
# all_store = []
# for city in r['data']['cities']:
#     city_name = city['name']
#     data = {
#         "city": city_name,
#         "has_point": True,
#         "lat": 79.116188049316406,
#         "lon": 111.46060180664062,
#         "page_num": 1,
#         "page_size": 999,
#         "parent_type": 1,
#         "openid": "oZdQ34yuqd1XKXJ5fGFgXPY--r0Y",
#     }
#     url = 'https://popvip-go.paquapp.com/miniapp/v2/sg/store/self_pickup_query'
#     data = json.dumps(e.get_sign(data,'POST'),ensure_ascii=False)
#     r = requests.post(url,data=data.encode('utf-8'),proxies=proxies).json()
#     store_list = r['data']['stores']
#     f = open('T_stores.txt', 'a')
#     f.write(city_name+':')
#     for store in store_list:
#         store_id = store['id']
#         store_name = store['name']
#         all_store.append({store_id:store_name})
#         text = str({store_id:store_name}) + ','
#         f.write(text)
#         print(city_name,store_name,'finished')
#     f.write('\n')
#     f.close()
#     time.sleep(1.5)
# print(all_store)
# 宁波市，南京市，杭州市，兰州市，银川市，上海市
citys = ['哈尔滨市']
store_dict = {}
with open('T_stores.txt', 'r') as f:
    stores_pure = f.read()
    stores = stores_pure.split('\n')
    for city_stores in stores:
        if city_stores.split(':',1)[0] in citys:
            for store_info in city_stores.split(':', 1)[1:]:
                if store_info != '':
                    stores = store_info.split(',')
                    for store in stores:
                        if store != '':
                            store = eval(store)
                            for i in store:
                                print(i,store[i])
                                store_dict[int(i)] = store[i]
print(store_dict)

