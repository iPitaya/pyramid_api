# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.topic.models.topic import (
        get_topic_ids,
        get_topic_detail_without_cache,
        )
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        version_gt,
        )
from hichao.base.config import (
        FALL_PER_PAGE_NUM,
        TOPIC_CATEGORY,
        INVISIBLE_TOPIC_CATEGORYS,
        )
from hichao.app.views.oauth2 import check_permission
from hichao.base.views.view_base import View
#from hichao.test.testTopic import get_test_topic_data, get_test_topic_component
from hichao.topic.models.topic import get_setting_more_apps, get_more_app_list
from hichao.topic.config import TOPIC_PV_PREFIX, TOPIC_UV_PREFIX
from hichao.util.object_builder import (
        build_topic_detail_by_id,
        build_topic_list_item_by_id,
        )
from hichao.base.lib.redis import redis
from hichao.util.statsd_client import statsd
from hichao.event.models.nv_shen.user_new import is_nv_shen_user
from hc.redis.count import Counter, SetCounter
import time

@view_defaults(route_name = 'topics')
class TopicsView(View):
    def __init__(self, request):
        super(TopicsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_topics.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        category = self.request.params.get('category', '')
        if category in INVISIBLE_TOPIC_CATEGORYS:
            query_type = category
        else:
            query_type = TOPIC_CATEGORY.CATEGORY_DICT.get(category, '')
        if flag == '':
            flag = time.time()
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        support_webp = 0
        support_pic = 0
        if (version_ge(gv, '6.0') and gf == 'iphone'):
            support_webp = 1
        if gf == 'iphone' and version_ge(gv, '6.6.0'):
            support_pic = 1
        elif gf == 'android' and version_ge(gv, '660'):
            support_pic = 1
        topic_ids = get_topic_ids(flag, FALL_PER_PAGE_NUM, query_type)
        topic_list = {}
        topic_list['items'] = []
        for id in topic_ids:
            component = build_topic_list_item_by_id(id, support_webp,support_pic)
            flag = component['component']['flag']
            del(component['component']['flag'])
            topic_list['items'].append(component)
        if len(topic_ids) >= FALL_PER_PAGE_NUM:
            topic_list['flag'] = flag
        # =============================测试====================================
        # data['items'].insert(0, get_test_topic_component())
        # =====================================================================
        return '', topic_list

@view_defaults(route_name = 'topic')
class TopicView(View):
    def __init__(self, request):
        super(TopicView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_topic.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        topic_id = self.request.params.get('topic_id', '')
        # =============================测试====================================
        # if topic_id == '5000':
        #     return '', get_test_topic_data()
        # =====================================================================
        width = self.request.params.get('width', '')
        if topic_id == '':
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        gi = self.request.params.get('gi', '')
        pv_key = TOPIC_PV_PREFIX.format(topic_id)
        uv_key = TOPIC_UV_PREFIX.format(topic_id)
        pv_counter = Counter(redis)
        uv_counter = SetCounter(redis, uv_key)
        pv_counter._incr(pv_key)
        uv_counter.add(gi)
        pv = pv_counter._byID(pv_key)
        if not pv: pv = 1
        if width == '':
            width = 320
        else:
            width = int(width)
        txt_with_margin = self.request.params.get('twm', '')
        if not txt_with_margin:
            txt_with_margin = 0
        else:
            txt_with_margin = 1
        user_id = self.user_id
        gv = self.request.params.get('gv', '')
        #if gv: gv = gv_float(gv)
        gf = self.request.params.get('gf', '')
        lite_thread = 0
        lite_action = 0
        support_webp = 0
        support_ec = 0
        if gf == 'iphone':
            if version_ge(gv, 5.0):
                lite_thread = 1
            if version_ge(gv, 5.2):
                lite_action = 1
            if version_ge(gv, 6.0):
                support_webp = 1
                support_ec = 1
            if version_ge(gv, '6.4.0'):
                #版本兼容专题单品模板 由于添加字段麻烦 和 帖子的共用一个  lite_thread = 1时是帖子的 2是新单品模板  
                lite_thread = 2
        if gf == 'android':
            if version_ge(gv, 50):
                lite_thread = 1
            if version_ge(gv, 60):
                lite_action = 1
            if version_ge(gv, 100):
                support_ec = 1
            if version_ge(gv, 640):
                lite_thread = 2
        if gf == 'ipad':
            if version_ge(gv, 4.0):
                lite_thread = 1
            if version_gt(gv, 5.0):
                lite_action = 1
            support_ec = 1
        data = build_topic_detail_by_id(topic_id, user_id, width, txt_with_margin, lite_thread, lite_action, support_webp, support_ec)
        #if data: data['v'] = str(pv)
        return '', data

@view_defaults(route_name = 'more_apps')
class MoreAppsView(View):
    def __init__(self, request):
        super(MoreAppsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_more_apps.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        platform = self.request.params.get('gf', 'iphone')
        type = self.request.params.get('type', 'form')
        items = []
        if type == 'form':
            items = get_setting_more_apps(platform)
        else:
            items = get_more_app_list(platform, type)
        data = {}
        data['items'] = items
        return '', data

@view_defaults(route_name = 'topic_detail_without_cache')
class TopicChecker(View):
    def __init__(self, request):
        super(TopicChecker, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_topic_detail_without_cache.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        topic_id = self.request.params.get('topic_id', '')
        width = int(self.request.params.get('width', '320'))
        if not id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        gv = self.request.params.get('gv', '')
        #if gv: gv = gv_float(gv)
        gf = self.request.params.get('gf', '')
        lite_action = 0
        support_ec = 0
        if gf == 'iphone':
            if version_ge(gv, 5.0):
                lite_action = 1
            if version_ge(gv, 6.0):
                support_ec = 1
        if gf == 'android' and version_ge(gv, 50):
            if version_ge(gv, 50):
                lite_action = 1
            if version_ge(gv, 100):
                support_ec = 1
        data = get_topic_detail_without_cache(topic_id, width, lite_action, support_ec)
        return '', data


