# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View

from hichao.app.views.oauth2 import (
        check_permission,
        )

from hichao.tuangou.models.count import (
        tuangou_sku_attend_new,
        )
from hichao.tuangou.models.tuangousku import (
        get_if_tuangou,
        get_tuangou_sku_id_by_source_id,
        get_tuangou_id_by_tuangou_sku_id,
        get_tuangou_info_by_tuangou_id,
        )
from hichao.util.statsd_client import statsd

from hichao.util.pack_data import pack_data

@view_defaults(route_name = 'tuan_sku_count')
class TuanSkuVisit(View):
    def __init__(self, request):
        super(TuanSkuVisit, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_tuan_sku_count.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        user_id=self.user_id
        id = int(self.request.params.get('id',0))
        tuangou_sku_attend_new(user_id, id)

        return '', {'code':1, 'msg':'Ok'}

@view_defaults(route_name = 'tuan_sku_normal')
class TuanSkuNormal(View):
    def __init__(self, request):
        super(TuanSkuNormal, self).__init__()
        self.request = request

    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        source_ids = self.request.params.get('source_ids', '')
        data = {}
        if source_ids:
            #data['items'] = {source_ids:0}
            source_id_list = source_ids.split(',')
            data['items'] = {str(source_id):0 for source_id in source_id_list}
            for source_id in source_id_list:
                tuangou_sku_ids = get_tuangou_sku_id_by_source_id(str(source_id))
                for tuangou_sku_id in tuangou_sku_ids:
                    tuangou_id_raw = get_tuangou_id_by_tuangou_sku_id(tuangou_sku_id)
                    if tuangou_id_raw:
                        if not isinstance(tuangou_id_raw, int):
                            tuangou_id = tuangou_id_raw[0]
                        else:
                            tuangou_id = tuangou_id_raw
                        tuangou_exist_id = get_tuangou_info_by_tuangou_id(tuangou_id)
                        if tuangou_exist_id:
                            data['items'][str(source_id)] = 1
                            break
            return '',data
        else:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '',{}
