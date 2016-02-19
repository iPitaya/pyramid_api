# -*- coding: utf-8 -*-

from pyramid.view import (
    view_defaults,
    view_config,
)
from hichao.sku.models.navigator import (
    get_region_recommend_tag,
    get_region_navigator,    
        )
from hichao.base.config import REDIS_CONFIG
from hichao.base.views.view_base import View
from hichao.util.pack_data import pack_data
from hichao.util.statsd_client import statsd

import redis
client = redis.Redis(**REDIS_CONFIG)

#6.4.0首页、专区瀑布流分类导航
@view_defaults(route_name='region_recommend_tag')
class RegionRecommendTagView(View):

    def __init__(self, request):
        super(RegionRecommendTagView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_recommend_tag.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        limit = 10
        region = self.request.params.get('region', '')
        data['items'] = get_region_recommend_tag(region, limit) 
        return '',data

#6.4.0专区顶部分类导航
@view_defaults(route_name='region_navigator')
class RegionNavigatorView(View):

    def __init__(self, request):
        super(RegionNavigatorView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_navigator.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        data['items'] = get_region_navigator()
        return '',data        



























