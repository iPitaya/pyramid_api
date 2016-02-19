# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.app.views.oauth2 import check_permission
from hichao.base.views.view_base import View
from hichao.collect.models.fake import collect_count
from hichao.util.pack_data import pack_data
from hichao.util.statsd_client import statsd
from hichao.tuangou.models.tuangouinfo import get_buying_info_datablock_list
from hichao.tuangou.models.count import (
        tuangou_attend_new,
        tuangou_sku_attend_new,
        )
from hichao.tuangou.models.attend_util import (
        judge_state,
        COUNT_FUNC_DICT,
        COUNT_FAKE_NUM,
        )
from icehole_client.tuangou_client import (
        get_buying_info,
        get_buying_sku_info,
        get_buying_id_with_sku_id,
        )
import time

notice_url = 'http://hichao.com/android_taobao/notice.htm'

@view_defaults(route_name = 'tuan_state')
class Tuan(View):
    def __init__(self, request):
        super(Tuan, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_tuan_state.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        user_id = self.user_id
        tuan_id = self.request.params.get('tuan_id','')
        sku_id = self.request.params.get('sku_id','')
        if tuan_id == "":
            self.error['error'] = 'Arguments error'
            self.error['errorCode'] = '10001'
            return '', {}
        tuan_id = int(tuan_id)
        sku_id = int(sku_id) if sku_id else 0

        buying_info = get_buying_info(tuan_id)
        start_time = int(buying_info.start_date)
        end_time = int(buying_info.end_date)
        now = int(time.time())
        if start_time <= now or now <= end_time or now <=start_time:
            if sku_id != 0:
                tuangou_sku_attend_new(user_id, sku_id)
            else:
                tuangou_attend_new(user_id, tuan_id)

        data = {}
        state, expires = judge_state(now, start_time, end_time)
        data['tuanState'] = state
        count = 0
        if sku_id:
            sku = get_buying_sku_info(sku_id)
            count = COUNT_FUNC_DICT['tuangou_sku'](sku_id)
            count = collect_count(tuan_id, count, sku.publish_date) + COUNT_FAKE_NUM
        else:
            count = COUNT_FUNC_DICT['tuangou'](tuan_id)
            count = collect_count(tuan_id, count, start_time - 86400 * 5) + COUNT_FAKE_NUM
        data['peopleCount'] = str(count)
        data['expires'] = expires
        return '', data

