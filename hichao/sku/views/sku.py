# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        )
from hichao.util.object_builder import (
        build_imgs_by_sku,
        build_sku_detail_by_sku_id,
        build_worthy_sku_detail_by_sku_id,
        )
from hichao.util.cps_util import check_cps_type
from hichao.sku.models.sku import (
        get_sku_by_id,
        get_sku_ids_by_source_sourceids,
        get_sku_cache_by_sourceid,
        )
from hichao.base.lib.redis import redis
from hichao.sku.config import (
        SKU_PV_PREFIX,
        SKU_UV_PREFIX,
        )
from hc.redis.count import Counter, SetCounter
from hichao.collect.models.sku import sku_collect_count
from hichao.util.statsd_client import statsd
import datetime
import time

sku_collect_counter = sku_collect_count

@view_defaults(route_name = 'sku_imgs')
class SkuImgView(View):
    def __init__(self, request):
        super(SkuImgView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_sku_imgs.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        source = self.request.params.get('source', '')
        source_id = self.request.params.get('source_id', '')
        width = self.request.params.get('width', '320')
        if not source_id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        if source == 'taobao':
            source = 'tmall'
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        support_webp = 0
        if (version_ge(gv, '6.0') and gf == 'iphone'):
            support_webp = 1
        data = {}
        data['items'] = build_imgs_by_sku(source, source_id, width, support_webp)
        return '', data

@view_defaults(route_name = 'sku')
class SkuView(View):
    def __init__(self, request):
        super(SkuView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_sku.get')
    @check_cps_type
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        sku_id = self.request.params.get('id', '')
        if not sku_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        support_webp = 0
        if (version_ge(gv, '6.0') and gf == 'iphone'):
            support_webp = 1
        data = build_sku_detail_by_sku_id(sku_id, self.cps_type, support_webp)
        if data:
            count = sku_collect_counter(sku_id, data['unixtime'])
            if not count: count = 0
            data['collectionCount'] = str(count)
            del(data['unixtime'])
        return '', data

@view_defaults(route_name = 'worthy_sku')
class WorthySkuView(View):
    def __init__(self, request):
        super(WorthySkuView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_worthy_sku.get')
    @check_cps_type
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        sku_id = self.request.params.get('id', '')
        if not sku_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        # add pv, uv
        gi = self.request.params.get('gi', '')
        pv_key = SKU_PV_PREFIX.format(sku_id)
        uv_key = SKU_UV_PREFIX.format(sku_id)
        pv_counter = Counter(redis)
        uv_counter = SetCounter(redis, uv_key)
        pv_counter._incr(pv_key)
        uv_counter.add(gi)

        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        support_webp = 0
        if (version_ge(gv, '6.0') and gf == 'iphone'):
            support_webp = 1
        data = build_worthy_sku_detail_by_sku_id(sku_id, self.cps_type, support_webp)
        return '', data


@view_defaults(route_name = 'src2sku')
class SourceIdsToSkuIdsView(View):
    def __init__(self, request):
        super(SourceIdsToSkuIdsView, self).__init__()
        self.request = request
    
    @statsd.timer('hichao_backend.r_src2sku.get')
    @check_cps_type
    @view_config(request_method = 'GET', renderer = 'json')
    def get(self):
        start = time.time()
        source_ids = self.request.params.get('ids', '')
        _source_ids = source_ids
        data = {}
        new_ids = []
        items = []
        source_ids = [str(id) for id in source_ids.split(',') if id.isdigit()]
        #items = get_sku_ids_by_source_sourceids('ecshop',new_ids)
        for source_id in source_ids:
            item = get_sku_cache_by_sourceid(source_id)
            if not item:
                continue
            public_time =  time.mktime(item.publish_date.timetuple())
            peopleCount = sku_collect_count(str(item.sku_id),public_time)
            temp = {}
            temp['sku_id'] = str(item.sku_id)
            temp['collection_count'] = str(peopleCount)
            data[str(item.source_id)] = temp
        #print '1'*20, '{0}||{1}||{2}'.format(_source_ids, data, time.time() - start)
        return data

