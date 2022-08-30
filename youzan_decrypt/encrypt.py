import json
import time
import base64
import random
import string
from Crypto.Cipher import AES

aim_url = 'https://h5.youzan.com/wscgoods/tee-app/detail-v2.json?app_id=wxdcc11cd7703c0e8d&access_token=8ae46d136280385ef47f933a1f37ed&kdt_id=44077958&alias=35z97hcsmrudiz8&scene=1008&subKdtId=0&shopAutoEnter=1&banner_id=f.83554713~image_ad.5~0~uHxOSgON&notQueryVoucher=1&is_share=1&from_uuid=FsJDfxTHJNrELJf1616473512245&oid=0&ump_alias=&ump_type=&activityId=&activityType='

sid_list = [
    'YZ902950859487641600YZJ3ggejC0',
    'YZ903051808784842752YZyF1b00od',
    'YZ902952604116701184YZvqq9zK2s',
    'YZ903234614924464128YZ0YLt93gN',
    'YZ903051399852797952YZWPq13QAp',
    'YZ903051128271831040YZeeFAg2jf',
    'YZ903239839223652352YZbNCAgpPT'
]


def milli_time():
    t = int(time.time_ns() / 1000000)
    return t


def get_Random_String(n):
    x = string.printable
    salt = ''
    for _ in range(n):
        salt += random.choice(x)
    return salt


def pad(text):
    byte = 16 - len(text) % 16
    return text + get_Random_String(byte - 1) + chr(byte)


def get_data():
    org_data = {"touchData": {}, "gyroscopeTrack": [], "speedTrack": [],
                "pageExposureTime": {"start": milli_time(), "now": milli_time() + 4333}}
    return org_data


def init_(rdm):
    final_str = ''
    word_list = []
    for _ in rdm:
        word_list.append(_)
    word_list = list(reversed(word_list))
    for _ in word_list:
        final_str += _
    key = final_str.split('@')[0]
    iv = final_str.split('@')[1]
    return [key, iv]


def encrypt(rdmstr):
    _init = init_(rdmstr)
    text = json.dumps(get_data()).replace(' ', '').replace('\n', '')
    text = pad(text).encode('utf-8')
    key = _init[0].encode('utf-8')
    iv = _init[1].encode('utf-8')
    aes = AES.new(key, AES.MODE_CBC, iv)
    encrypt_aes = aes.encrypt(text)
    encrypted_text = base64.encodebytes(encrypt_aes).decode('utf-8')
    return encrypted_text.replace('\n', '')
