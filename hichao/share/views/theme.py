# -*- coding:utf-8 -*-

from hichao.util.statsd_client import statsd
from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.util.pack_data import pack_data, version_ge
from hichao.util.object_builder import build_theme_detail_by_id
from pyramid.response import Response
import json

@view_defaults(route_name = 'share_theme')
class ShareThemeView(View):
    def __init__(self, request):
        super(ShareThemeView, self).__init__()
        self.request = request

    @statsd.timer("hichao_backend.r_share_theme.get")
    @view_config(request_method = 'GET', renderer = 'share/theme.html')
    @pack_data
    def get(self):
        theme_id = self.request.params.get('id', '')
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        app_api = self.request.params.get('ga', '')
        data = build_theme_detail_by_id(theme_id)
        data['gf'] = gf
        data['gv'] = gv
        data['id'] = theme_id
        if (gf == 'iphone' and version_ge(gv, '6.4.0')) or (gf == 'android' and version_ge(gv, 640)):
            datas = {}
            datas['data'] = data
            datas['message'] = ''
            datas['data']['appApi'] = app_api
            for index, anchor in enumerate(datas['data']['anchors']):
                datas['data']['anchors'][index]['action'] = json.loads(anchor['action'])
            for index, tag in enumerate(datas['data']['tags']):
                datas['data']['tags'][index]['action'] = json.loads(tag['action'])
            return Response(json.dumps(datas),content_type = 'application/json')
        return '', data

