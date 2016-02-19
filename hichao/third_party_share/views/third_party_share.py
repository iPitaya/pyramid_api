# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.third_party_share.models.third_party_share import add_third_party_share
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.util.pack_data import pack_data
from hichao.util.statsd_client import statsd
import time

@view_defaults(route_name = 'third_party_share')
class ThirdPartyShareView(View):
    def __init__(self, request):
        super(ThirdPartyShareView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_third_party_share.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        type_id = self.request.params.get('type_id', '')
        type = self.request.params.get('type', '')
        third_party = self.request.params.get('third_party', 'weixin')
        tm = time.time()
        if not type_id or not type:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        re = add_third_party_share(self.user_id, type_id, type, tm, third_party)
        if re <= 0:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return '', {}
        else:
            return '', {}

