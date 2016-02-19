# -*- coding: utf-8 -*-
from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from hichao.base.views.view_base import View
from hichao.base.lib.require import require, RequirementException
from hichao.user.models.device import device_update_by_devicetoken, device_new, get_device_by_devicetoken
from hichao.util.pack_data import pack_data
from hichao.base.celery.db import celery
from hichao.util.statsd_client import statsd
from hichao.app.models.oauth2 import OAuth2AccessToken
from hichao.user.models.device import (
        device_OnOff_state_by_devicetoken,
        device_relate_state_by_devicetoken,
    )

import time
import requests

@view_defaults(route_name='device')
class DeviceView(View):
    def __init__(self, request):
        super(DeviceView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_device.post')
    @view_config(request_method='POST', renderer='json')
    @pack_data
    def post(self):
        devicetoken = self.request.params.get('device_token', '')
        third_push_name = self.request.params.get('tpn', '')
        if third_push_name == 'ios':
            third_push_name = ''
        if not third_push_name:
            third_push_name = ''
        data = {}
        message = ''
        if devicetoken:
            start = time.time()
            device_token = get_device_by_devicetoken(devicetoken, third_push_name)
            appname = self.request.params.get('gn', '')
            open_uuid = self.request.params.get('gi', '')
            mac = self.request.params.get('mac', '')
            version = self.request.params.get('gv', '')
            platform = self.request.params.get('gf', '')
            token = self.request.params.get('access_token', '')
            tpn_token = self.request.params.get('tpn_token', '')
            user_id = 0
            if token:
                user_id = OAuth2AccessToken.get_user_id(token)
                if not user_id:
                    user_id = 0
            enable = 1
            if device_token:
                if device_token.enable == 0:
                    enable = 1
                else:
                    enable = device_token.enable
                start = time.time()
                logintime = self.request.params.get('logintime', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
                device_update_by_devicetoken(devicetoken, appname, open_uuid, mac, version, platform, enable, third_push_name, user_id, tpn_token, logintime)
            else:
                start = time.time()
                enable = 1
                device_new(devicetoken, appname, open_uuid, mac, version, platform, enable,third_push_name, user_id, tpn_token)
        #print time.ctime(), 'o2o_callback mac_md5:', mac, '\tgi:', open_uuid
        #call_o2o.delay(mac, open_uuid)
        return message, data

@celery.task
def call_o2o(mac, gi):
    try:
        params = {'mac_md5':mac}
        r = requests.post('http://api2.haobao.com/ads/device_callback?gi=%s' % gi, data = params)
        print r.text
    except Exception, ex:
        print Exception, ex


@view_defaults(route_name='device_push_state')
class DevicePushUpdateView(View):
    def __init__(self, request):
        super(DevicePushUpdateView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_device_push_state.post')
    @view_config(request_method='POST', renderer='json')
    @pack_data
    def post(self):
        devicetoken = self.request.params.get('device_token', '')
        state_type = self.request.params.get('state_type', '')
        third_push_name = self.request.params.get('tpn', '')
        if third_push_name == 'ios':
            third_push_name = ''
        data = {}
        message = ''
        if devicetoken:
            start = time.time()
            device_token = get_device_by_devicetoken(devicetoken,third_push_name)
            token = self.request.params.get('access_token', 0)
            user_id = 0
            if token:
                user_id = OAuth2AccessToken.get_user_id(token)
            if device_token:
                #start = time.time()
                #logintime = self.request.params.get('logintime', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
                if state_type == 'login':
                    device_relate_state_by_devicetoken(devicetoken,user_id,third_push_name = third_push_name)
                if state_type == 'logout':
                    device_relate_state_by_devicetoken(devicetoken,0, third_push_name = third_push_name)
                if state_type == 'push_on':
                    device_OnOff_state_by_devicetoken(devicetoken,1, third_push_name = third_push_name)
                if state_type == 'push_off':
                    device_OnOff_state_by_devicetoken(devicetoken,2, third_push_name = third_push_name)
        return message, data


@view_defaults(route_name='device_state')
class DevicePushStateView(View):
    def __init__(self, request):
        super(DevicePushStateView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_device_state.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def post(self):
        devicetoken = self.request.params.get('device_token', '')
        third_push_name = self.request.params.get('tpn', '')
        if third_push_name == 'ios':
            third_push_name = ''
        data = {}
        message = ''
        if devicetoken:
            device_token = get_device_by_devicetoken(devicetoken,third_push_name)
            if device_token:
                data['enable'] = str(device_token.enable)
                data['user_id'] = str(device_token.user_id)
        return message,data

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

