# -*- coding: utf-8 -*-
import traceback
import requests
from urllib import quote
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from hichao.base.views.view_base import View
from hichao.base.lib.require import require, RequirementException
from hichao.base.config import THIRD_PARTY_APP
from hichao.third.models.oauth2 import third_party_oauth2_token_new 
from hichao.third.config import FAKE_TOKEN_URL
from hichao.user.models.user import user_new
from hichao.app.models.oauth2 import OAuth2AccessToken 
from time import time

import json

class OAuth2Mixin(View):
    def __init__(self, request):
        super(OAuth2Mixin, self).__init__()
        self.request = request

    @view_config(route_name='connect_auth2_token', request_method='GET', renderer = 'json')
    def _connect_auth2_token(self):
        resp = dict()
        return '' 

    def _third_party_oauth2_token_new(self, user_id, access_token, refresh_token=None):
        return third_party_oauth2_token_new(user_id, access_token, self.THIRD_PARTY, refresh_token)

    def _user_new(self, username, email, avatar, url, open_id, gender, location):
        user_id = user_new(username, 0, email, avatar, url, 0,
             self.THIRD_PARTY, open_id, gender, location)
        _access_token = OAuth2AccessToken.get_access_token(user_id)
        if not _access_token:
            _access_token = OAuth2AccessToken.access_token_new(user_id)
            #临时性解决方案, 有待分析原因
            if not _access_token:
                _access_token = OAuth2AccessToken.access_token_new(user_id)
        return user_id, _access_token

class WeiboMixin(OAuth2Mixin):
    THIRD_PARTY = 'weibo'
    _BASE_URL = 'https://api.weibo.com/oauth2/%s'
    _OAUTH_AUTHORIZE_URL = 'https://open.weibo.cn/oauth2/authorize' 
    _OAUTH_ACCESS_TOKEN_URL = _BASE_URL % 'access_token'
    _OAUTH_NO_CALLBACKS = False
    API = THIRD_PARTY_APP[THIRD_PARTY]

    @view_config(route_name='connect_weibo_authorize', request_method='GET')
    def connect_authorize(self):
        url = '%s?client_id=%s&redirect_uri=%s&display=mobile&forcelogin=true'\
                %(self._OAUTH_AUTHORIZE_URL, self.API['client_id'], self.API['redirect_uri'])
        return HTTPFound(location=url)
        

    @view_config(route_name='connect_weibo', request_method='GET', renderer = 'json')
    def _connect_code(self):
        code = self.request.params.get('code', '')
        if not code:
            self.error['errorCode'] = '20014'
            self.error['error_code'] = '20014'
            self.error['error'] = quote('获取用户信息失败')
            url = "%s?hichao_status=500&third_party=weibo&error=%s&errorCode=%s&error_code=%s"\
                    %(FAKE_TOKEN_URL, self.error['error'], self.error['errorCode'], self.error['error_code'])
            return HTTPFound(location = url)
        data = {
            'redirect_uri': self.API['redirect_uri'],
            'code': code,
            'extra_params': {'grant_type': 'authorization_code'},
            'client_id': self.API['client_id'],
            'client_secret': self.API['client_secret'],
        }

        try:
            r = requests.post(self._OAUTH_ACCESS_TOKEN_URL, data = data)
            r = r.json()
            uid = r['uid']
            access_token = r['access_token']

            user_id, username, _access_token, avatar = self._get_user_info(access_token, uid)
            #tid = self._third_party_oauth2_token_new(user_id, access_token)
            url = "%s?token=%s&username=%s&user_id=%s&avatar=%s&hichao_status=200&third_party=weibo"\
                    % (FAKE_TOKEN_URL, _access_token, quote(username), user_id, avatar)
        except Exception, ex:
            self.error['errorCode'] = '20014'
            self.error['error_code'] = '20014'
            self.error['error'] = quote('获取用户信息失败')
            url = "%s?hichao_status=500&third_party=weibo&error=%s&errorCode=%s&error_code=%s"\
                    %(FAKE_TOKEN_URL, self.error['error'], self.error['errorCode'], self.error['error_code'])
        return HTTPFound(location=url)

    @view_config(route_name='connect_weibo_sso', request_method='POST', renderer = 'json')
    def connect_sso(self):
        access_token = self.request.params['access_token'] 
        app_api = self.request.params.get('ga', '')                     # generic app api
        uid = self.request.params['uid'] 
        try:
            user_id, username, _access_token, avatar = self._get_user_info(access_token, uid)


            #tid = self._third_party_oauth2_token_new(user_id, access_token)
            return {
                'data':{
                'appApi': app_api,
                'username': username,
                'user_id': user_id,
                'avatar': avatar,
                'token': _access_token,
                },
                'hichao_status': 200,
            }
        except Exception, ex:
            print Exception, ex
            self.error['data'] = {'appApi':app_api}
            self.error['errorCode'] = '20014'
            self.error['error_code'] = '20014'
            self.error['error'] = '获取用户信息失败'
            self.error['hichao_status'] =  500
            return self.error

    def _get_user_info(self, access_token, uid):
        data = { 
            'access_token':access_token,
            'uid':uid
        }

        r = requests.get('https://api.weibo.com/2/users/show.json?access_token=%s&uid=%s'%(access_token, uid))
        r = json.loads(r.text)
        username = r['name'].encode('utf8')
        url = r['url'].encode('utf8')
        avatar = r['avatar_large'].encode('utf8')
        location = r['location'].encode('utf8')
        gender = r['gender'].encode('utf8')
        if gender == 'm':
            gender = 1
        else:
            gender = 0

        user_id, _access_token = \
                self._user_new(username, 0, avatar, url, uid, gender, location)

        return user_id, username, _access_token, avatar


