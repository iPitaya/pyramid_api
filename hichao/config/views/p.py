# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.util.statsd_client import statsd

@view_defaults(route_name = 'p')
class PointView(View):
    def __init__(self, request):
        super(PointView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_p.get')
    @view_config(request_method = 'GET', renderer = 'json')
    def get(self):
        return 1

