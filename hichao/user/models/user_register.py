# -*- coding:utf-8 -*-
import requests
import urllib2,urllib
import json
import re
from hichao.user.config  import (
        TEL_REGEXP,
        PASSWORD_MIN_SIZE,
        PASSWORD_MAX_SIZE,
        SECRET_KEY,
        SECRET_KEY_NOTICE,
        USER_REGISTER_TEMPLATE,
        FIND_PASSWORD_TEMPLATE,
    )

from hichao.base.config  import(
        LEANCLOUD_APP_ID_AND_KEY,
        SMS_SERVICE_TYPE,
    )
from icehole_client.throne_client  import  ThroneClient
from hichao.util.image_url  import default_user_avatar
import string
import hashlib
from hichao.user.models.mandao_sms  import (
    get_code_by_tel_with_mandao,
    check_code_and_tel_match,
    get_code_by_tel_with_weiwang,
    )
from hichao.util.statsd_client import timeit
from hichao.cache import get_cache_client
import cPickle
import redis

EXPIRED_TIME_MINUTE = 10
EXPIRED_TIME = EXPIRED_TIME_MINUTE*60
cache_client = get_cache_client()

timer = timeit('hichao_backend.m_user_register')

def get_code_from_redis(key):
    value = cache_client.get(key)
    if value:
        value = cPickle.loads(value)
    return value

def set_code_to_redis(key, value, time_out = EXPIRED_TIME):
    result = cache_client.setex(key, time_out, cPickle.dumps(value))
    return result

def check_password_legal(passwd):
    passwd_len = len(str(passwd)) 
    if passwd_len >= PASSWORD_MIN_SIZE and  passwd_len <= PASSWORD_MAX_SIZE:
        str_all = string.printable[:-5]
        for item in passwd:
            if item in str_all:
                continue
            else:
                return False
        return True
    else:
        return False

def check_tel_legal(number):
    regexp = TEL_REGEXP
    p = re.compile(regexp)
    if p.match(str(number)):
        return True
    else:
        return False
    #phoneprefix=['130','131','132','133','134','135','136','137','138','139','150','151','152','153','156','158','159','170','183','182','185','186','188','189']
    #if check_size_and_digit(str(number),11):
    #    if number[:3] in phoneprefix:
    #        return True
    #return False
        
def check_size_and_digit(number,size):
    if len(number) == int(size) and number.isdigit():
        return True
    else:
        return False

def save_user_tel_and_password(tel,passwd,app_name='mxyc'):
    '''  返回 -1 表示发生错误 '''
    throneclient = ThroneClient()
    #nickname = "{0}****{1}".format(tel[0:3],tel[7:]) 
    nickname = tel[0:3] + '****' + tel[7:]
    print "user %s registered as nickname %s" % (tel, nickname)
    '''函数定义  add_user_our(self, login_name, password, email, phone, nickname, user_type = 'mxyc') '''
    user_id = throneclient.add_user_our(tel,passwd,'',tel,nickname, app_name)
    if user_id:
        token = throneclient.get_token_by_uid(user_id)
        user_info = {}
        user_info["username"] = nickname
        user_info["avatar"] = default_user_avatar
        user_info["user_id"] = user_id
        user_info["token"] = token

        return user_info
    else:
        return  '-1'



def update_user_password_by_tel(tel,passwd):
    ''' 1 : 成功  0:更新不成功  -1：发生错误  '''
    throneclient = ThroneClient()
    user = throneclient.get_user_by_login_name(tel)
    result = ''
    if user:   
        result = throneclient.user_our_change_passwd(int(user.user_id),passwd)
    if result:
        if result.status:
            return '1'
        else:
            return '0'
    else:
        return '-1'


        

def check_tel_used(tel):
    '''  1 : 成功  0:更新不成功  -1：发生错误  ''' 
    throneclient = ThroneClient()
    isuser = throneclient.is_loginname(tel)
    if isuser:
        if isuser.status:
            return  '1'
        else:
            return  '0'
    else:
        return  '-1'

def get_request_headers(app_name = 'mxyc'):
    if app_name not in LEANCLOUD_APP_ID_AND_KEY:
        app_name = 'mxyc'
    app_id = LEANCLOUD_APP_ID_AND_KEY[app_name]['LEANCLOUD_APP_ID']
    app_key = LEANCLOUD_APP_ID_AND_KEY[app_name]['LEANCLOUD_APP_KEY']
    headers = {
        'X-AVOSCloud-Application-Id':app_id,
        'X-AVOSCloud-Application-Key':app_key,
        'Content-Type':'application/json'
    }
    return headers

@timer
def get_code_by_tel(number, send_type, app_name = 'mxyc'):
        url = 'https://leancloud.cn/1.1/requestSmsCode'
        headers = get_request_headers(app_name)
        query = {"mobilePhoneNumber": number}
        if send_type == 'user_register':
            query['template'] = USER_REGISTER_TEMPLATE
        if send_type == 'find_password':
            query['template'] = FIND_PASSWORD_TEMPLATE
        r = requests.post(url, data=json.dumps(query), headers=headers,verify=False)
        print app_name , send_type ,r.status_code , number, ' send SMS', r.text
        return r.status_code

@timer
def get_code_by_tel_for_notice(number, send_type, app_name = 'SMS_notice'):
        url = 'https://leancloud.cn/1.1/requestSmsCode'
        headers = get_request_headers(app_name)
        query = {"mobilePhoneNumber": number}
        if send_type == 'find_password':
            query['template'] = send_type
        if send_type:
            query['template'] = send_type
        else:
            query['template'] = 'default_notice'
        #query["business"] = '我是明星衣橱'
        r = requests.post(url, data=json.dumps(query), headers=headers,verify=False)
        print app_name , send_type ,r.status_code , number, ' send SMS', r.text
        return r.status_code

