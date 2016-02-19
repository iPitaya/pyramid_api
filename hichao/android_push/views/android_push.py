# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.android_push.models.android_push import (
        get_last_android_push_id,
        )
from hichao.util.pack_data import pack_data
from hichao.base.views.view_base import View
from hichao.util.object_builder import build_android_push_by_id
from hichao.util.statsd_client import statsd

@view_defaults(route_name = 'android_push')
class AndroidPushView(View):
    def __init__(self, request):
        super(AndroidPushView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_android_push.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        version = self.request.params.get('version', '')
        last_id = int(get_last_android_push_id())
        data = {}
        if last_id > 0 and version != str(last_id):
            data = build_android_push_by_id(last_id)
        return '', data

