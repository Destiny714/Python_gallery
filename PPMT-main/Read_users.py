f = open('T_users.txt', 'r')
users = f.read()
openid_list = []
perm_list = []
for user in users.split('\n'):
    if user != '\n' and user != '':
        perm_list.append(user)
for _ in perm_list:
    if _ not in openid_list:
        openid_list.append(_)
f.close()
