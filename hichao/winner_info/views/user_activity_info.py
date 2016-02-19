# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.winner_info.models.user_activity_info import update_user_activity_info
from hichao.winner_info.models.topic_winner_attachinfo import update_winner_attachinfo
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.util.pack_data import pack_data
import time

@view_defaults(route_name = 'user_activity_info')
class UserActivityInfoView(View):
    def __init__(self, request):
        super(UserActivityInfoView, self).__init__()
        self.request = request

    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        user_id = int(self.user_id)
        name = self.request.params.get('name', '')
        cellphone = self.request.params.get('cellphone', '')
        email = self.request.params.get('email', '')
        address = self.request.params.get('address', '')
        _attachment = self.request.params.get('attachment', '')
        _id = self.request.params.get('type_id', '')
        _type = self.request.params.get('type', 'topic')
        if not user_id or user_id <= 0:
            self.error['error'] = 'Check user failed.'
            self.error['errorCode'] = '20001'
            return '', {}
        info_re = update_user_activity_info(user_id, name, cellphone, email, address, time.time())
        attach_re = update_winner_attachinfo(_id, user_id, _attachment, _type)
        if not _id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        if info_re and attach_re:
            return '', {}
        else:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return '', {}
