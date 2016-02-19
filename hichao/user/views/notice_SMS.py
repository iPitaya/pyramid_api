# -*- coding:utf-8 -*-
from pyramid.view  import view_config
from pyramid.view  import view_defaults
from pyramid.response  import Response
from hichao.base.views.view_base  import View
from hichao.user.models.user_register import (
        get_code_by_tel,
        check_tel_number_and_code,
        check_tel_legal,
        check_size_and_digit,
        save_user_tel_and_password,
        check_tel_used,
        update_user_password_by_tel,
        check_change_password_status,
        check_password_legal,
        check_telephone_and_sign,
        check_telephone_and_sign_for_notice,
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
from hichao.user.models.redis_sms  import  get_num_count_from_redis_notice



@view_defaults(route_name='send_SMS_notice')
class SendSMSForNoticeView(View):
    def __init__(self,request):
        super(SendSMSForNoticeView,self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_send_SMS_notice.post')
    @check_permission
    @view_config(request_method='POST',renderer = 'json')
    @pack_data
    def post(self):
        num = str(self.request.params.get('mobile_num',''))
        send_type = str(self.request.params.get('type',''))
        send_type = send_type.strip()
        sign = str(self.request.params.get('sign',''))
        app_name = str(self.request.params.get('app_name','SMS_notice'))
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
        if not check_telephone_and_sign_for_notice(num,sign):
            self.error['error'] = 'sign Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '非法请求'
            return message,data

        if app_name != 'SMS_notice':
            self.error['error'] = 'Arguments error'
            self.error['errorCode'] = '10001'
            data['status'] = '0'
            message = '参数错误'
            return message,data
           
        #限制每天每个手机号码发送次数   
        num_count = get_num_count_from_redis_notice(num)
        if int(num_count) <= 0: 
            self.error['error'] = 'requst error'
            self.error['errorCode'] = '20001'
            data['status'] = '0'
            message = '短信消息提醒发送失败，24小时内只能发送10次'
            return message,data
            
        status_code = get_code_by_tel_for_notice_select(str(num),send_type, content, app_name, sms_type)
        if status_code != 200:
            self.error['error'] = 'requst error'
            self.error['errorCode'] = '20001'
            data['status'] = '0'
            message = status_code
            return message,data
        else:
            data['status'] = '1'
        return '',data

