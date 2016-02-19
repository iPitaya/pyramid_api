# -*- coding: utf-8 -*-

from pyramid.view import view_defaults
from pyramid.view import view_config
from hichao.base.views.view_base import View, require_type
from hichao.base.config import COLLECTION_TYPE
from hichao.app.views.oauth2 import check_permission
from hichao.sku.models.sku import get_sku_id_by_source_sourceid
from hichao.collect.models.sku import sku_collect_user_has_item
from hichao.collect.models.star import star_collect_user_has_item
from hichao.collect.models.topic import topic_user_has_item
from hichao.collect.models.thread import thread_user_has_item
from hichao.util.statsd_client import statsd
from hichao.util.pack_data import pack_data

@view_defaults(route_name = 'collect_state')
class CollectStateView(View):
    def __init__(self, request):
        super(CollectStateView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_collect_state.get')
    @check_permission
    @require_type
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        '''
        type, ids, source, source_id
        '''
        if self.user_id == -2:
            self.error['error'] = 'User info error.'
            self.error['errorCode'] = '20002'
            return '', {}
        if self.user_id == -1:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        ids = self.request.params.get('ids', '')
        item_ids = ids.split(',')
        if self.type == COLLECTION_TYPE.SKU:
            source = self.request.params.get('source', '')
            if source:
                source_id = self.request.params.get('source_id', '')
                if not source_id:
                    self.error['error'] = 'Arguments missing'
                    self.error['errorCode'] = '10002'
                    return '', {}
                sku_id = get_sku_id_by_source_sourceid(source, source_id)
                if not sku_id:
                    self.error['error'] = 'Operation failed'
                    self.error['errorCode'] = '30001'
                    return '', {}
                res = sku_collect_user_has_item(self.user_id, sku_id)
                if res: res = '1'
                else: res = '0'
                return '', {'collected':res}
        data = {}
        if self.type == COLLECTION_TYPE.STAR:
            method = star_collect_user_has_item
            data['type'] = 'star'
        elif self.type == COLLECTION_TYPE.SKU:
            method = sku_collect_user_has_item
            data['type'] = 'sku'
        elif self.type == COLLECTION_TYPE.TOPIC:
            method = topic_user_has_item
            data['type'] = 'topic'
        elif self.type == COLLECTION_TYPE.THREAD:
            method = thread_user_has_item
            data['type'] = 'thread'
        data['items'] = []
        for id in item_ids:
            res = method(self.user_id, id)
            if res: res = '1'
            else: res = '0'
            data['items'].append({str(id):res,})
        return '', data

