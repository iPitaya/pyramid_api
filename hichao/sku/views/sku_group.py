# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )   
from hichao.base.views.view_base import View
from hichao.util.pack_data import pack_data
from hichao.util.object_builder import (
        build_group_sku_by_id,
        )   
from hichao.sku.models.sku import get_sku_by_id
from hichao.base.config import FALL_PER_PAGE_NUM

from icehole_client.banner_recommend_client import BannerRecommendClient
from hichao.util.statsd_client import statsd

@view_defaults(route_name = 'group_sku')
class GroupSkuView(View):
    def __init__(self, request):
        super(GroupSkuView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_group_sku.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        banner_recommend_id = self.request.params.get('id', '') 
        offset = self.request.params.get('flag', '') 
        offset = int(offset) if offset else 0
        try:
            banner_recommend_id = int(banner_recommend_id)
        except:
            banner_recommend_id = 0
        if not banner_recommend_id or banner_recommend_id <= 0:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        #请求中间件，获得sku_ids, FALL_PER_PAGE_NUM + 1个
        banner_recommend_client = BannerRecommendClient()
        sku_ids = banner_recommend_client.getSkuIdList(banner_recommend_id, offset, FALL_PER_PAGE_NUM + 1)
        data = {}
        data["items"] = []
        banner_recommend = banner_recommend_client.getRecommend(banner_recommend_id)
        data["title"] = ""
        if banner_recommend_id:
            data["title"] = banner_recommend.title
        if len(sku_ids) > FALL_PER_PAGE_NUM:
            data["flag"] = str(FALL_PER_PAGE_NUM + offset)
            sku_ids = sku_ids[:-1]
        for sku_id in sku_ids:
            com = build_group_sku_by_id(sku_id)
            if com:
                data['items'].append(com)
        return '', data
