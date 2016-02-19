# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.util.pack_data import pack_data
from hichao.util.date_util import FIVE_MINUTES
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.cache.cache import deco_cache
from hichao.tuangou.models.tuangoulist import get_last_tuangou_publish_date
from icehole_client.message_client import AllClient, OfficialClient
from hichao.util.statsd_client import statsd
import time


@view_defaults(route_name = 'notification_num')
class NotificationNumView(View):
    def __init__(self, request):
        super(NotificationNumView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_notification_num.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', 'iphone')
        ltss = self.request.params.get('lts', '')
        tps = self.request.params.get('type', 'tuan_list')
        tps = tps.split(',')
        ltss = ltss.split(',')
        types = zip(tps, ltss)
        data = {}
        data['items'] = []
        for _type in types:
            tp, lts = _type
            lts = float(lts) if lts else 0
            if tp == 'tuan_list':
                more_tuan = 0
                last_ts = get_last_tuangou_publish_date()
                if last_ts: last_ts = float(last_ts)
                if not lts or lts < last_ts:
                    more_tuan = 1
                lts = last_ts
                noti_tuan = {}
                if more_tuan: noti_tuan['moreTuanGou'] = str(more_tuan)
                if gv == '47': noti_tuan['moreTuanGou'] = '0'
                noti_tuan['type'] = tp
                noti_tuan['lts'] = str(lts)
                data['items'].append(noti_tuan)
            elif tp == 'msg':
                noti_msg = {}
                noti_msg['type'] = tp
                uid = int(self.user_id)
                if uid > 0:
                    all_client = AllClient()
                    count = all_client.count(uid)
                    all_client.close()
                    if count: noti_msg['totalCount'] = str(count)
                if not lts:
                    # 如果用户第一次打开，lts设定为当前时间前推24小时，即可以看到之前一天之内推的官方消息。
                    lts = int(time.time()) - 86400
                noti_msg['officialCount'] = '0'
                noti_msg['lts'] = str(lts)
                data['items'].append(noti_msg)
        return '', data

if __name__ == '__main__':
    print get_last_tuangou_publish_date()

