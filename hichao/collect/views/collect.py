# -*- coding: utf-8 -*-
from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from hichao.base.views.view_base import View, require_type
from hichao.base.config import (
        COLLECTION_TYPE,
        )
from hichao.app.views.oauth2 import check_permission
from hichao.collect.models.collect import Collect
from hichao.star.models.star import get_star_by_star_id
from hichao.sku.models.sku import (
        get_old_sku_by_id,
        get_sku_id_by_source_sourceid,
        )
from hichao.topic.models.topic import get_topic_by_id
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        version_eq,
        )
from hichao.util.component_builder import (
        build_component_star,
        build_component_item,
        )
from hichao.util.object_builder import (
        build_star_by_star_id,
        build_topic_list_item_by_id,
        build_topic_as_drop_by_topic_id,
        build_thread_by_id,
        build_lite_thread_by_id,
        build_item_component_by_sku_id,
        build_news_list_item_by_id,
        build_theme_list_item_by_id,
        build_brand_collect_list_item_by_id,
        CpsType,
        build_lite_post_by_id,
        )
from hichao.collect.models.star import (
        star_collect_new,
        star_collect_rm,
        star_collect_count,
        star_count_by_user_id,
        star_collect_user_has_item,
        star_collect_list_by_user_id,
)
from hichao.collect.models.sku import (
        sku_collect_new,
        sku_collect_rm,
        sku_collect_count,
        sku_count_by_user_id,
        sku_collect_list_by_user_id,
        sku_collect_user_has_item,
)
from hichao.collect.models.topic import (
        topic_collect_new,
        topic_collect_rm,
        topic_collect_list_by_user_id,
        topic_count_by_user_id,
        )
from hichao.collect.models.thread import (
        thread_collect_new,
        thread_collect_rm,
        thread_collect_list_by_user_id,
        thread_count_by_user_id,
        thread_user_has_item,
        )
from hichao.collect.models.news import (
        news_collect_new,
        news_collect_rm,
        news_collect_list_by_user_id,
        news_count_by_user_id,
        news_collect_user_has_item,
        )
from hichao.collect.models.theme import (
        theme_collect_new,
        theme_collect_rm,
        theme_count_by_user_id,
        theme_collect_user_has_item,
        unpack_topic_id_to_theme_id,
        )
from hichao.collect.models.brand import (
        brand_collect_new,
        brand_collect_rm,
        brand_collect_list_by_user_id,
        brand_count_by_user_id,
        brand_collect_user_has_item,
        )
from hichao.forum.models.thread import get_thread_by_id
from hichao.patch.collect_patch import patch_ios_collect_v_3_3
from hichao.feed.models.feed import NewsFeed
from hichao.feed import ACTIVITY_STATUS
from hichao.util.sku_util import rebuild_sku
from hichao.util.statsd_client import statsd
import json

star_collection = Collect('star')
sku_collection = Collect('sku')
mix_collection = NewsFeed

FALL_PER_PAGE_NUM = 22


