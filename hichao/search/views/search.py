# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.search.es import (
        search,
        stars,
        skus,
        forum,
        sg_tags,
        )
from hichao.base.views.view_base import View
from hichao.sku.models.sku import get_sku_by_id, get_old_sku_by_id
from hichao.base.config import (
        FALL_PER_PAGE_NUM,
        MYSQL_MAX_INT,
        CATEGORY_DICT,
        CHANNEL_DICT,
        )
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        )
from hichao.util.object_builder import (
        build_lite_thread_by_id,
        build_star_by_star_id,
        build_search_thread_by_thread_id,
        build_search_topic_by_topic_id,
        build_item_component_by_sku_id,
        build_brand_action_by_brand_id,
        )
from hichao.util.component_builder import build_component_drop,build_component_serach_hongren
from hichao.util.cps_util import check_cps_type
from hichao.util.short_url import generate_short_url
from hichao.util.sku_util import rebuild_sku
from hichao.app.views.oauth2 import check_permission
from hichao.util.statsd_client import timeit
from icehole_client.search_manage_client import SearchManageClient
from hichao.util.statsd_client import statsd
import time
from icehole_client.brand_client import BrandClient
from hichao.util.image_url  import build_category_and_brand_image_url
from hichao.app.views.oauth2 import check_permission
from hichao.collect.models.brand import brand_collect_user_has_item
from hichao.search.models.search import get_special_keywords

SUGGEST_TAG_COUNT = 10

