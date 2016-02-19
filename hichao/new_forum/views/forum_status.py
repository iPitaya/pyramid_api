# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        )
from hichao.util.object_builder import build_forum_status_by_ids
from hichao.util.statsd_client import statsd

@view_defaults(route_name = 'new_forum_status')
class ForumStatusView(View):
    def __init__(self, request):
        super(ForumStatusView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_new_forum_status.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        forum_ids = self.request.params.get('forum_ids', '')
        if forum_ids:
            forum_ids = forum_ids.split(',')
        else:
            forum_ids = []
        forum_4 = 0
        if not forum_ids:
            gf = self.request.params.get('gf', '')
            gv = self.request.params.get('gv', '')
            #if gv: gv = gv_float(gv)
            # 当gv<=5.2时，ios前端有bug，返回的版块个数必须为4的整数倍。
            if version_ge(5.2, gv) and gf == 'iphone':
                forum_4 = 1
        data = {}
        data['items'] = build_forum_status_by_ids(forum_ids, forum_4 = forum_4)
        return '', data

