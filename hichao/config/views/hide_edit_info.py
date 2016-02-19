# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.util.pack_data import pack_data
from hichao.base.views.view_base import View

@view_defaults(route_name = 'hide_edit_info')
class HideEditInfoView(View):
    def __init__(self, request):
        super(HideEditInfoView, self).__init__()
        self.request = request

    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        #gf = self.request.params.get('gf', '')
        #gv = self.request.params.get('gv', '0')
        #gn = self.request.params.get('gn', '')
        return '', {'hide':'1'}

