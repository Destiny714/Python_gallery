import Encrypt as e
if __name__ == '__main__':
    f = open('T_finished.txt', 'r')
    old_results = f.read()
    f.close()
    if old_results:
        with open('T_finished.txt', 'w') as f:
            new_results = []
            for old_result in old_results.split('\n'):
                if old_result != '':
                    if old_result not in new_results:
                        new_results.append(old_result)
            text = ''
            for i, new_result in enumerate(new_results):
                if i + 1 < len(new_results):
                    text += (new_result + '\n')
                else:
                    text += new_result
            f.write(text)
            f.close()
        f = open('T_finished.txt', 'r')
        results = f.read()
        results = results.split('\n')
        print('查询成功订单:',len(results))
        for result in results:
            if result != '\n' and result != '':
                result = eval(result)
                try:
                    add_info = e.get_address(result[0])
                    if add_info != '无默认地址':
                        user_info = str(e.get_user_info(add_info['id'])).replace('{',',').replace('}','').replace("'","")
                        order_info = str(e.get_order_info(result[0],result[1])).replace('{',',').replace('}','').replace("'","")
                        print('姓名:',add_info['name'],user_info,order_info)
                    else:
                        order_info = str(e.get_order_info(result[0], result[1])).replace('{', ',').replace('}', '').replace("'",
                                                                                                                            "")
                        print(order_info)
                except Exception as e:
                    print(e)
                    pass
        print('查询完毕')
    else:
        print('无结果')

