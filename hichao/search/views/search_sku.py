# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.config import FALL_PER_PAGE_NUM, MYSQL_MAX_INT
from hichao.base.views.view_base import View
from hichao.util.object_builder import (
        build_item_component_by_sku_id,
        )
from hichao.util.cps_util import check_cps_type
from hichao.cache.cache import deco_cache
from hichao.util.statsd_client import statsd
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        )
from hichao.search.new_search import search_skus
from hichao.base.config import FALL_PER_PAGE_NUM
from hichao.app.views.oauth2 import check_permission
from icehole_client.search_manage_client import SearchManageClient
from hichao.util.image_url  import build_category_and_brand_image_url,build_evaluation_image_url
from hichao.collect.models.brand import brand_collect_user_has_item
from hichao.search.es import sg_tags
from hichao.search.models.search import (
        get_item_component_data,
        get_item_component_data_lite,
        build_key_word,
        get_special_keywords,
        )
from hichao.app.views.oauth2 import check_permission
from hichao.util.component_builder import build_component_search_sku_lite
import time


SUGGEST_TAG_COUNT = 10

@view_defaults(route_name = 'search_sku')
class SearchSkuView(View):
    def __init__(self, request):
        super(SearchSkuView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_search_sku.get')
    @check_cps_type
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        if not flag:
            flag = 0
        flag = int(flag)
        sort = self.request.params.get('sort', 'all')
        asc_desc = self.request.params.get('asc', '1')
        cat = self.request.params.get('cat', 'all')
        query = self.request.params.get('query', '')
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        if not query:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        if sort == 'sale':
            sort = 'sales'
        if sort == 'price':
            sort = 'promotion_price'
        if sort == 'new':
            sort = 'on_sale_time'
        if str(asc_desc) == '1':
            asc_desc = 'asc'
        else:
            asc_desc = 'desc'
        result = search_skus(query,0,flag,FALL_PER_PAGE_NUM,sort,asc_desc, cat,include_source = True)
        lite_action = 1
        ecshop_action = 1
        support_webp = 1
        support_ec = 1
        support_xiajia = 1
        support_search_only = 0
        if (gf == 'iphone' and version_ge(gv,'6.3.4')) or (gf == 'android' and version_ge(gv,634)):
            support_search_only = 1
        data = {}
        has_color=False
        if isinstance(result, dict):
            sku_items = result['items']
            has_color = result['has_color']
        else:
            sku_items = result
        sku_num = len(sku_items)
        data['items'] = []
        for sku_item in sku_items:
                com = get_item_component_data(sku_item['sku_id'], lite_action,self.cps_type,support_webp,support_ec,support_xiajia, has_color, sku_item = sku_item)
                #if support_search_only == 0:
                #    com = get_item_component_data(sku_item['sku_id'], lite_action,self.cps_type,support_webp,support_ec,support_xiajia, has_color, sku_item = sku_item)
                #else:
                #    sku_item['has_color'] = has_color
                #    com = get_item_component_data_lite(sku_item['sku_id'], has_color, sku_item = sku_item)
                if com:
                    #com['component']['sales'] = str(sku_item['sales'])
                    #com['component']['price'] = str(sku_item['current_price'])
                    data['items'].append(com)
        data_item = get_special_keywords(query, self.user_id)
        if data_item:
            if data_item.has_key('concerns'):
                data['concerns'] = data_item['concerns']
            if data_item.has_key('tags'):
                data['tags'] = data_item['tags']

        if sku_num >= FALL_PER_PAGE_NUM:
            data['flag']  = str(flag + FALL_PER_PAGE_NUM )
        return '', data
        

@view_defaults(route_name = 'search_thread_sku')
class SearchThreadSkuView(View):
    def __init__(self, request):
        super(SearchThreadSkuView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_search_thread_sku.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        if not flag:
            flag = 0
        flag = int(flag)
        sort = self.request.params.get('sort', 'all')
        asc_desc = self.request.params.get('asc', '1')
        cat = self.request.params.get('cat', 'all')
        query = self.request.params.get('query', '')
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        if not query:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        if sort == 'sale':
            sort = 'sales'
        if sort == 'price':
            sort = 'promotion_price'
        if sort == 'new':
            sort = 'on_sale_time'
        if str(asc_desc) == '1':
            asc_desc = 'asc'
        else:
            asc_desc = 'desc'
        result = search_skus(query,0,flag,FALL_PER_PAGE_NUM,sort,asc_desc, cat,include_source = True)
        has_color=False
        if isinstance(result, dict):
            sku_items = result['items']
            has_color = result['has_color']
        else:
            sku_items = result
        sku_num = len(sku_items)
        data = {}
        data['items'] = []
        for sku_item in sku_items:
            item = {}
            item['picUrl'] = sku_item['url']
            if has_color:
                item['picUrl'] = sku_item['color_url']
            item['picUrl'] = build_evaluation_image_url(item['picUrl'],'backend_images', size = 100)
            item['title'] = sku_item['title']
            item['price'] = str(sku_item['current_price'])
            item['brandName'] = sku_item['brand']
            item['source_id'] = str(sku_item['item_id'])
            item['source'] = 'ecshop'
            item['sku_id'] = str(sku_item['sku_id'])
            data['items'].append(item)
        if sku_num >= FALL_PER_PAGE_NUM:
            data['flag']  = str(flag + FALL_PER_PAGE_NUM )
        return '', data

