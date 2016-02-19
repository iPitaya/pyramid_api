# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from pyramid.httpexceptions import (
        HTTPFound,
        )
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.event.models.nv_shen.user_new import is_nv_shen_user
import time

get_nv_shen_quan_url = "http://static.hichao.com/rs/rotate_v2/index.html?access_token={0}&_={1}"
act_url = "http://static.hichao.com/rs/rotate_v2/bonus.html?access_token={0}&_={1}"

@view_defaults(route_name = 'event_nv_shen')
class NvShenQuanView(View):
    def __init__(self, request):
        super(NvShenQuanView, self).__init__()
        self.request = request

    @check_permission
    @view_config(request_method = 'GET')
    def get(self):
        access_token = self.request.params.get('access_token')
        has_nv_shen_quan = is_nv_shen_user(self.user_id)
        _headers = [('Cache-Control','max-age=0, private, no-store, no-cache, must-revalidate')]
        if not has_nv_shen_quan:
            return HTTPFound(location = get_nv_shen_quan_url.format(access_token, time.time()), headers = _headers)
        return HTTPFound(location = act_url.format(access_token, time.time()), headers = _headers)