@view_defaults(route_name = 'search')
class Search(View):
    def __init__(self, request):
        super(Search, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_search.get')
    @check_cps_type
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        query = self.request.params.get('query', '')
        _type = self.request.params.get('type', 'sku')
        crop = self.request.params.get('crop', '')
        crop = crop != '' and True or False
        more_items = self.request.params.get('more_items', '')
        gv = self.request.params.get('gv', '')
        #if gv: gv = gv_float(gv)
        gf = self.request.params.get('gf', '')
        self.lite_action = 0
        self.sku_v2 = 0
        self.support_webp = 0
        self.support_ec = 0
        if gf == 'iphone':
            if version_ge(gv, 5.2):
                self.lite_action = 1
            if version_ge(gv, 6.0):
                self.support_webp = 1
                self.support_ec = 1
                self.sku_v2 = 1
        elif gf == 'android':
            if version_ge(gv, 60):
                self.lite_action = 1
            if version_ge(gv, 100):
                self.support_ec = 1
                self.sku_v2 = 1
        elif gf == 'ipad':
            if version_ge(gv, 5.1):
                self.lite_action = 1
        data = {}
        data['items'] = []
        if _type == 'star':
            flag = (flag == '' and [0,] or [int(flag),])[0]
            ids = stars(query, flag, FALL_PER_PAGE_NUM)
            for id in ids[0:FALL_PER_PAGE_NUM - 1]:
                com = build_star_by_star_id(id, crop, self.lite_action)
                if com:
                    data['items'].append(com)
            if len(ids) == FALL_PER_PAGE_NUM:
                data['flag'] = str(flag + FALL_PER_PAGE_NUM)
        elif _type == 'sku':
            if self.sku_v2:
                flag = int(flag) if flag else 0
                sku_ids = search(query, flag, FALL_PER_PAGE_NUM, 'sku_v2')
                for sku_id in sku_ids:
                    com = build_item_component_by_sku_id(sku_id, more_items, self.lite_action, self.cps_type, self.support_webp, self.support_ec)
                    if com:
                        data['items'].append(com)
                client = SearchManageClient()
                key_word = client.get_special_word(query.encode('utf-8'))
                if key_word:
                    data['concerns'] = self.build_key_word(key_word)
                else:
                    tags = sg_tags(query, SUGGEST_TAG_COUNT)
                    data['tags'] = []
                    for tag in tags:
                        obj = {}
                        obj['text'] = tag['name']
                        obj['color'] = tag['background']
                        obj['picUrl'] = tag['img_url']
                        data['tags'].append(obj)
                if len(sku_ids) == FALL_PER_PAGE_NUM:
                    flag = str(flag + FALL_PER_PAGE_NUM)
                    data['flag'] = flag
            else:
                flag = (flag == '' and [0,] or [int(flag),])[0]
                _skus = skus(query, flag, FALL_PER_PAGE_NUM)
                for sku in _skus:
                    com = build_item_component_by_sku_id(sku['sku_id'], more_items, self.lite_action, cps_type = self.cps_type)
                    if com:
                        data['items'].append(com)
                if len(_skus) == FALL_PER_PAGE_NUM:
                    flag = str(flag + FALL_PER_PAGE_NUM)
                    data['flag'] = flag
        elif _type == 'thread':
            flag = int(flag) if flag else 0
            thread_ids = forum(query, flag, FALL_PER_PAGE_NUM, _type)
            for thread_id in thread_ids:
                thread_id = thread_id['id']
                com = build_lite_thread_by_id(thread_id)
                if com:
                    data['items'].append(com)
            if len(thread_ids) == FALL_PER_PAGE_NUM:
                data['flag'] = str(flag + FALL_PER_PAGE_NUM)
        return '', data

@view_defaults(route_name = 'query')
class QueryView(View):
    def __init__(self, request):
        super(QueryView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_query.get')
    @check_permission
    @check_cps_type
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        q = self.request.params.get('q', '').strip()
        if not q: return '', {}

        ifcrop = 0
        lite_action = 1
        more_items = 0
        support_webp = 0
        support_ec = 0

        tp = self.request.params.get('type', '')
        flag = self.request.params.get('flag', '')
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        if gf == 'iphone':
            if version_ge(gv, 6.0):
                support_webp = 1
                support_ec = 1
                if tp == 'sku':
                    tp = 'sku_v2'
        if gf == 'android':
            if version_ge(gv, 100):
                support_ec = 1
                if tp == 'sku':
                    tp = 'sku_v2'
        if gf == 'ipad':
            support_ec = 1

        flag = int(flag) if flag else 0
        data = {}
        if tp == 'thread': tp = 'forum'
        item_ids = search(q, flag, FALL_PER_PAGE_NUM, tp)
        if tp == 'forum':
            item_ids = item_ids['items']
        items = []

        for item in item_ids:
            _id = item
            _type = tp
            if tp == '' or tp == 'forum':
                _id = item['id']
                _type = item['type']
            com = {}
            if _type == 'star':
                com = build_star_by_star_id(_id, ifcrop, lite_action, support_webp)
            elif _type == 'sku' or _type == 'sku_v2':
                com = build_item_component_by_sku_id(_id, more_items, lite_action, self.cps_type, support_webp, support_ec)
            elif _type == 'topic':
                com = build_search_topic_by_topic_id(_id, support_webp, support_ec)
            elif _type == 'threads':
                com = build_search_thread_by_thread_id(_id, support_webp)
            elif _type == 'hongren':
                com = build_component_serach_hongren(item)
            if com:
                com['component']['action']['trackQuery'] = "query;;{0};;{1};;{2}".format(q, _type, _id)
                items.append(com)
        if items:
            data['items'] = items

        if len(item_ids) == FALL_PER_PAGE_NUM:
            data['flag'] = str(flag + FALL_PER_PAGE_NUM)
        if tp == 'hongren':
            return '', data 
        data_item = get_special_keywords(q, self.user_id)
        if data_item:
            if data_item.has_key('concerns'):
                data['concerns'] = data_item['concerns']
            if data_item.has_key('tags'):
                data['tags'] = data_item['tags']
        return '', data

    @check_permission
    def build_key_word(self, key_word):
        concerns = {}
        concerns['background'] = key_word.get_background_image()
        concerns['picUrl'] = key_word.get_image()
        concerns['follow'] = str(key_word.get_focus_count())
        concerns['text'] = key_word.get_name()
        concerns['description'] = key_word.get_description()
        concerns['id'] = str(key_word.get_tag_id())
        brand_id = key_word.get_brand_id()
        if brand_id > 0:
            res = brand_collect_user_has_item(int(self.user_id), int(brand_id))
        else:
            client = SearchManageClient()
            res = client.judge_user_follow_tag(int(self.user_id), int(key_word.get_tag_id()))
        if res: concerns['focused'] = '1'
        else: concerns['focused'] = '0'
        return concerns

