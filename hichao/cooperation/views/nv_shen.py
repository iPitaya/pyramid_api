# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.util.pack_data import pack_data
from hichao.util.object_builder import build_nv_shen_entry
from hichao.util.statsd_client import statsd

@view_defaults(route_name = 'nvshen')
class NvShenView(View):
    def __init__(self, request):
        super(NvShenView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_nvshen.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        data = {}
        data['items'] = []
        entry = build_nv_shen_entry()
        if entry:
            data['items'].append(entry)
        return '', data