@timer
def check_tel_number_and_code(number,code,app_name = 'mxyc'):
    url = "https://leancloud.cn/1.1/verifySmsCode/{0}?mobilePhoneNumber={1}".format(code,number)
    print url, app_name
    headers = get_request_headers(app_name)
    r = requests.post(url, headers=headers,verify=False)
    return r.status_code

def check_change_password_status(oldpasswd,passwd1,passwd2,user_id):
    throneclient = ThroneClient()
    if oldpasswd and passwd1 and passwd2:
        try:
            #if passwd1 == passwd2:
                user_info = throneclient.get_user_by_uid(user_id)
                # 已经绑定 提交修改密码
                if user_info.loginname:
                    result_info = throneclient.user_ours_login(user_info.loginname, oldpasswd)
                    # 登录成功
                    if result_info.status:
                        # 执行修改密码操作
                        change_result_info = throneclient.user_our_change_passwd(user_id, passwd1)
                        # 修改成功
                        if change_result_info.status:
                            result = {
                                "status": 1,
                                "msg": "密码修改成功。",
                                "errorCode":'',
                                "error":'',
                                }
                        # 修改失败
                        else:
                            result = {
                                "status": 0,
                                "msg": "数据异常，请稍等后重试。",
                                "errorCode" : '30001',
                                "error" : 'change password error',
                            }
                    # 失败原密码不正确
                    else:
                        result = {
                            "status": 0,
                            "msg": "原始密码不正确，请修改后重试。",
                            "errorCode" : "30003",
                            "error": "username or password error",
                        }
                # 未绑定提示请先绑定
                else:
                    result = {
                        "status": 0,
                        "msg": "该用户尚未注册，请先注册，再尝试修改密码。",
                        "errorCode":"30001",
                        "error": "user no exist",
                    }
            # 密码不一致
            #else:
            #    result = {
            #        "status": 0,
            #        "msg": "两次密码输入不一致，请修改后重试。",
            #        "errorCode":"10001",
            #        "error":"两次密码输入不一致",
            #    }
        except Exception, e:
            print e
            result = {
                "status": 0,
                "msg": "服务器异常，请稍等后重试。",
                "errorCode":'30005',
                "error":"修改密码出现异常",
        }
    else:
        result = {
                "status": 0,
                "msg": "参数错误，请修改后重试。",
                "errorCode":'10002',
                "error":"有的参数为空",
        }
    return result


def check_telephone_and_sign(tel,sign):
    key = SECRET_KEY
    tel_key = hashlib.md5(key + tel).hexdigest()
    if tel_key.lower() == sign.lower():
        return True
    else:
        return False
    
def check_telephone_and_sign_for_notice(tel,sign):
    key = SECRET_KEY_NOTICE
    tel_key = hashlib.md5(key + tel).hexdigest()
    if tel_key.lower() == sign.lower():
        return True
    else:
        return False
    
def select_sms_service(number):
    sms_type = 'leancloud'
    if SMS_SERVICE_TYPE == 'all':
        num_yu = int(abs(hash(str(number))))%3
        if num_yu == 0:
            sms_type = 'leancloud'
        elif num_yu == 1:
            sms_type = 'mandao'
        else:
            sms_type = 'weiwang'
    else:
        sms_type = SMS_SERVICE_TYPE
    return sms_type
       

def get_code_by_tel_select(number, send_type, content = '', app_name = 'mxyc'):
    result = 200
    sms_type = select_sms_service(number)
    if sms_type == 'leancloud':
        result = get_code_by_tel(number, send_type, app_name)
        if result != 200:
            result = '验证码发送出现异常'
    if sms_type == 'mandao':
        temp = get_code_by_tel_with_mandao(number, send_type, app_name = 'mxyc')
        if temp['status'] == '1':
            result = 200
        else:
            result = temp['message']
    if sms_type == 'weiwang':
        temp = get_code_by_tel_with_weiwang(number, send_type, app_name = 'mxyc')
        if temp['status'] == '1':
            result = 200
        else:
            result = temp['message']
    if sms_type != 'leancloud':
        content = temp['content']
    print number,send_type,app_name,sms_type,result,content
    return result

def get_code_by_tel_for_notice_select(number, send_type, content = '', app_name = 'SMS_notice', sms_flag = 0):
    result = 200
    sms_type = select_sms_service(number)
    message = ''
    if sms_type == 'leancloud':
        result = get_code_by_tel_for_notice(number, send_type, app_name)
        if result != 200:
            result = '短信消息提醒发送出现异常'
    if sms_type == 'mandao':
        temp = get_code_by_tel_with_mandao(number, send_type, content, app_name = 'SMS_notice')
        if temp['status'] == '1':
            result = 200
        else:
            result = temp['status']
    if sms_type == 'weiwang':
        temp = get_code_by_tel_with_weiwang(number, send_type, content, app_name = 'SMS_notice', sms_type = sms_flag)
        if temp['status'] == '1':
            result = 200
        else:
            result = temp['status']
    if sms_type != 'leancloud':
        content = temp['content']
        message = temp['message']
    print number,send_type,app_name,sms_type,result,content,message
    return result

def check_tel_number_and_code_select(number,code,app_name = 'mxyc'):
    result = 200
    sms_type = select_sms_service(number)
    if sms_type == 'leancloud':
        result = check_tel_number_and_code(number,code,app_name)
    if sms_type == 'mandao':
        temp = check_code_and_tel_match(number,code)
        if temp['status'] == '1':
            result = 200
        else:
            result = temp['message']
    if sms_type == 'weiwang':
        temp = check_code_and_tel_match(number,code)
        if temp['status'] == '1':
            result = 200
        else:
            result = temp['message']
    return result

