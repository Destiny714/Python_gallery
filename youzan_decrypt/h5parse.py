# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# @author : Destiny_
# @file   : h5parse.py
# @time   : 2022/03/13
import re
import requests

if __name__ == '__main__':
    url = 'https://shop102077638.m.youzan.com/wscgoods/detail/3nkpzxcrrnxriaa?banner_id=f.98916189~goods.1~3~HC47DZI2&alg_id=0&slg=tagGoodList-default%2COpBottom%2Cuuid%2CabTraceId&components_style_layout=1&reft=1647152323306&spm=f.98916189&shopAutoEnter=1&is_share=1&dc_ps=2996520708546348035.300001&from_uuid=5cf3587f-9565-b4f1-61ed-4df42d5351c7&sf=wx_sm&share_cmpt=native_wechat'

    res = requests.get(url)
    res = res.text
    data: str = re.findall(r'window._global = (.*?)\n', res)[0]
    false = False
    true = True
    data = eval(data)
