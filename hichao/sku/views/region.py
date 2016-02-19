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
        version_eq,
        )
from hichao.search.new_search import search_skus,search_zone
from hichao.base.config import FALL_PER_PAGE_NUM
from hichao.sku.models.recommend_sku import get_recommend_sku_list
from icehole_client.promotion_client import PromotionClient
from hichao.keywords.models.classes import get_category_by_title

@view_defaults(route_name = 'region_skus')
class RegionSkusView(View):
    def __init__(self, request):
        super(RegionSkusView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_skus.get')
    @check_cps_type
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        flag = int(flag) if flag else 0
        region_id = self.request.params.get('id', '')
        sort = self.request.params.get('sort', '')
        sort = sort if sort else 'all'
        asc_desc = self.request.params.get('asc', '')
        asc_desc = asc_desc if asc_desc else '1'
        cat = self.request.params.get('cat', '')
        if cat == '全部':
            cat = 'all'
        query = self.request.params.get('query', '')
        if region_id:
            pc_item = PromotionClient().get_content_by_id(int(region_id))
            if pc_item:
                query = pc_item.title
        query = query.replace('专区','')
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        if not query:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        if not region_id:
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
        if gf == 'iphone' and version_eq(gv, '6.3.4'):
            if cat != 'all':
                cat = get_category_by_title(cat)
                cat = cat.query_title
        support_recommend_sku = 0  #专区默认:后台推荐
        if (gf == 'iphone' and version_ge(gv, '6.3.4')) or (gf == 'android' and version_ge(gv, 634)):
            if sort == 'all' and cat == 'all':   #分类搜索走的同一接口
                support_recommend_sku = 1
        if (gf == 'iphone' and version_ge(gv, '6.4.0')) or (gf == 'android' and version_ge(gv, 640)):
            if cat == '' or cat == 'all':
                support_recommend_sku = 1
        if support_recommend_sku:
            result = get_recommend_sku_list(region_id, flag, FALL_PER_PAGE_NUM)
        else:
            result = search_zone(query,0,flag,FALL_PER_PAGE_NUM,sort,asc_desc,cat,include_source = True)
        lite_action = 1
        ecshop_action = 1
        support_webp = 1
        support_ec = 1
        support_xiajia = 1
        data = {}
        if not result:
            return '', data
        if isinstance(result, dict):
            sku_items = result['items']
        else:
            sku_items = result
        sku_num = len(sku_items)
        data['items'] = []
        for sku_item in sku_items:
            sku_id = sku_item['sku_id']
            com = build_item_component_by_sku_id(sku_id,0,lite_action,self.cps_type,support_webp,support_ec,support_xiajia)
            if com: 
                if sku_item.has_key('sales'):
                    com['component']['sales'] = str(sku_item['sales'])
                if sku_item.has_key('current_price'):
                    com['component']['price'] = str(sku_item['current_price'])
                com['component']['trackValue'] = 'item_sku_' + str(sku_id)
                if com['component'].has_key('action'):
                    com['component']['action']['trackValue'] = com['component']['trackValue']
                elif com['component'].has_key('actions'):
                    com['component']['actions'][0]['trackValue'] = com['component']['trackValue']
                data['items'].append(com)
        if sku_num >= FALL_PER_PAGE_NUM: 
            data['flag']  = str(flag + FALL_PER_PAGE_NUM)
        return '', data
        
