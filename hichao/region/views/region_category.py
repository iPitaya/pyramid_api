# -*- coding:utf-8 -*-

from pyramid.view import (
    view_defaults,
    view_config,
    )

from hichao.mall.models.panicbuying import build_panic_buying
from hichao.base.views.view_base  import View
from hichao.util.pack_data  import pack_data
from hichao.util.statsd_client import statsd
from hichao.app.views.oauth2 import check_permission
from hichao.flash_sale.models.flash_sale_sku import get_panic_by_flash_sale
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        version_gt,
        )

@view_defaults(route_name = 'region_category')
class RegionCategory(View):
    def __init__(self,request):
        super(RegionCategory,self).__init__()
        self.request = request

    
    @statsd.timer('hichao_backend.r_panic_region_category.get')
    @view_config(request_method = 'GET',renderer = 'json')
    @pack_data
    def get(self):
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        region_id = self.request.params.get('id', '')
        data = {}
        cates = ['全部','上衣','裤子','裙子','鞋子','包包','配饰','美妆']
        data['items'] = cates
        return '',data

