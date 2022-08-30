import base64
import json
import requests
import rsa
import time
from Crypto.Cipher import AES

# login
TOKEN_TYPE = 'Bearer'
TOKEN = '7686b8c6-c720-4bf4-ad55-25fefacbfc10'

DOMAIN = 'https://wxmall.topsports.com.cn'

# common.js this.iv
IV = 'f74ae0290a9e4b64'

# 需要请求接口地址
# l = '/serviceTerms/getServiceTerms'
link = '/shopCommodity/queryShopCommodityDetail/73336fdd5738410993c95acddf1052c5'
# 时间戳
time = int(time.time() * 1e3)
# 构造加密参数
m = 'tsmall#{}#{}'.format(time, link)

# topsports_decrypt/init
init_data = {
    "code": 1,
    "bizCode": 20000,
    "bizMsg": "成功",
    "data": "fs0+VFvqj7fZhOcSEG6B08wcEOXwynSrD5qvwOvDw+pQoklTctA3s5px/pi3dPiYiDUZzo0KEkw+8ZPRqjtkiT+6S3WuWtvCuQHV29mKfdkkoPpWIwikVsy2sjO56qz65rT6Lwsd0isPHHngrNQ1ta5XFGHbrBxjiA2dl0phrrk="
}

headers = {
    'Authorization': '{} {}'.format(TOKEN_TYPE, TOKEN),
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.9(0x1800092c) NetType/WIFI Language/zh_CN'
}

# 读取私钥, common.js - this.privateKey = xx
privateKey = rsa.PrivateKey.load_pkcs1(open('pk.pem', 'rb').read())
# 获取 AES password
word = rsa.decrypt(base64.b64decode(init_data['data']), privateKey).decode('utf-8')
print('AES加密password: ' + word)


class PrpCrypt(object):

    def __init__(self, key, iv):
        self.ciphertext = None
        self.key = key.encode('utf-8')
        self.mode = AES.MODE_CBC
        self.iv = iv.encode('utf-8')
        # block_size 128位

    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16但是不是16的倍数，那就补足为16的倍数。
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.iv)
        text = self.pkcs7padding(text)
        print(text)
        self.ciphertext = cryptor.encrypt(bytes(text, encoding='utf-8'))
        return str(base64.b64encode(self.ciphertext), encoding='utf8')

    @staticmethod
    def pkcs7padding(text):
        bs = AES.block_size  # 16
        length = len(text)
        bytes_length = len(bytes(text, encoding='utf-8'))
        # note：utf-8编码时英文1byte，中文3byte
        padding_size = length if (bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        # note: chr(padding)看与其它语言的约定，有的使用'\0'
        padding_text = chr(padding) * padding
        return text + padding_text


crypto = PrpCrypt(key=word, iv=IV)
tssign = crypto.encrypt(m)

target = '{}{}?tssign={}'.format(DOMAIN, link, tssign)
print(target)

# response = requests.get(target, headers=headers).json()
# print(response)

# post example

data = {
    "shopNo": "NKCD94",
    "productCode": "BQ6472-105",
    "productSkuNo": "20210524003170",
    "productSizeCode": "6.5",
    "productSkuId": "98c72441d4ef499bbe013205d5c1cdb3",
    "shopCommodityId": "f45197dd360e46c68769f2ee370f5853",
    "brandNo": "NK",
    "num": 1,
    "merchantNo": "TS",
    "liveType": 0,
    "roomId": "",
    "roomName": ""
}

response = requests.get(target, headers=headers).json()
print(response)
