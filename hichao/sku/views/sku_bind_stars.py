# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        )
from hichao.base.views.view_base import View
from hichao.star.models.star_sku import get_star_ids_by_sku_id
from hichao.util.object_builder import build_embed_star_by_star_id
from hichao.util.statsd_client import statsd

@view_defaults(route_name = 'sku_bind_stars')
class SkuBindStarsView(View):
    def __init__(self, request):
        super(SkuBindStarsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_sku_bind_stars.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        sku_id = self.request.params.get('item_id', '')
        if not sku_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        gv = self.request.params.get('gv', '')
        #if gv: gv = gv_float(gv)
        gf = self.request.params.get('gf', '')
        self.lite_action = 0
        if (version_ge(gv, 60) and gf == 'android') or (version_ge(gv, 5.2) and gf == 'iphone'): self.lite_action = 1
        star_ids = get_star_ids_by_sku_id(sku_id)
        data = {}
        data['items'] = []
        for star_id in star_ids[:5]:
            com = build_embed_star_by_star_id(star_id, self.lite_action)
            if com:
                data['items'].append(com)
        return '', data

