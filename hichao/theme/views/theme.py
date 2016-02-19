# -*- coding:utf-8 -*-

from hichao.util.statsd_client import statsd
from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.config import FALL_PER_PAGE_NUM
from hichao.base.views.view_base import View
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        )
from hichao.util.object_builder import (
        build_theme_detail_by_id,
        build_theme_list_item_by_id,
        build_topic_list_item_by_theme_id,
        )
from hichao.theme.models.tag import get_tag_by_id
from hichao.theme.models.theme import (
        get_latest_theme_ids,
        get_theme_ids_by_tag_id,
        )
from hichao.theme.config import THEME_PV_PREFIX, THEME_UV_PREFIX
from pyramid.response import Response
from pyramid.httpexceptions import (
    HTTPSeeOther,
    HTTPNotFound,
    )
from hichao.base.config import ERROR_404_PAGE
from hichao.base.lib.redis import redis
from hc.redis.count import Counter, SetCounter
import time
import datetime
import json


@view_defaults(route_name='theme')
class ThemeView(View):

    def __init__(self, request):
        super(ThemeView, self).__init__()
        self.request = request

    @statsd.timer("hichao_backend.r_theme.get")
    @view_config(request_method='GET', renderer='theme/theme.html')
    @pack_data
    def get(self):
        theme_id = self.request.params.get('id', '')
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        gi = self.request.params.get('gi', '')
        app_api = self.request.params.get('ga', '')
        if not theme_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10001'
            self.error['message'] = ''
            self.error['data'] = {}
            self.error['data']['appApi'] = app_api
            return Response(json.dumps(self.error), content_type = 'application/json')
        pv_key = THEME_PV_PREFIX.format(theme_id)
        uv_key = THEME_UV_PREFIX.format(theme_id)
        pv_counter = Counter(redis)
        uv_counter = SetCounter(redis, uv_key)
        pv_counter._incr(pv_key)
        uv_counter.add(gi)
        data = build_theme_detail_by_id(theme_id)
        if data:
            share = data['share']
            share['share']['detailUrl'] = share['share']['detailUrl'] + '&gf={0}&gv={1}'.format(gf, gv)
            data['share'] = json.dumps(share)
        else:
            return HTTPSeeOther(location = ERROR_404_PAGE)
        data['gf'] = gf
        data['gv'] = gv
        data['id'] = theme_id
        #if (gf == 'iphone' and version_ge(gv, '6.4.0')) or (gf == 'android' and version_ge(gv, 640)):
        #    datas = {}
        #    datas['data'] = data
        #    datas['message'] = ''
        #    datas['data']['appApi'] = app_api
        #    for index, anchor in enumerate(datas['data']['anchors']):
        #        datas['data']['anchors'][index]['action'] = json.loads(anchor['action'])
        #    for index, tag in enumerate(datas['data']['tags']):
        #        datas['data']['tags'][index]['action'] = json.loads(tag['action'])
        #    datas['data']['share'] = json.loads(datas['data']['share'])
        #    return Response(json.dumps(datas),content_type = 'application/json')
        return '', data


@view_defaults(route_name='themes')
class ThemesView(View):

    def __init__(self, request):
        super(ThemesView, self).__init__()
        self.request = request

    @statsd.timer("hichao_backend.r_themes.get")
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        tag_id = self.request.params.get('tag_id', '')
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        self.topic_style = 0
        if (version_ge(gv, 632) and gf == 'android') or (version_ge(gv, '6.3.1') and gf == 'iphone'): self.topic_style = 1
        theme_list = {}
        if not flag:
            flag = datetime.datetime.now()
        else:
            flag = datetime.datetime.strptime(flag, "%Y-%m-%d %H:%M:%S")
        if not tag_id:
            theme_ids = get_latest_theme_ids(flag)
        else:
            theme_ids = get_theme_ids_by_tag_id(flag, tag_id)
        theme_list['items'] = []
        for theme_id in theme_ids:
            com = ''
            if self.topic_style:
                com = build_topic_list_item_by_theme_id(theme_id)
            else:
                com = build_theme_list_item_by_id(theme_id)
            if com:
                flag = com['component']['flag']
                del(com['component']['flag'])
                theme_list['items'].append(com)
        if len(theme_list['items']) >= FALL_PER_PAGE_NUM:
            theme_list['flag'] = flag
        return '', theme_list

