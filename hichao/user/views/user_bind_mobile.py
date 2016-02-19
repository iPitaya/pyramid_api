# -*- coding:utf-8 -*-
from pyramid.view  import view_config
from pyramid.view  import view_defaults
from pyramid.response  import Response
from hichao.base.views.view_base  import View
from hichao.util.pack_data  import pack_data
from icehole_client.throne_client import ThroneClient
from hichao.app.views.oauth2 import check_permission
from hichao.util.statsd_client import statsd
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
from hichao.user.models.user import update_user_loginname_and_mobile_num
from hichao.util.user_util import user_change_password
from hichao.user.models.redis_sms  import  get_num_count_from_redis,minus_num_from_redis
from hichao.event.models.super_girls.sg_mobile import sg_send_code

@view_defaults(route_name='bind_mobile')
class BindMobileView(View):
    def __init__(self,request):
        super(BindMobileView,self).__init__()
        self.request = request

    @view_config(request_method='GET',renderer = 'json')
    def get(self):
        return {'ok':'ok'}

    @statsd.timer('hichao_backend.r_bind_mobile.post')
    @check_permission
    @view_config(request_method='POST',renderer = 'json')
    @pack_data
    def post(self):
        num = str(self.request.params.get('mobile_num',''))
        code = str(self.request.params.get('code',''))
        passwd = str(self.request.params.get('password',''))
        app_name = str(self.request.params.get('app_name','mxyc'))
        update_pwd = str(self.request.params.get('update_pwd','0'))
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
        if str(update_pwd) == '1' and not check_password_legal(passwd):
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
            message = status_code
        else:
            update_user_loginname_and_mobile_num(self.user_id, str(num),str(num))
            if passwd and update_pwd:
                user_change_password(self.user_id, passwd)
            data['status'] = '1'
            try:
                sg_send_code(num)
            except Exception,e:
                print e
        return message,data

@view_defaults(route_name='check_tel_code')
class CheckTelCodeView(View):
    def __init__(self,request):
        super(CheckTelCodeView,self).__init__()
        self.request = request

    @view_config(request_method='GET',renderer = 'json')
    def get(self):
        return {'ok':'ok'}

    @statsd.timer('hichao_backend.r_check_tel_code.post')
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
        status_code = check_tel_number_and_code_select(str(num),str(code),app_name)
        if status_code != 200:
            self.error['error'] = 'requst error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = status_code
        else:
            data['status'] = '1'
        return message,data

@view_defaults(route_name='bind_SMS')
class BindSendSMSToUserView(View):
    def __init__(self,request):
        super(BindSendSMSToUserView,self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_bind_SMS.post')
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
        check_reg = '1' #1需要检测注册 0不需要检测注册
        first_bind = str(self.request.params.get('first_bind','0'))
        data = {}
        if not check_tel_legal(str(num)):
            self.error['error'] = 'Telephone Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '该号码无效'
            return message,data
        if not check_telephone_and_sign(num,sign) or self.user_id <= 0:
            self.error['error'] = 'sign Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '非法请求'
            return message,data

        check_result = check_tel_used(num)
        if send_type == 'bind_mobile' and check_result == '1':
            self.error['error'] = 'tel Arguments error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            if str(first_bind) == '0':
                message = '换绑账号请填写新手机号'
            else:
                message = '手机号已被注册过'
            return message,data
        elif send_type == 'check_user' and check_result != '1':
            self.error['error'] = 'tel Arguments error'
            self.error['errorCode'] = '30001'
            data['status'] = '0'
            message = '手机号还没有被注册过'
            return message,data
        elif send_type == '' or send_type not in ['bind_mobile','check_user']:
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
