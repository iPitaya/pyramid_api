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
from hichao.timeline.models.timeline  import get_daily_hotsale_unit_by_type_id

@view_defaults(route_name = 'hot_sale_skus')
class HotSaleSkusView(View):
    def __init__(self, request):
        super(HotSaleSkusView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_hot_sale_skus.get')
    @check_cps_type
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        sort = self.request.params.get('sort', 'all')
        if not flag :
            flag = 0
        asc_desc = self.request.params.get('asc', '1')
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        #if not query:
        #    self.error['error'] = 'Arguments missing.'
        #    self.error['errorCode'] = '10002'
        #    return '', {}
        result = get_daily_hotsale_unit_by_type_id(sort, flag, FALL_PER_PAGE_NUM, asc_desc)
        lite_action = 1
        ecshop_action = 1
        support_webp = 1
        support_ec = 1
        support_xiajia = 1
        data = {}
        if not result:
            return '', data
        result_num = len(result)
        data['items'] = []
        for item in result:
            sku_id = item.sku_id
            com = build_item_component_by_sku_id(sku_id,0,lite_action,self.cps_type,support_webp,support_ec,support_xiajia)
            if com:
                com['component']['trackValue'] = 'item_sku_' + str(sku_id)
                if com['component'].has_key('action'):
                    com['component']['action']['trackValue'] = com['component']['trackValue']
                elif com['component'].has_key('actions'):
                    com['component']['actions'][0]['trackValue'] = com['component']['trackValue']
                data['items'].append(com)
        if result_num >= FALL_PER_PAGE_NUM: 
            data['flag']  = str(int(flag) + FALL_PER_PAGE_NUM)
        return '', data
        
