import Encrypt as e
import time

f = open('T_users.txt', 'r')
old_users = f.read().split('\n')
users = []
num = 0
for u in old_users:
    if u != '':
        if u not in users:
            users.append(u)
        else:
            num += 1
if num > 0:
    print('重复{}个'.format(num))
for user in users:
    print(user)
    e.get_address(user)
    time.sleep(2)
if e.limited:
    print(f'限流{len(e.limited)}个账号')
if e.invalid_users:
    for i in e.invalid_users:
        users.remove(i)
    print(len(e.invalid_users), '个用户无效')
f.close()
valid_users = users
print(len(valid_users), '个有效用户')
text = ''
for i,valid_user in enumerate(valid_users):
    if i+1 < len(valid_users):
        text += (valid_user + '\n')
    else:
        text += valid_user
with open('T_users.txt', 'w') as f:
    f.write(text)

