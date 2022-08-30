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
        for result in results:
            if result != '\n' and result != '':
                result = eval(result)
                open_id = str(result[0])
                order_id = str(result[1])
                e.cancel_orders(open_id=open_id, order_no=order_id)
