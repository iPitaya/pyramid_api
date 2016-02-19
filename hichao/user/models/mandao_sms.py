# -*- coding:utf-8 -*-
import requests
import urllib2,urllib
import json
import re
import string
import hashlib
import random
from hichao.cache import get_cache_client
import cPickle
import redis
#from hichao.base.config  import CACHE_CONFIG

#cache_client = get_cache_client()
EXPIRED_TIME_MINUTE = 10
EXPIRED_TIME = EXPIRED_TIME_MINUTE*60

#CACHE_CONFIG = dict(
#    host = '192.168.1.222',
#    port = 5555,
#    db = 1,
#    socket_connect_timeout = 1.2,
#    socket_timeout = 1.2,
#    )

#pool = redis.ConnectionPool(host = '192.168.1.222',port = 5555,db = 1)
#pool = redis.ConnectionPool(**CACHE_CONFIG)
#CACHE_CONFIG['connection_pool'] = pool
#cache_client = redis.StrictRedis(connection_pool=pool)
cache_client = get_cache_client()

def get_code_from_redis(key):
    value = cache_client.get(key)
    if value:
        value = cPickle.loads(value)
    return value

def set_code_to_redis(key, value, time_out = EXPIRED_TIME):
    result = cache_client.setex(key, time_out, cPickle.dumps(value))
    return result

def del_code_from_redis(key):
    result = cache_client.delete(key)
    return result

def generate_SMS_verification_code():
    ''' 生成短信验证码 '''
    code = 123456
    random.seed()
    code = random.randint(0,1000000)
    code = str(code)
    if len(code) < 6:
        code = '0'*(6 - len(code)) + code
    return code

def generate_SMS_content(content, key):
    ''' 生成带验证码的内容 '''
    hasCode = content.find('{{code}}')
    if hasCode:
        code = generate_SMS_verification_code()
        content = content.replace('{{code}}',code)
        content = content.replace('{{ttl}}',str(EXPIRED_TIME_MINUTE))
        result = set_code_to_redis(key, code)
        if not result:
            content = ''
        print  content,'content'
    return content

def compatible_old_SMS_content(content, send_type, app_name = 'mxyc'):
    ''' 兼容老的短信内容 '''
    name = '【明星衣橱】'
    data = {
    'find_password' : name + '您的验证码是:{{code}}，您正在找回明星衣橱登录平台密码，请在{{ttl}}分钟内完成验证。',
    'user_register' : name + '您的验证码是:{{code}}，您正在使用明星衣橱手机号注册业务，请在{{ttl}}分钟内完成验证。',
    'bind_mobile' : name + '您的验证码是:{{code}}，此验证码只用于绑定或更换绑定明星衣橱手机号，请在{{ttl}}分钟内完成验证。',
    'check_user' : name + '您的验证码是:{{code}}，此验证码只用于绑定或更换绑定明星衣橱手机号，请在{{ttl}}分钟内完成验证。',
    'customer_notice' : name + '您有新的用户咨询消息，请尽快登录明星衣橱商家后台客服查看~',
    'default_notice' : '【明星衣橱】您有新的消息，请尽快登录明星衣橱商家后台查看消息~',
    'order_notice' : name + '您有待发货的订单，请尽快登录明星衣橱商家后台订单管理页面处理~~',
    'refund_notice' : name + '您有新退款申请，请尽快登录明星衣橱商家后台退货退款页面处理~~',
    'agreeRefund' : '【明星衣橱】 糖小卷来报！您的退款申请商家已经同意了，退款会原路返回您的账户。退款详情您也可以打开明星衣橱APP进行查询哦：http://www.hichao.com/download ',
    'agreeReturn' : '【明星衣橱】糖小卷来报！您的退货申请商家已经同意了，不要忘记在订单详情里及时填写物流信息哦。您也可以打开明星衣橱APP，说不定会有意外惊喜呢：http://www.hichao.com/download ',
    'businessGetGoods' : '【明星衣橱】商家告诉小卷已经收到了您发来的退货，退款将于近期返还到您的账户，有任何问题您可以打开明星衣橱APP或拨打电话：400-650-6468直接联系我们的客服。',
    'businessNotGetGoods' : '【明星衣橱】 商家未收到您的退货，交易即将完成，有任何问题请您及时打开明星衣橱APP或拨打电话：400-650-6468联系我们的客服。',
    'businessShipping' : '【明星衣橱】 Hi，我是糖小卷。女神您钦点的货已经送到快递小哥手里了！不要太心急哦。订单详情您也可以打开明星衣橱APP进行查询：http://www.hichao.com/download ',
    'disagreeRefund' : '【明星衣橱】糖小卷来报！商家拒绝了您的退款申请，我已经帮您狠狠教训他了！有任何问题您可以打开明星衣橱APP或拨打电话：400-650-6468直接联系我们的客服。',
    'disagreeReturn' : '【明星衣橱】糖小卷来报！商家拒绝了您的退货申请，我已经帮您狠狠教训他了！有任何问题您可以打开明星衣橱APP或拨打电话：400-650-6468直接联系我们的客服。',
    'warn_msg' : '【明星衣橱】近期有不法分子冒充明星衣橱商家或工作人员进行诈骗。若您有任何订单、售后问题，请直接登录明星衣橱APP操作，如需人工服务请直接在APP内联系客服或拨打电话400-650-6468！',
    }
    if (app_name == 'customer' or app_name == 'SMS_notice') and send_type == 'find_password':
        ''' 兼容leancloud数据 '''
        content = name + '您有新的用户咨询消息，请尽快登录明星衣橱商家后台客服网页查看~'
    if not content:
        if send_type in data.keys():
            return data[send_type]
    return content

