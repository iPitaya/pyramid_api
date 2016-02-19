# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.config.CDN import (
        CDN_CHECK_PATH,
        )
from hichao.util.pack_data import pack_data
from hichao.base.views.view_base import View

@view_defaults(route_name = 'cdn_hosts')
class CDNHosts(View):
    def __init__(self, request):
        super(CDNHosts, self).__init__()
        self.request = request

    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        data = {}
        data['urls'] = CDN_CHECK_PATH
        return '', data

