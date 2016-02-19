# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.util.pack_data import pack_data
from hichao.app.models.oauth2 import OAuth2AccessToken
from hichao.user.models.user import get_user_by_userid_openid
from hichao.base.views.view_base import View
from hichao.util.statsd_client import statsd

@view_defaults(route_name = 'exchange_access_token')
class ExchangeAccessTokenView(View):
    def __init__(self, request):
        super(ExchangeAccessTokenView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_exchange_access_token.post')
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        user_id = self.request.params.get('user_id', '')
        open_id = self.request.params.get('open_id', '')
        if not user_id or not open_id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        user = get_user_by_userid_openid(user_id, open_id)
        if user:
            access_token = OAuth2AccessToken.get_access_token(user_id)
            if not access_token or access_token == 'None':
                access_token = OAuth2AccessToken.access_token_new(user_id)
            username = user.username
            avatar = user.avatar
            return '', {'username':username, 'avatar':avatar, 'access_token':access_token}
        else:
            self.error['error'] = 'User info is illegal!'
            self.error['errorCode'] = '20001'
            return '', {}


