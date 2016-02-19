# -*- coding:utf-8 -*-
import base64
import json
import hashlib
from hichao.base.config import ORDER_DETAIL_URL
import requests

def get_message_from_ecshop_interface(source, app_uid, method, token, version, d_attr):
    API_SECRET_KEY = '71e5d83f6480523cb7b52e13445c2865'
    data = {}
    data['source'] = 'mxyc_ios'
    data['version'] = version
    data['method'] = method
    data['token'] = token
    data['app_uid'] = app_uid
    data['data'] = base64.b64encode(json.dumps(d_attr))
    sign = str(data['source']) + str(data['version']) + str(data['method']) + str(data['token']) + str(data['app_uid']) + str(data['data']) + API_SECRET_KEY
    data['sign'] = hashlib.md5(sign).hexdigest()
    url = ORDER_DETAIL_URL
    r = requests.post(url, data = data,verify=False)
    return r.text

def get_user_hongbao_cupon_msg(source, app_uid, method, token, version, d_attr):
    msg = get_message_from_ecshop_interface(source, app_uid, method, token, version, d_attr)
    if not msg:
        return {}
    result = eval(msg)
    if result.get('response',{}).get('code',-1) != 0:
        return result.get('response',{}).get('data',{})
    else:
        return {}
#d_attr = {'userid':1891706}
#print get_user_hongbao_cupon_msg(source = 'mxyc_ios', app_uid = '2254984', method = 'user.promote.data', token = 'q9d4AhDxnOgD5cJXki3CvMPc_6uCPVSWrHi4CfQgWJo', version = '6.3.1', d_attr = d_attr)
