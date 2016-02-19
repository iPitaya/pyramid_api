# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.topic.models.topic import get_news_ids
from hichao.util.statsd_client import statsd
from hichao.util.pack_data import pack_data
from hichao.base.config import FALL_PER_PAGE_NUM
from hichao.util.object_builder import build_news_list_item_by_id
from hichao.news.models.news_star  import build_newsStar_list
import functools
import time

#get_news_ids = functools.partial(get_topic_ids, category = u'明星资讯')

@view_defaults(route_name = 'news_list')
class NewsListView(View):
    def __init__(self, request):
        super(NewsListView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_news_list.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        tp = self.request.params.get('type', '')
        if not tp: tp = 'news'
        if tp == 'news':
            return self.get_news_list()
        else:
            return self.get_star_list()

    def get_news_list(self):
        flag = self.request.params.get('flag', '')
        if not flag:
            flag = time.time()
        news_ids = get_news_ids(flag, FALL_PER_PAGE_NUM, u'明星资讯')
        data = {}
        data['items'] = []
        for news_id in news_ids:
            com = build_news_list_item_by_id(news_id)
            flag = com['component']['flag']
            del(com['component']['flag'])
            if com:
                data['items'].append(com)
        if len(news_ids) >= FALL_PER_PAGE_NUM:
            data['flag'] = flag 
        return '', data

    def get_star_list(self):
        data = {}
        data['list'] = build_newsStar_list()
        return '',data