def send_code_by_tel_with_mandao(number, content, send_type = '', app_name = 'mxyc'):
    ''' 发送验证码通过漫道 '''
    url = 'http://sdk.entinfo.cn:8061/mdgxsend.ashx'
    query = {'sn':'SDK-MDQ-010-00132',
    'pwd':'186EC37078B4B27A77869821CD7A48B9',
    #'mobile':'18301686676',
    #'content':'hello%E3%80%90%E6%BC%AB%E9%81%93%E7%A7%91%E6%8A%80%E3%80%91',
    'ext':'',
    'stime':'',
    'rrid':'',
    'msgfmt':''}
    query['mobile'] = number
    query['content'] = content
    r = requests.get(url, params = query)
    return {'status':r.status_code,'message':r.text}

def get_code_by_tel_with_mandao(number, send_type, content = '' , app_name = 'mxyc'):
    ''' 发送短信 '''
    content = compatible_old_SMS_content(content, send_type, app_name)
    data = {}
    hasCode = content.find('{{code}}')
    code_redis = get_code_from_redis(number)
    data['content'] = content
    if hasCode >= 0:
        if not code_redis:
            content = generate_SMS_content(content, number)
            if not content:
                data['status'] = '-1'
                data['message'] = '内容为空，发送失败'
                return data 
        else:
            data['status'] = '0'
            data['message'] = '验证码已经发送没有验证，10分钟内不能连续发送'
            return data
    data['content'] = content
    result = send_code_by_tel_with_mandao(number, content)
    if result['status'] == 200 and result['message'] > 0:
        data['status'] = '1'
        data['message'] = '发送成功'
    else:
        data['status'] = '-1'
        data['message'] = str(result['message'])
            
    return data

    
def send_code_by_tel_with_weiwang(number, content, send_type = '', app_name = 'mxyc', sms_type = 0):
    ''' 发送验证码通过微网 '''
    if not content:
        return {'status':-1,'message':'内容为空'}
    url = 'http://cf.51welink.com/submitdata/Service.asmx/g_Submit'
    data = {}
    data['sname'] = 'dlmxyc'
    data['spwd'] = 'YG5g2HRO'
    data['scorpid'] = ''
    if sms_type == 0:
        data['sprdid'] = '1012818'
    elif sms_type == 1:
        data['sprdid'] = '1012808'
    else:
        data['sprdid'] = '1012812'
    print data['sprdid'], sms_type
    data['sdst'] = str(number)
    data['smsg'] = content
    head ={}
    head['Content-Type'] = 'application/x-www-form-urlencoded'
    r = requests.post(url,data = data, headers = head)
    pattern = re.compile('<State>(.*)</State>')
    match = pattern.search(r.text)
    status_code = match.group().replace('<State>','').replace('</State>','')
    if str(status_code) == '0':
        status_code = 200
    pattern = re.compile('<MsgState>(.*)</MsgState>')
    match = pattern.search(r.text)
    content = match.group().replace('<MsgState>','').replace('</MsgState>','')
    pattern = re.compile('<MsgID>(.*)</MsgID>')
    match = pattern.search(r.text)
    msgid = match.group().replace('<MsgID>','').replace('</MsgID>','')
    print msgid

    return {'status':status_code,'message':content}

def get_code_by_tel_with_weiwang(number, send_type, content = '' , app_name = 'mxyc', sms_type = 0):
    ''' 发送短信 '''
    content = compatible_old_SMS_content(content, send_type, app_name)
    data = {}
    hasCode = content.find('{{code}}')
    code_redis = get_code_from_redis(number)
    if sms_type and content.find("退订回T") < 0:
        content += "退订回T"
    data['content'] = content
    if hasCode >= 0:
        if not code_redis:
            content = generate_SMS_content(content, number)
            if not content:
                data['status'] = '-1'
                data['message'] = '内容为空，发送失败'
                return data 
        else:
            data['status'] = '0'
            data['message'] = '验证码已经发送没有验证，10分钟内不能连续发送'
            return data
    data['content'] = content
    result = send_code_by_tel_with_weiwang(number, content, send_type, app_name, sms_type)
    if result['status'] == 200 and result['message'] > 0:
        data['status'] = '1'
        data['message'] = '发送成功'
    else:
        data['status'] = '-1'
        data['message'] = str(result['message'])
            
    return data

def check_code_and_tel_match(number, code):
    ''' 判断验证码和手机号是否匹配 '''
    code_redis = get_code_from_redis(number)
    data = {}
    if code_redis:
        if code_redis == code:
            del_code_from_redis(number)
            data['status'] = '1'
            data['message'] = '验证通过'
        else:
            data['status'] = '-1'
            data['message'] = '验证码和手机号不匹配'
    else:
        data['status'] = '0'
        data['message'] = '您的验证码失效，请重新获取'
    print data['status'],data['message']
    return data    
        

