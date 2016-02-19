# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.util.pack_data import pack_data
from hichao.base.config import (
        FALL_PER_PAGE_NUM,
        TOPIC_CATEGORY,
        INVISIBLE_TOPIC_CATEGORYS,
        ) 
from hichao.topic.models.topic import get_topic_ids
from hichao.base.views.view_base import View
from hichao.util.statsd_client import statsd
from hichao.timeline.models.mix_topic import get_mix_topic_units
from hichao.util.object_builder import (
        build_topic_list_item_by_id,
        build_topic_list_item_by_theme_id,
        )
from hichao.util.pack_data import version_ge
import time

@view_defaults(route_name = 'mix_topics')
class MixTopicsView(View):
    def __init__(self, request):
        super(MixTopicsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mix_topics.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        if self.request.params.get('category', ''):
            return self.get_category_topics()
        flag = self.request.params.get('flag', '')
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        support_pic = 0  #这个参数确定6.6.0以后给专题的图片提供宽高
        if gf == 'iphone' and version_ge(gv, '6.6.0'):
            support_pic = 1
        elif gf == 'android' and version_ge(gv, '660'):
            support_pic = 1
        units = get_mix_topic_units(flag, FALL_PER_PAGE_NUM)
        flag = ''
        data = {}
        data['items'] = []
        support_webp = 1
        for unit in units:
            if unit.get_component_type() == 'topic':
                com = build_topic_list_item_by_id(unit.get_component_type_id(), support_webp, support_pic)
            else:
                com = build_topic_list_item_by_theme_id(unit.get_component_type_id(), support_pic)
            if com:
                flag = unit.get_component_flag()
                del(com['component']['flag'])
                data['items'].append(com)
        if len(units) == FALL_PER_PAGE_NUM:
            data['flag'] = str(flag)
        return '', data

    def get_category_topics(self):
        flag = self.request.params.get('flag', '')
        category = self.request.params.get('category', '')
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        support_pic = 0  #这个参数确定6.6.0以后给专题的图片提供宽高
        if gf == 'iphone' and version_ge(gv, '6.4.0'):
            support_pic = 1
        elif gf == 'android' and version_ge(gv, '640'):
            support_pic = 1
        query_type = category if category in INVISIBLE_TOPIC_CATEGORYS else TOPIC_CATEGORY.CATEGORY_DICT.get(category, '')
        flag = flag if flag else time.time()
        support_webp = 1
        topic_ids = get_topic_ids(flag, FALL_PER_PAGE_NUM, query_type)
        topic_list = {}
        topic_list['items'] = []
        for id in topic_ids:
            com = build_topic_list_item_by_id(id, support_webp, support_pic)
            if com:
                flag = com['component']['flag']
                del(com['component']['flag'])
                topic_list['items'].append(com)
        if len(topic_ids) >= FALL_PER_PAGE_NUM:
            topic_list['flag'] = str(flag)
        return '', topic_list

