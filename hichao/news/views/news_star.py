# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.topic.models.topic import get_news_ids
from hichao.util.statsd_client import statsd
from hichao.util.pack_data import pack_data,version_ge
from hichao.base.config import FALL_PER_PAGE_NUM
from hichao.util.object_builder import build_news_list_item_by_id
from hichao.news.models.news_star  import (
        build_newsStar_list,
        get_starspace_news_list,
        get_starspace_star_list,
        )
import functools
import time
from hichao.util.object_builder import build_topic_detail_by_id 
from hichao.app.views.oauth2 import check_permission


@view_defaults(route_name = 'news_star')
class NewsStarView(View):
    def __init__(self, request):
        super(NewsStarView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_news_star.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        tp = self.request.params.get('type', '')
        topic_id = self.request.params.get('id', '')
        if not topic_id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        if not tp: tp = 'news'
        if tp == 'news':
            return self.get_news_detail(topic_id)
        else:
            return self.get_star_detail(topic_id)

    def get_news_detail(self,topic_id):
        width = self.request.params.get('width', '')
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        lite_thread = 1 
        if gf == 'iphone':
            if version_ge(gv, '6.4.0'):
            #版本兼容专题单品模板 由于添加字段麻烦 和 帖子的共用一个  lite_thread = 1时是帖子的 2是新单品模板  
                lite_thread = 2
        if gf == 'android':
            if version_ge(gv, 640):
                lite_thread = 2
        if width == '':
            width = 320
        else:
            width = int(width)
        txt_with_margin = self.request.params.get('twm', '')
        if not txt_with_margin:
            txt_with_margin = 0
        else:
            txt_with_margin = 1
        data = {}
        data = build_topic_detail_by_id(topic_id, self.user_id, width, txt_with_margin, lite_thread, 1, 1, 1)
        return '',data

    def get_star_detail(self,topic_id):
        tag = self.request.params.get('tag', 'star')
        flag = self.request.params.get('flag', '')
        data = {}
        if tag == 'star':
            data = get_starspace_star_list(topic_id, flag, tag)
        else:
            data = get_starspace_news_list(topic_id, flag)
        return '', data


