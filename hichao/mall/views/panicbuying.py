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

@view_defaults(route_name = 'panic_buying')
class Panic(View):
    def __init__(self,request):
        super(Panic,self).__init__()
        self.request = request

    
    @statsd.timer('hichao_backend.r_panic_buying.get')
    @view_config(request_method = 'GET',renderer = 'json')
    @pack_data
    def get(self):
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')

        data = {}
        #if (gf == 'iphone' and version_ge(gv, '6.1.0')) or (gf == 'android' and version_ge(gv, '110')):
        #    ''' 数据来自闪购后台 '''
        #    items = get_panic_by_flash_sale()
        #else:
        #    ''' 数据来自限时抢购后台 '''
        #    items = build_panic_buying()
        items = get_panic_by_flash_sale()
        data['items'] = items
        return '',data
