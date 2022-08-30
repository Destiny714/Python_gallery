import time
import random
import C_stores
import schedule
import datetime
import threading
import Read_users
import Encrypt as e
import multiprocessing
from push import pusher

sell_time = ''
group_num = 2
openid_list = Read_users.openid_list
all_openid_list = openid_list
print('用户导入完毕', '用户数量', len(openid_list))
openid_list = openid_list[:30]


def count_create_orders(store_id):
    threads = []
    for openid in openid_list:
        thread = threading.Thread(target=e.create_order, args=[goodid,openid,store_id,buynum,10])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def create_orders(stores:list,user_list,good_id,buy_num,time_out):
    threads = []
    for openid in user_list:
        store = random.choice(stores)
        thread = threading.Thread(target=e.create_order, args=[good_id,openid,store,buy_num,time_out])
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def multi_create(stores:list):
    process_list = []
    lists_list = []
    for _ in range(len(openid_list) // group_num):
        lists_list.append(openid_list[_ * group_num:(_ + 1) * group_num])
    lists_list.append(openid_list[(len(openid_list) // group_num) * group_num:(len(openid_list) // group_num) * group_num + len(openid_list) % group_num])
    for _ in lists_list:
        process = multiprocessing.Process(target=create_orders,args=(stores,_,goodid,buynum,2))
        process.start()
        process_list.append(process)
    for _ in process_list:
        _.join()


def check_rate():
    test_time = 0
    sum_time = 0
    for _ in range(4):
        try:
            use_time = e.create_order(33,random.choice(all_openid_list),207,1,5) / 1000
            test_time += 1
            sum_time += use_time
        except Exception as error:
            print(error)
            pass
        time.sleep(1)
    avg_time = round(sum_time / test_time, 3)
    print(f'延迟{avg_time}s')
    return avg_time


def countdown():
    print('还有5秒')
    global y
    x = True
    while x:
        y = False
        if sell_time - time.time() <= early_time:
            count_create_orders(storeid)
            x = False


if __name__ == '__main__':
    buynum = 2
    goodid = 506
    storeid = 3007
    sell_time = e.get_sell_time(goodid)
    if not sell_time:
        print('======>补货模式')
        while openid_list:
            if e.new_get_stock(goodid,storeid,all_openid_list):
                create_orders([storeid],openid_list,goodid,buynum,2)
                pusher('出现库存',str(datetime.datetime.now()))
                if e.finish_list:
                    print('success:{}'.format(len(e.finish_list)))
                    with open('T_finished.txt', 'a', encoding='utf-8') as o:
                        for i in e.finish_list:
                            pusher('下单成功',str(i[2]))
                            o.write(str(i)+'\n')
                        o.close()
                    e.finish_list = []
                if e.finished_openid:
                    for invalid_id in e.finished_openid:
                        openid_list.remove(invalid_id)
                    e.finished_openid = []
            time.sleep(0.65)
    else:
        early_time = check_rate()
        print('======>倒计时模式 ====>抢购店铺:{} =====>本组用户数量{}'.format(C_stores.stores[storeid],len(openid_list)))
        pre_time = str(time.strftime('%H:%M:%S',time.localtime(sell_time - 5)))
        schedule.every().day.at(pre_time).do(countdown)
        y = True
        while y:
            schedule.run_pending()
            print('倒计时',sell_time - int(time.time()),'s')
            time.sleep(1)
        if e.finish_list:
            with open('T_finished.txt', 'a', encoding='utf-8') as o:
                for i in e.finish_list:
                    pusher('下单成功', str(i[2]))
                    o.write(str(i) + '\n')
                    openid_list.remove(i[0])
                o.close()