class QQMixin(OAuth2Mixin):
    THIRD_PARTY = 'qq'
    _BASE_URL = 'https://graph.qq.com/'
    _OAUTH_AUTHORIZE_URL = 'https://graph.qq.com/oauth2.0/authorize' 
    _OAUTH_ACCESS_TOKEN_URL = 'https://graph.qq.com/oauth2.0/token' 
    _OAUTH_NO_CALLBACKS = False
    API = THIRD_PARTY_APP[THIRD_PARTY]

    @view_config(route_name='connect_qq_authorize', request_method='GET')
    def connect_authorize(self):
        url = '%s?client_id=%s&redirect_uri=%s&display=mobile&response_type=code&scope=get_user_info'\
                %(self._OAUTH_AUTHORIZE_URL, self.API['client_id'], self.API['redirect_uri'])
        return HTTPFound(location=url)

    @view_config(route_name='connect_qq', request_method='GET', renderer = 'json')
    def _connect_code(self):
        code = self.request.params.get('code', '')
        if not code:
            self.error['errorCode'] = '20014'
            self.error['error_code'] = '20014'
            self.error['error'] = quote('获取用户信息失败')
            url = "%s?hichao_status=500&third_party=weibo&error=%s&errorCode=%s&error_code=%s"\
                    %(FAKE_TOKEN_URL, self.error['error'], self.error['errorCode'], self.error['error_code'])
            return HTTPFound(location = url)

        data = {
            'redirect_uri': self.API['redirect_uri'],
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': self.API['client_id'],
            'client_secret': self.API['client_secret'],
        }

        try:
            r = requests.get(self._OAUTH_ACCESS_TOKEN_URL, params = data)
            access_token = r.text.split('&')[0].split('=')[1]

            uid = self._get_open_id(access_token)

            user_id, username, _access_token, avatar = self._get_user_info(access_token, uid)
            #self._third_party_oauth2_token_new(user_id, access_token)

            url = "%s?token=%s&username=%s&user_id=%s&avatar=%s&hichao_status=200&third_party=qq"\
                    % (FAKE_TOKEN_URL, _access_token, quote(username), user_id, avatar)
        except Exception, ex:
            print Exception, ex
            self.error['errorCode'] = '20014'
            self.error['error_code'] = '20014'
            self.error['error'] = quote('获取用户信息失败')
            url = "%s?hichao_status=500&third_party=qq&error=%s&errorCode=%s&error_code=%s"\
                    %(FAKE_TOKEN_URL, self.error['error'], self.error['errorCode'], self.error['error_code'])
        return HTTPFound(location=url)

    @view_config(route_name='connect_qq_sso', request_method='POST', renderer = 'json')
    def connect_sso(self):
        access_token = self.request.params['access_token'] 
        uid = self.request.params['uid'] 
        app_api = self.request.params.get('ga', '')                     # generic app api
        try:
            user_id, username, _access_token, avatar = self._get_user_info(access_token, uid)
            tid = self._third_party_oauth2_token_new(user_id, access_token)
            return {
                'data':{
                'appApi': app_api,
                'username': username,
                'user_id': user_id,
                'avatar': avatar,
                'token': _access_token,
                },
                'hichao_status': 200,
            }
        except Exception, ex:
            print Exception, ex
            self.error['data'] = {'appApi':app_api}
            self.error['errorCode'] = '20014'
            self.error['error_code'] = '20014'
            self.error['error'] = '获取用户信息失败'
            self.error['hichao_status'] =  500
            return self.error

    def _get_open_id(self, access_token):

        data = { 
            'access_token':access_token
        } 

        r = requests.get('https://graph.qq.com/oauth2.0/me', params=data)
        openid = r.text.split(' ')[1].split('"')[-2]
        return openid 

    def _get_user_info(self, access_token, uid):

        data = { 
            'access_token':access_token,
            'openid':uid,
            'oauth_consumer_key':self.API['client_id'],
            'format':'json',
        } 

        r = requests.get('https://graph.qq.com/user/get_user_info', params=data)
        r = r.json()

        username = r['nickname'].encode('utf-8')
        gender = r['gender'].encode('utf-8')
        avatar = r['figureurl_2'].encode('utf-8')
        if gender == '男':
            gender = 1
        else:
            gender = 0

        user_id, _access_token = \
                self._user_new(username, 0, avatar, 0, uid, gender, 0)
        return user_id, username, _access_token, avatar


