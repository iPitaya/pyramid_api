# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.util.pack_data import pack_data
from hichao.app.views.oauth2 import check_permission
from hichao.util.statsd_client import statsd
from hichao.user.models.user import get_user_by_id

@view_defaults(route_name = 'statistics_info')
class StatisticsInfoView(View):
    def __init__(self, request):
        super(StatisticsInfoView, self).__init__()
        self.request = request

    @statsd.timer("hichao_backend.r_statistics_info.get")
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        data = {}
        ip = self.request.environ.get('HTTP_X_REAL_IP', '')
        if not ip: ip = self.request.client_addr
        data['ip'] = ip
        if self.user_id < 1:
            return '', data
        user = get_user_by_id(self.user_id)
        data['userRank'] = str(user.get_rank())
        return '', data