@view_defaults(route_name='collections')
class CollectView(View):
    def __init__(self, request):
        super(CollectView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_collections.get')
    @check_permission
    @require_type
    @view_config(request_method='GET', renderer = 'json')
    @patch_ios_collect_v_3_3
    @pack_data
    def get(self):
        items = []
        ids = []
        user_id = self.request.params.get('user_id', '')
        user_id = user_id != '' and int(user_id) or -1
        user_id = user_id == -1 and self.user_id or user_id
        if user_id == -2:
            self.error['error'] = 'User info expired.'
            self.error['errorCode'] = '20002'
            return '', {}
        if user_id == -1:
            ids = self.request.params.get('ids', '')
            if not ids:
                self.error['error'] = 'Arguments error.'
                self.error['errorCode'] = '10001'
                return '', {}
            ids = ids.split(',')
        flag = self.request.params.get('flag', '')
        flag = flag != '' and int(flag) or 0
        crop = self.request.params.get('crop', '')
        crop = 1 if crop else 0
        more_img = self.request.params.get('more_pic', '')
        more_items = self.request.params.get('more_items', '')
        cps_type = CpsType.IPHONE
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        #gv = float(gv) if gv else 0
        if gf == 'ipad':
            cps_type = CpsType.IPAD
        lite_thread = self.request.params.get('lite_thread', '')
        lite_action = 0
        support_webp = 0
        support_ec = 0
        support_xiajia = 0 
        support_theme = 0
        post_thread = 0
        if gf == 'iphone':
            if version_ge(gv, '5.2'):
                lite_action = 1
                lite_thread = 1
            if version_ge(gv, '6.0'):
                support_webp = 1
                support_ec = 1
            if version_ge(gv, '6.2.0'):
                support_theme = 1
            if version_ge(gv, '6.4.0'):
                post_thread = 1
        elif gf == 'android':
            if version_ge(gv, 60):
                lite_action = 1
                lite_thread = 1
            if version_ge(gv, 100):
                support_ec = 1
            if version_ge(gv, 120):
                support_theme = 1
            if version_ge(gv, 640):
                post_thread = 1
        elif gf == 'ipad':
            if version_ge(gv, '5.1'):
                lite_action = 1
                lite_thread = 1
            support_ec = 1
        if self.type == COLLECTION_TYPE.STAR:
            if not ids:
                ids = star_collect_list_by_user_id(user_id, flag, FALL_PER_PAGE_NUM)
            for id in ids:
                obj = build_star_by_star_id(id, crop, lite_action, support_webp)
                if obj:
                    items.append(obj)
        elif self.type == COLLECTION_TYPE.SKU:
            if not ids:
                ids = sku_collect_list_by_user_id(user_id, flag, FALL_PER_PAGE_NUM)
            ############### ios 3.5，前端少传了more_items参数 ################
            if version_eq(gv, '3.5') and gf == 'iphone':
                more_items = '1'
            #============== ios 3.5，前端少传了more_items参数 ===============#
            for id in ids:
                obj = build_item_component_by_sku_id(id, more_items, lite_action, cps_type, support_webp, support_ec, support_xiajia)
                if obj:
                    items.append(obj)
        elif self.type == COLLECTION_TYPE.TOPIC:
            if not ids:
                ids = topic_collect_list_by_user_id(user_id, flag, FALL_PER_PAGE_NUM)
            for id in ids:
                obj = {}
                if id.isdigit():
                    obj = build_topic_as_drop_by_topic_id(id, support_webp)
                elif support_theme:
                    id = unpack_topic_id_to_theme_id(id)
                    obj = build_theme_list_item_by_id(id)
                if obj:
                    items.append(obj)
        elif self.type == COLLECTION_TYPE.THREAD:
            ids = thread_collect_list_by_user_id(user_id, flag, FALL_PER_PAGE_NUM)
            for id in ids:
                if lite_thread:
                    with_top_icon = 0
                    without_icon = 0
                    if post_thread:
                        obj = build_lite_post_by_id(id, self.user_id)
                    else:
                        obj = build_lite_thread_by_id(id, with_top_icon, without_icon, support_webp)
                else:
                    obj = build_thread_by_id(id, crop, more_img, support_webp)
                if obj:
                    items.append(obj)
        elif self.type == COLLECTION_TYPE.NEWS:
            if not ids:
                ids = news_collect_list_by_user_id(user_id, flag, FALL_PER_PAGE_NUM)
            for id in ids:
                obj = build_news_list_item_by_id(id)
                if obj:
                    items.append(obj)
        elif self.type == COLLECTION_TYPE.BRAND:
            if not ids:
                ids = brand_collect_list_by_user_id(user_id, flag, FALL_PER_PAGE_NUM)
            for id in ids:
                obj = build_brand_collect_list_item_by_id(id)
                if obj:
                    items.append(obj)
        elif self.type == COLLECTION_TYPE.ALL:
            # 混合列表里没有加明星资讯和品牌收藏的相关逻辑。
            ids = mix_collection.activity_list(user_id, flag, FALL_PER_PAGE_NUM)
            for id in ids:
                user, code, id = id.split(':')
                if code == ACTIVITY_STATUS.STAR_COLLECT.CODE:
                    obj = build_star_by_star_id(id, crop, lite_action, support_webp)
                elif code == ACTIVITY_STATUS.SKU_COLLECT.CODE:
                    obj = build_item_component_by_sku_id(id, more_items, lite_action, cps_type, support_webp, support_ec, support_xiajia)
                elif code == ACTIVITY_STATUS.TOPIC_COLLECT.CODE:
                    obj = build_topic_as_drop_by_topic_id(id, support_webp)
                elif code == ACTIVITY_STATUS.THREAD_COLLECT.CODE:
                    if lite_thread:
                        with_top_icon = 0
                        without_icon = 0
                        obj = build_lite_thread_by_id(id, with_top_icon, without_icon, support_webp)
                    else:
                        obj = build_thread_by_id(id, crop, more_img, support_webp)
                if obj:
                    items.append(obj)
        data = {}
        data['items'] = items
        star_total = star_count_by_user_id(user_id)
        sku_total = sku_count_by_user_id(user_id)
        topic_total = topic_count_by_user_id(user_id)
        thread_total = thread_count_by_user_id(user_id)
        news_total = news_count_by_user_id(user_id)
        brand_total = brand_count_by_user_id(user_id)
        data['starTotal'] = str(star_total)
        data['skuTotal'] = str(sku_total)
        data['topicTotal'] = str(topic_total)
        data['collectThreadTotal'] = str(thread_total)
        data['newsTotal'] = str(news_total)
        data['brandTotal'] = str(brand_total)
        len_ids = len(ids)
        if user_id != -1 and len_ids >= FALL_PER_PAGE_NUM:
            flag = flag + len_ids
            data['flag'] = str(flag)
        return '', data

    @statsd.timer('hichao_backend.r_collections.post')
    @check_permission
    @require_type
    @view_config(request_method='POST', renderer = 'json')
    @pack_data
    def post(self):
        if self.user_id < 1:
            self.error['error'] = 'User info error.'
            self.error['errorCode'] = '20002'
            return '', {}
        item_list = self.request.params.get('ids', '')
        item_ids = [id for id in item_list.split(',') if id.isdigit() and int(id) > 0]
        state = 1
        source = ''
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        source = self.request.params.get('source', '')
        type_flag = self.request.params.get('type', '')
        source_id = self.request.params.get('source_id', '')
        print self.user_id,'#',gf,'#',gv,'#',item_list,'#',source,'#',source_id,'#',type_flag,'#$$$$$'
        if self.type == COLLECTION_TYPE.STAR and item_ids:
            state = star_collect_new(self.user_id, item_ids)
        elif self.type == COLLECTION_TYPE.SKU:
            source_id = self.request.params.get('source_id', '')
            #if not source_id:
            #    self.error['error'] = 'Arguments missing'
            #    self.error['errorCode'] = '10002'
            #    return '', {}
            if source_id:
                source = 'ecshop'
                sku_id = get_sku_id_by_source_sourceid(source, source_id)
                if not sku_id:
                    self.error['error'] = 'Operation failed.'
                    self.error['errorCode'] = '30001'
                    return '', {}
                item_ids = [sku_id]
            if item_ids:
                state = sku_collect_new(self.user_id, item_ids)
            else:
                self.error['error'] = 'Arguments missing'
                self.error['errorCode'] = '10002'
                return '',{}
        elif self.type == COLLECTION_TYPE.TOPIC and item_ids:
            state = topic_collect_new(self.user_id, item_ids)
        elif self.type == COLLECTION_TYPE.THREAD and item_ids:
            state = thread_collect_new(self.user_id, item_ids)
        elif self.type == COLLECTION_TYPE.NEWS and item_ids:
            state = news_collect_new(self.user_id, item_ids)
        elif self.type == COLLECTION_TYPE.THEME and item_ids:
            state = theme_collect_new(self.user_id, item_ids)
        elif self.type == COLLECTION_TYPE.BRAND and item_ids:
            state = brand_collect_new(self.user_id, item_ids)
        else:
            if not item_ids:
                self.error['error'] = 'Arguments missing'
                self.error['errorCode'] = '10002'
                return '',{}
            else:
                self.error['error'] = 'TypeError.'
                self.error['errorCode'] = '10002'
                return '', {}
        if state == 0:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return '', {}
        else:
            if source:
                return '', {'result':'1'}
            return '', {'ids':item_list, 'type':self.type}

    @statsd.timer('hichao_backend.r_collections.delete')
    @check_permission
    @require_type
    @view_config(request_method='DELETE', renderer = 'json')
    @pack_data
    def delete(self):
        if self.type == COLLECTION_TYPE.MIX: return self.delete_mix_items()
        else: return self.delete_single_item()

    def delete_single_item(self):
        item_id = self.request.params.get('id', '')
        source = ''
        if self.type == COLLECTION_TYPE.SKU:
            source = self.request.params.get('source', '')
            if source:
                source_id = self.request.params.get('source_id', '')
                if not source_id:
                    self.error['error'] = 'Arguments missing'
                    self.error['errorCode'] = '10002'
                    return '', {}
                item_id = get_sku_id_by_source_sourceid(source, source_id)
                if not item_id:
                    self.error['error'] = 'Operation failed'
                    self.error['errorCode'] = '30001'
                    return '', {}
        state = self.delete_item(item_id, self.type)
        if state == 0:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return '', {}
        else:
            if source:
                return '', {'result':'1'}
            return '', {'id':item_id, 'type':self.type}

    def delete_mix_items(self):
        deletions = self.request.params.get('deletions', '')
        if not deletions:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        deletions = json.loads(deletions)
        data = {}
        for key in deletions.keys():
            data[key] = []
            ids = deletions[key].split(',')
            for item_id in ids:
                state = self.delete_item(item_id, key)
                if state:
                    data[key].append(item_id)
        for key in data.keys():
            if data[key]: data[key] = ','.join(data[key])
        return '', data

    def delete_item(self, item_id, _type):
        state = 1
        if _type == COLLECTION_TYPE.STAR:
            state = star_collect_rm(self.user_id, item_id)
        elif _type == COLLECTION_TYPE.SKU:
            state = sku_collect_rm(self.user_id, item_id)
        elif _type == COLLECTION_TYPE.TOPIC:
            topic = get_topic_by_id(item_id)
            category_id = topic.get_category_id()
            state = topic_collect_rm(self.user_id, topic.get_category_id(), item_id)
        elif _type == COLLECTION_TYPE.THREAD:
            collected = thread_user_has_item(self.user_id, item_id)
            if not collected or int(collected) <= 0: return state
            thread = get_thread_by_id(item_id)
            state = thread_collect_rm(self.user_id, thread.category_id, item_id)
        elif _type == COLLECTION_TYPE.THEME:
            state = theme_collect_rm(self.user_id, item_id)
        elif _type == COLLECTION_TYPE.NEWS:
            state = news_collect_rm(self.user_id, item_id)
        elif _type == COLLECTION_TYPE.BRAND:
            state = brand_collect_rm(self.user_id, item_id)
        return state

@view_defaults(route_name='collection_ids')
class CollectIdsView(View):
    def __init__(self, request):
        super(CollectIdsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_collection_ids.get')
    @check_permission
    @require_type
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        if self.user_id < 1:
            return '', {}
        _type = self.type
        star_ids = ''
        sku_ids = ''
        data = {}
        if _type == COLLECTION_TYPE.ALL:
            stars = star_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            skus = sku_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            topics = topic_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            threads = thread_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            news = news_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            brands = brand_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            topic_ids = [id for id in topics if id.isdigit()]
            topic_ids = ','.join(map(str, topic_ids))
            star_ids = ','.join(map(str, stars))
            sku_ids = ','.join(map(str, skus))
            thread_ids = ','.join(map(str, threads))
            news_ids = ','.join(map(str, news))
            theme_ids = [unpack_topic_id_to_theme_id(id) for id in topics if not id.isdigit()]
            theme_ids = ','.join(map(str, theme_ids))
            brand_ids = ','.join(map(str, brands))
            data['starIds'] = star_ids
            data['skuIds'] = sku_ids
            data['topicIds'] = topic_ids
            data['subjectIds'] = thread_ids
            data['newsIds'] = news_ids
            data['themeIds'] = theme_ids
            data['brandIds'] = brand_ids
        elif _type == COLLECTION_TYPE.STAR:
            stars = star_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            star_ids = ','.join(map(str, stars))
            data['starIds'] = star_ids
        elif _type == COLLECTION_TYPE.SKU:
            skus = sku_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            sku_ids = ','.join(map(str, skus))
            data['skuIds'] = sku_ids
        elif _type == COLLECTION_TYPE.TOPIC:
            topics = topic_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            topics = [id for id in topics if id.isdigit()]
            topic_ids = ','.join(map(str, topics))
            data['topicIds'] = topic_ids
        elif _type == COLLECTION_TYPE.THREAD:
            threads = thread_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            thread_ids = ','.join(map(str, threads))
            data['subjectIds'] = thread_ids
        elif _type == COLLECTION_TYPE.NEWS:
            news = news_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            news_ids = ','.join(map(str, news))
            data['newsIds'] = news_ids
        elif _type == COLLECTION_TYPE.THEME:
            themes = topic_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            themes = [unpack_topic_id_to_theme_id(id) for id in themes if not id.isdigit()]
            theme_ids = ','.join(map(str, themes))
            data['themeIds'] = theme_ids
        elif _type == COLLECTION_TYPE.BRAND:
            brands = brand_collect_list_by_user_id(self.user_id, offset = 0, limit = -1)
            brand_ids = ','.join(map(str, brands))
            data['brandIds'] = brand_ids
        star_total = star_count_by_user_id(self.user_id)
        sku_total = sku_count_by_user_id(self.user_id)
        topic_total = topic_count_by_user_id(self.user_id)
        thread_total = thread_count_by_user_id(self.user_id)
        news_total = news_count_by_user_id(self.user_id)
        brand_total = brand_count_by_user_id(self.user_id)
        data['starTotal'] = str(star_total)
        data['skuTotal'] = str(sku_total)
        data['topicTotal'] = str(topic_total)
        data['subjectTotal'] = str(thread_total)
        data['newsTotal'] = str(news_total)
        data['brandTotal'] = str(brand_total)
        return '', data

#网站使用的收藏的类型的接口
@view_defaults(route_name='collection_ids_web')
class CollectIdsWebView(View):
    def __init__(self, request):
        super(CollectIdsWebView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_collection_ids_web.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        user_id = self.request.params.get('user_id', '')
        if user_id < 1:
            return '', {}
        col_type = self.request.params.get('type', '')
        flag = self.request.params.get('offset', '0')
        limit = self.request.params.get('limit', '18')
        flag= int(flag)
        limit = int(limit)
        if col_type == 'thread':
            col_type = 'subject'
        data = {}
        if col_type == COLLECTION_TYPE.STAR:
            stars = star_collect_list_by_user_id(user_id, offset = flag, limit = limit)
            star_ids = ','.join(map(str, stars))
            data['ids'] = star_ids
            data['total'] = str(star_count_by_user_id(user_id))
        elif col_type == COLLECTION_TYPE.SKU:
            skus = sku_collect_list_by_user_id(user_id, offset = flag, limit = limit)
            sku_ids = ','.join(map(str, skus))
            data['ids'] = sku_ids
            data['total'] = str(sku_count_by_user_id(user_id))
        if col_type == COLLECTION_TYPE.TOPIC:
            topics = topic_collect_list_by_user_id(user_id, offset = flag, limit = limit)
            print topics
            topics = [id for id in topics if id.isdigit()]
            topic_ids = ','.join(map(str, topics))
            data['ids'] = topic_ids
            data['total'] = str(topic_count_by_user_id(user_id))
        elif col_type == COLLECTION_TYPE.THREAD:
            threads = thread_collect_list_by_user_id(user_id, offset = flag, limit = limit)
            thread_ids = ','.join(map(str, threads))
            data['ids'] = thread_ids
            data['total'] = str(thread_count_by_user_id(user_id))
        elif col_type == COLLECTION_TYPE.NEWS:
            news = news_collect_list_by_user_id(user_id, offset = flag, limit = limit)
            news_ids = ','.join(map(str, news))
            data['ids'] = news_ids
            data['total'] = str(news_count_by_user_id(user_id))
        elif col_type == COLLECTION_TYPE.THEME:
            themes = topic_collect_list_by_user_id(user_id, offset = flag, limit = limit)
            print themes 
            themes = [unpack_topic_id_to_theme_id(id) for id in themes if not id.isdigit()]
            theme_ids = ','.join(map(str, themes))
            data['ids'] = theme_ids
            data['total'] = str(thread_count_by_user_id(user_id))
        elif col_type == COLLECTION_TYPE.BRAND:
            brands = brand_collect_list_by_user_id(user_id, offset = flag, limit = limit)
            brand_ids = ','.join(map(str, brands))
            data['ids'] = brand_ids
            data['total'] = str(brand_count_by_user_id(user_id))
        return '', data

@view_defaults(route_name = 'collection_merger')
class CollectMergerView(View):
    def __init__(self, request):
        super(CollectMergerView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_collection_merger.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        data = self.request.params.get('data', '')
        if not self.user_id or self.user_id < 1:
            self.error['error'] = 'User is illegal.'
            self.error['errorCode'] = '20001'
            return '', {}
        if not data:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        data = json.loads(data)
        for tp, dt in data.items():
            collector = Collect(tp)
            li = []
            for id,ts in dt.items():
                li.append((id, ts))
            collector.new_by_time(self.user_id, li)
        return '', {}