class TaobaoMixin(OAuth2Mixin):
    _time = {}
    THIRD_PARTY = 'taobao'
    _BASE_URL = 'https://oauth.taobao.com/'
    _OAUTH_AUTHORIZE_URL = 'https://oauth.taobao.com/authorize' 
    _OAUTH_ACCESS_TOKEN_URL = 'https://oauth.taobao.com/token' 
    _OAUTH_NO_CALLBACKS = False
    API = THIRD_PARTY_APP[THIRD_PARTY]

    @view_config(route_name='connect_taobao_authorize', request_method='GET')
    def connect_authorize(self):
        url = '%s?client_id=%s&redirect_uri=%s&view=wap&response_type=code&scope=get_user_info'\
            %(self._OAUTH_AUTHORIZE_URL, self.API['client_id'], self.API['redirect_uri'])
        return HTTPFound(location=url)

    @view_config(route_name='connect_taobao', request_method='GET', renderer = 'json')
    def _connect_code(self):
        self._time['start'] = time()
        
        code = self.request.params.get('code', '')
        if not code:
            self.error['errorCode'] = '20014'
            self.error['error_code'] = '20014'
            self.error['error'] = quote('获取用户信息失败')
            url = "%s?hichao_status=500&third_party=weibo&error=%s&errorCode=%s&error_code=%s"\
                    %(FAKE_TOKEN_URL, self.error['error'], self.error['errorCode'], self.error['error_code'])
            return HTTPFound(location = url)

        data = {
            'client_id': self.API['client_id'],
            'client_secret': self.API['client_secret'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.API['redirect_uri'],
        }

        try:
            self._time['get_access_token_start'] = time()

            r = requests.post(self._OAUTH_ACCESS_TOKEN_URL, data=data)
            r = r.json()
            uid = r['taobao_user_id']
            username = r['taobao_user_nick']
            token_type = r['token_type']
            access_token = r['access_token'].encode('utf-8')
            refresh_token = r['access_token'].encode('utf-8')
            self._time['get_access_token_end'] = time()

            user_id, username, _access_token, avatar = self._get_user_info(access_token, uid)


            #try:
            #    self._third_party_oauth2_token_new(user_id, access_token, refresh_token)
            #except Exception, ex:
            #    print ex, '_token_new'

            url = "%s?token=%s&username=%s&user_id=%s&avatar=%s&hichao_status=200&third_party=taobao"\
                    % (FAKE_TOKEN_URL, _access_token, quote(username), user_id, avatar)
        except Exception, ex:
            print  Exception, ex
            self._time['get_access_token_end'] = time()
            self.error['errorCode'] = u'20014'
            self.error['error_code'] = u'20014'
            self.error['error'] = quote('获取用户信息失败')
            url = "%s?hichao_status=500&third_party=taobao&error=%s&errorCode=%s&error_code=%s"\
                    %(FAKE_TOKEN_URL, self.error['error'], self.error['errorCode'], self.error['error_code'])

        self._time['get_user_info_end'] = time()
        print self._time
        print self._time['get_user_info_end'] - self._time['start'], self._time['get_access_token_end'] - self._time['get_access_token_start'], self._time['get_user_info_end'] - self._time['get_access_token_end'] 
        return HTTPFound(location=url)

    @view_config(route_name='connect_taobao_sso', request_method='POST', renderer = 'json')
    def connect_sso(self):
        access_token = self.request.params['access_token'] 
        uid = self.request.params['uid'] 
        app_api = self.request.params.get('ga', '')                     # generic app api
        try:
            user_id, username, _access_token, avatar = self._get_user_info(access_token, uid)
            tid = self._third_party_oauth2_token_new(user_id, access_token)
            return {
                'data':{
                'appApi': app_api,
                'username': username,
                'user_id': user_id,
                'avatar': avatar,
                'token': _access_token,
                },
                'hichao_status': 200,
            }
        except Exception, ex:
            print Exception, ex
            self.error['data'] = {'appApi':app_api}
            self.error['errorCode'] = '20014'
            self.error['error_code'] = '20014'
            self.error['error'] = '获取用户信息失败'
            self.error['hichao_status'] =  500
            return self.error

    def _get_user_info(self, access_token, uid):
        data = { 
            'access_token':access_token,
            'app_key':self.API['client_id'],
            'format':'json',
            'method':'taobao.user.buyer.get',
            'v':'2.0',
            'fields':'user_id,nick,sex,location,avatar,email'
        } 

        try:
            r = requests.get('https://eco.taobao.com/router/rest', params=data, verify=False)
            r = r.json()
        except Exception, ex:
            print ex


        r = r['user_buyer_get_response']['user']
        username =r['nick'].encode('utf-8')
        try:
            avatar =r['avatar'].encode('utf-8')
        except Exception:
            avatar = 'http://a.tbcdn.cn/app/sns/img/default/avatar-120.png'
        uid = uid
        # 淘宝 taobao.user.buyer.get  API 变动
        #uid = 0

        try:
            user_id, _access_token = \
                self._user_new(username, 0, avatar, 0, uid, 0, 0)
        except Exception, ex:
            print 'user_new', Exception, ex

        return user_id, username, _access_token, avatar


if __name__ == "__main__":
    pass

