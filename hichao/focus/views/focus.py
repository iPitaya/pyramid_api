# -*- coding: utf-8 -*-
from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.util.pack_data import pack_data
from icehole_client.search_manage_client import SearchManageClient
from hichao.util.statsd_client import statsd
from hichao.collect.models.brand import (
        brand_collect_new,
        brand_collect_rm,
        )

@view_defaults(route_name = 'focus')
class FocusView(View):
    def __init__(self, request):
        super(FocusView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_focus.post')
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        return self.handle('follow')

    @statsd.timer('hichao_backend.r_focus.delete')
    @view_config(request_method = 'DELETE', renderer = 'json')
    @pack_data
    def delete(self):
        return self.handle('unfollow')

    @check_permission
    def handle(self, act):
        if self.user_id < 1:
            self.error['error'] = 'User info error.'
            self.error['errorCode'] = '20002'
            return '', {}
        _id = self.request.params.get('id', '')
        if not _id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
        client = SearchManageClient()
        special_info = client.get_special_word_by_id(int(_id))
        if act == 'follow':
            if special_info and special_info.brand_id > 0:
                res = brand_collect_new(int(self.user_id),[int(special_info.brand_id)])
            else:
                res = client.user_follow_tag(int(self.user_id), int(_id))
        else:
            if special_info and special_info.brand_id > 0:
                res = brand_collect_rm(int(self.user_id),int(special_info.brand_id))
            else:
                res = client.user_unfollow_tag(int(self.user_id), int(_id))
        if not res:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
        return '', {}

