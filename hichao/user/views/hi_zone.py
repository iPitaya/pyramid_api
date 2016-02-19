# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.util.pack_data import pack_data,version_ge
from hichao.forum.models.thread import (
        get_thread_ids_by_user_id,
        )
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.base.config import (
        MYSQL_MAX_INT,
        FALL_PER_PAGE_NUM,
        )
from hichao.util.object_builder import (
        build_thread_by_id,
        build_lite_thread_by_id,
        build_lite_post_by_id,
        )
from hichao.util.user_util import (
        is_deletable,
        is_owner,
        )
from hichao.util.statsd_client import statsd

@view_defaults(route_name = 'hi_zone')
class HiZoneView(View):
    def __init__(self, request):
        super(HiZoneView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_hi_zone.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        user_id = self.request.params.get('user_id', '')
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        flag = flag != '' and int(flag) or MYSQL_MAX_INT
        user_id = user_id != '' and int(user_id) or self.user_id
        if user_id == -2:
            self.error['error'] = 'User info expired.'
            self.error['errorCode'] = '20002'
            return '', {}
        if user_id == -1:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        crop = self.request.params.get('crop', '')
        crop = 1 if crop else 0
        ids = get_thread_ids_by_user_id(user_id, flag, FALL_PER_PAGE_NUM)
        ids = [id[0] for id in ids]
        more_img = self.request.params.get('more_pic', '')
        lite_thread = self.request.params.get('lite_thread', '')
        new_thread_flag = 0
        if (gf == 'iphone' and version_ge(gv, '6.4.0')) or (gf == 'android' and version_ge(gv, 640)):
            new_thread_flag = 1
        data = {}
        data['items'] = []
        for id in ids:
            com = {}
            if lite_thread:
                if new_thread_flag == 0:
                    com = build_lite_thread_by_id(id)
                else:
                    com = build_lite_post_by_id(id, self.user_id)
            else:
                com = build_thread_by_id(id, crop, more_img)
                #if self.user_id > 0 and is_deletable(self.user_id, com):
                #    com['component']['actions'][1]['isDeletable'] = '1'
                if com:
                    if self.user_id > 0 and is_owner(self.user_id, com):
                        com['component']['actions'][1]['isOwner'] = '1'
            if com:
                data['items'].append(com)
        if len(ids)==FALL_PER_PAGE_NUM:
            data['flag']=ids[len(ids)-1]
        return '', data


