# -*- coding:utf-8 -*-
from pyramid.view  import view_config
from pyramid.view  import view_defaults
from pyramid.response  import Response
from hichao.base.views.view_base  import View
from hichao.user.models.user_register import (
        get_code_by_tel,
        check_tel_number_and_code,
        get_code_by_tel_select,
        check_tel_number_and_code_select,
        check_tel_legal,
        check_size_and_digit,
        save_user_tel_and_password,
        check_tel_used,
        update_user_password_by_tel,
        check_change_password_status,
        check_password_legal,
        check_telephone_and_sign,
        get_code_by_tel_for_notice,
        get_code_by_tel_for_notice_select,
) 
from hichao.util.pack_data  import pack_data
from icehole_client.throne_client import ThroneClient
from hichao.app.views.oauth2 import check_permission
from hichao.user.models.user import (
        get_user_by_id,
        update_user_nickname,
    )
from hichao.util.statsd_client import statsd
from hichao.util.content_util import filter_tag
import requests
import json
import urllib2
from hichao.user.models.redis_sms  import  get_num_count_from_redis,minus_num_from_redis
from hichao.user.models.img_code import check_img_code
from hichao.event.models.super_girls.sg_mobile import sg_send_code

@view_defaults(route_name='send_SMS')
class SendSMSToUserView(View):
    def __init__(self,request):
        super(SendSMSToUserView,self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_send_SMS.post')
    @check_permission
    @view_config(request_method='POST',renderer = 'json')
    @pack_data
    def post(self):
        num = str(self.request.params.get('mobile_num',''))
        send_type = str(self.request.params.get('type',''))
        send_type = send_type.strip()
        sign = str(self.request.params.get('sign',''))
        app_name = str(self.request.params.get('app_name','mxyc'))
        content = str(self.request.params.get('content',''))  #暂时没用  为了以后动态内容扩展用
        data = {}
        if not check_tel_legal(str(num)):
            self.error['error'] = 'Telephone Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '该号码无效'
            return message,data
        if not check_telephone_and_sign(num,sign):
            self.error['error'] = 'sign Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '非法请求'
            return message,data

        check_result = check_tel_used(num)
        if send_type == 'user_register' and check_result == '1':
            self.error['error'] = 'tel Arguments error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = '手机号已被注册过'
            return message,data
        elif send_type == 'find_password' and check_result != '1':
            self.error['error'] = 'tel Arguments error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = '手机号还没有被注册过'
            return message,data
        elif send_type == '' or send_type not in ['user_register','find_password']:
            self.error['error'] = 'Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '参数错误'
            return message,data
            
        num_count = get_num_count_from_redis(num) 
        if int(num_count) <= 0: 
            self.error['error'] = 'requst error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = '短信消息提醒发送失败，24小时内只能发送5次'
            return message,data

        status_code = get_code_by_tel_select(str(num),send_type, app_name)
        if status_code != 200:
            self.error['error'] = 'requst error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = status_code
            return message,data
        else:
            data['status'] = '1'
            minus_num_from_redis(num)
        return '',data


@view_defaults(route_name='user_register')
class UserRegisterView(View):
    def __init__(self,request):
        super(UserRegisterView,self).__init__()
        self.request = request

    @view_config(request_method='GET',renderer = 'json')
    def get(self):
        return {'ok':'ok'}

    @statsd.timer('hichao_backend.r_user_register.post')
    @check_permission
    @view_config(request_method='POST',renderer = 'json')
    @pack_data
    def post(self):
        num = str(self.request.params.get('mobile_num',''))
        code = str(self.request.params.get('code',''))
        passwd = str(self.request.params.get('password',''))
        app_name = str(self.request.params.get('app_name','mxyc'))
        data = {}
        message = ''
        if not check_tel_legal(str(num)):
            self.error['error'] = 'Telephone Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '该号码无效'
            return message,data
            
        status_code = 0
        if not check_size_and_digit(str(code),6):
            self.error['error'] = 'Code Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '验证码无效'
            return message,data
        if check_tel_used(num) == '1':
            self.error['error'] = 'Code Arguments error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = '手机号已被注册过'
            return message,data
        if not check_password_legal(passwd):
            self.error['error'] = 'password Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '密码数据格式有问题'
            return message,data
        status_code = check_tel_number_and_code_select(str(num),str(code),app_name)
        if status_code != 200:
            self.error['error'] = 'requst error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = '手机号和验证码不符'
        else:
            user_info = save_user_tel_and_password(str(num),str(passwd),app_name) 
            if user_info == '-1':
                self.error['error'] = 'insert user msg error'
                self.error['errorCode'] = '30001'
                data['status'] = '0'
                message = '手机号和验证码不符'
            else:
                data['token'] = user_info['token']
                data['user_id'] = user_info['user_id']
                data['username'] = user_info['username']
                data['avatar'] = user_info['avatar']
                data['status'] = '1'
                try:
                    sg_send_code(num)
                except Exception,e:
                    print e
        return message,data


@view_defaults(route_name='find_password')
class UserFindPasswordView(View):
    def __init__(self,request):
        super(UserFindPasswordView,self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_find_password.post')
    @check_permission
    @view_config(request_method='POST',renderer = 'json')
    @pack_data
    def post(self):
        num = str(self.request.params.get('username',''))
        code = str(self.request.params.get('code',''))
        passwd = str(self.request.params.get('password',''))
        app_name = str(self.request.params.get('app_name','mxyc'))
        data = {}
        message = ''
        if not check_tel_legal(str(num)):
            self.error['error'] = 'Telephone Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '手机号不合法'
            return message,data
        if not check_size_and_digit(str(code),6):
            self.error['error'] = 'Code Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '验证码不合法'
            return message,data
        
        if check_tel_used(num) != '1':
            self.error['error'] = 'Code Arguments error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = '用户名还没有注册'
            return message,data

        if not check_password_legal(passwd):
            self.error['error'] = 'password Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '密码数据格式有问题'
            return message,data

        status_code = check_tel_number_and_code_select(str(num),str(code), app_name)
        if status_code != 200:
            self.error['error'] = 'requst error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = '手机号和验证码不符'
            return message,data
        else:
            result_status = update_user_password_by_tel(num,passwd)
            if result_status == '-1' or result_status == '0':
                self.error['error'] =  'error'
                self.error['errorCode'] = '30001'
                data['status'] = '0'
                message = '错误 请重新尝试'
            else:
                data['status'] = '1'
        return message,data



@view_defaults(route_name='change_password')
class UserChangePasswordView(View):
    def __init__(self,request):
        super(UserChangePasswordView,self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_change_password.post')
    @check_permission
    @view_config(request_method='POST',renderer = 'json')
    @pack_data
    def post(self):
        oldpasswd = str(self.request.params.get("oldpassword", None))
        passwd1 = str(self.request.params.get("newpassword", None))
        passwd2 = str(self.request.params.get("password2", None))
        data = {}
        for psd in [oldpasswd,passwd1]:
            if not check_password_legal(psd):
                self.error['error'] = 'password Arguments error'
                self.error['errorCode'] = '10001'
                data['status'] = '0'
                message = '密码数据格式有问题'
                return message,data
        result = check_change_password_status(oldpasswd,passwd1,passwd2,self.user_id)
        data['status'] = str(result['status'])
        message = result['msg']
        if data['status'] == '0':
            self.error['error'] = result['error']
            self.error['errorCode'] = result['errorCode']
        return message,data


@view_defaults(route_name='change_nickname')
class UserChangeNicknameView(View):
    def __init__(self,request):
        super(UserChangeNicknameView,self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_change_nickname.post')
    @check_permission
    @view_config(request_method='POST',renderer = 'json')
    @pack_data
    def post(self): 
        nickname = str(self.request.params.get("nickname", None))
        nickname = nickname.strip()
        nickname = filter_tag(nickname)
        nickname = nickname.replace('\n','')
        message = ''
        data = {}
        if nickname:
            result = update_user_nickname(self.user_id,nickname)
            if result:
                data['status'] = '1'
                get_user_by_id(self.user_id, use_cache = False)
            else:
                self.error['error'] = 'sql update error'
                self.error['errorCode'] = '30001'
                data['status'] = '0'
                message = '昵称修改失败'
        else:
            self.error['error'] = 'nickname Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '昵称不能为空'
        return message,data


@view_defaults(route_name='send_SMS_customer')
class SendSMSForCustomerView(View):
    def __init__(self,request):
        super(SendSMSForCustomerView,self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_send_SMS_customer.post')
    @check_permission
    @view_config(request_method='POST',renderer = 'json')
    @pack_data
    def post(self):
        num = str(self.request.params.get('mobile_num',''))
        send_type = str(self.request.params.get('type',''))
        sign = str(self.request.params.get('sign',''))
        app_name = str(self.request.params.get('app_name','mxyc'))
        content = str(self.request.params.get('content',''))
        #0默认正常验证码 1通知
        sms_type = int(self.request.params.get('sms_type',0))
        sms_type = 1
        data = {}
        if not check_tel_legal(str(num)):
            self.error['error'] = 'Telephone Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '该号码无效'
            return message,data
        if not check_telephone_and_sign(num,sign):
            self.error['error'] = 'sign Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '非法请求'
            return message,data

        if app_name != 'customer':
            self.error['error'] = 'Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '参数错误'
            return message,data
            
        status_code = get_code_by_tel_for_notice_select(str(num),send_type, content, app_name, sms_type)
        if status_code != 200:
            self.error['error'] = 'requst error'
            self.error['errorCode'] = '20001'
            data['status'] = '0'
            message = '客服短信消息提醒发送出现异常'
            return message,data
        else:
            data['status'] = '1'
        return '',data

@view_defaults(route_name='web_send_SMS')
class WebSendSMSToUserView(View):
    def __init__(self,request):
        super(WebSendSMSToUserView,self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_web_send_SMS.post')
    @check_permission
    @view_config(request_method='POST',renderer = 'json')
    @pack_data
    def post(self):
        num = str(self.request.params.get('mobile_num',''))
        send_type = str(self.request.params.get('type',''))
        send_type = send_type.strip()
        sign = str(self.request.params.get('sign',''))
        app_name = str(self.request.params.get('app_name','mxyc'))
        content = str(self.request.params.get('content',''))  #暂时没用  为了以后动态内容扩展用
        img_code = str(self.request.params.get('img_code',''))
        data = {}
        if not check_tel_legal(str(num)):
            self.error['error'] = 'Telephone Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '该号码无效'
            return message,data
        if not check_img_code(sign,img_code):
            self.error['error'] = 'sign Arguments error'
            self.error['errorCode'] = '10021'
            data['status'] = '0'
            message = '非法请求,验证码错误'
            return message,data

        check_result = check_tel_used(num)
        if send_type == 'user_register' and check_result == '1':
            self.error['error'] = 'tel Arguments error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = '手机号已被注册过'
            return message,data
        elif send_type == 'find_password' and check_result != '1':
            self.error['error'] = 'tel Arguments error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = '手机号还没有被注册过'
            return message,data
        elif send_type == '' or send_type not in ['user_register','find_password']:
            self.error['error'] = 'Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '参数错误'
            return message,data
            
        num_count = get_num_count_from_redis(num) 
        if int(num_count) <= 0: 
            self.error['error'] = 'requst error'
            self.error['errorCode'] = '20001'
            data['status'] = '0'
            message = '短信消息提醒发送失败，24小时内只能发送5次'
            return message,data

        status_code = get_code_by_tel_select(str(num),send_type, app_name)
        if status_code != 200:
            self.error['error'] = 'requst error'
            self.error['errorCode'] = '20001'
            data['status'] = '0'
            message = status_code
            return message,data
        else:
            data['status'] = '1'
            minus_num_from_redis(num)
        return '',data

