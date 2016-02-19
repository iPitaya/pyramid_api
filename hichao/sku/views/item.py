# -*- coding:utf-8 -*-

from pyramid.view import (
    view_defaults,
    view_config,
)
from hichao.sku.models.sku import (
    get_sku_by_id,
    get_old_sku_by_id,
)
from hichao.sku.models.worthy import get_worthy_sku_list
from hichao.timeline.models.timeline import (
    get_time_line_units_by_power,
    get_time_line_units_by_cate_ids,
    TIME_LINE,
)
from hichao.base.views.view_base import View
from hichao.util.object_builder import (
    build_worthy_sku_by_id,
    build_item_component_by_sku_id,
)
from hichao.util.pack_data import (
    pack_data,
    version_ge,
)
from hichao.search.es import newest_sku
from hichao.util.collect_util import sku_collect_counter
from hichao.util.component_builder import (
    build_component_hangtag,
    calendar_builder,
)
from hichao.base.config import FALL_PER_PAGE_NUM, MYSQL_MAX_INT
from hichao.collect.models.sku_top import (
    sku_top_n,
    sku_top_n_count,
)
from hichao.util.cps_util import check_cps_type
from hichao.cache.cache import deco_cache
from hichao.util.date_util import (
    DAY,
    ZHOU_DICT,
    format_digital,
)
from random import randint
from hichao.util.statsd_client import statsd
import datetime


@view_defaults(route_name='items')
class ItemView(View):

    def __init__(self, request):
        super(ItemView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_items.get')
    @check_cps_type
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        with_drop = int(self.request.params.get('with_drop', 0))
        tp = self.request.params.get('type', 'selection')
        more_items = self.request.params.get('more_items', '')
        gv = self.request.params.get('gv', '')
        #if gv: gv = gv_float(gv)
        gf = self.request.params.get('gf', '')
        category_ids = self.request.params.get('category_ids', '')
        lite_action = 0
        ecshop_action = 0
        support_webp = 0
        support_ec = 0
        support_xiajia = 2
        if gf == 'iphone':
            if version_ge(gv, 5.2):
                lite_action = 1
            if version_ge(gv, 5.5):
                ecshop_action = 1
            if version_ge(gv, 6.0):
                support_webp = 1
                support_ec = 1
        elif gf == 'android':
            if version_ge(gv, 60):
                lite_action = 1
            if version_ge(gv, 70):
                ecshop_action = 1
            if version_ge(gv, 100):
                support_ec = 1
        elif gf == 'ipad':
            if version_ge(gv, 5.1):
                lite_action = 1
            support_ec = 1
        data = {}
        data['items'] = []
        if tp in ['selection', 'latest', 'unknown', 'worthy', 'shop']:
            _tp = TIME_LINE.SKU_V60
            if tp != 'selection':
                _tp = TIME_LINE.WORTH_SKU
            if tp == 'shop':
                _tp = TIME_LINE.SHOP
            if 0 == len(category_ids):
                if not flag:
                    units = get_time_line_units_by_power(MYSQL_MAX_INT, FALL_PER_PAGE_NUM, _tp)
                else:
                    units = get_time_line_units_by_power(flag, FALL_PER_PAGE_NUM, _tp)
            else:
                try:
                    category_ids = category_ids.split(',')
                    category_ids = [int(c_id) for c_id in category_ids]
                    if not flag:
                        units = get_time_line_units_by_cate_ids(category_ids, MYSQL_MAX_INT, FALL_PER_PAGE_NUM, _tp)
                    else:
                        units = get_time_line_units_by_cate_ids(category_ids, flag, FALL_PER_PAGE_NUM, _tp)
                except Exception as e:
                    print e

            for unit in units:
                flag = unit.power
                if unit.type == 'sku':
                    if tp != 'worthy':
                        #sku = unit.get_bind_drop()
                        sku_id = unit.get_component_type_id()
                        # if sku:
                        com = build_item_component_by_sku_id(sku_id, more_items, lite_action, self.cps_type, support_webp, support_ec, support_xiajia)
                        if com:
                            com['component']['trackValue'] = 'item_sku_' + str(sku_id)
                            if com['component'].has_key('action'):
                                com['component']['action']['trackValue'] = com['component']['trackValue']
                            elif com['component'].has_key('actions'):
                                com['component']['actions'][0]['trackValue'] = com['component']['trackValue']
                            data['items'].append(com)
                    else:
                        com = build_worthy_sku_by_id(unit.type_id, ecshop_action, support_webp, support_ec)
                        if com:
                            data['items'].append(com)
                elif unit.type == 'timesku':
                    if tp != 'worthy':
                        if not ((gf == 'iphone' and version_ge(gv, '6.3.4')) or (gf == 'android' and version_ge(gv, 634))):
                            if with_drop:
                                com = build_component_hangtag(unit)
                                com['component']['action'] = com['component']['actions'][1]
                                del(com['component']['actions'])
                                com['component']['trackValue'] = 'item_sku_' + str(unit.type_id)
                                com['component']['action']['trackValue'] = com['component']['trackValue']
                                data['items'].append(com)
                            else:
                                tm = {}
                                com = calendar_builder(unit)
                                com['componentType'] = 'calendar'
                                com['action'] = {}
                                tm['component'] = com
                                data['items'].append(tm)
                        if not with_drop:
                            #sku = unit.get_bind_drop()
                            sku_id = unit.get_component_type_id()
                            # if sku:
                            com = build_item_component_by_sku_id(sku_id, more_items, lite_action, self.cps_type, support_webp, support_ec, support_xiajia)
                            if com:
                                com['component']['trackValue'] = 'item_sku_' + str(sku_id)
                                if com['component'].has_key('action'):
                                    com['component']['action']['trackValue'] = com['component']['trackValue']
                                elif com['component'].has_key('actions'):
                                    com['component']['actions'][0]['trackValue'] = com['component']['trackValue']
                                data['items'].append(com)
                    else:
                        tm = build_worthy_calendar(unit)
                        data['items'].append(tm)
                        com = build_worthy_sku_by_id(unit.type_id, ecshop_action, support_webp, support_ec)
                        if com:
                            data['items'].append(com)
            if len(units) == FALL_PER_PAGE_NUM:
                data['flag'] = str(flag)
        else:
            flag = (flag != '' and [int(flag), ] or [0, ])[0]
            cnt = sku_top_n_count()
            if flag == 0:
                flag = randint(cnt / 2, cnt)
            elif flag >= cnt:
                flag = 0
            _skus = sku_top_n(flag, FALL_PER_PAGE_NUM)
            _skus = [sku[0] for sku in _skus]
            for sku in _skus:
                com = build_item_component_by_sku_id(sku, more_items, lite_action, self.cps_type, support_webp, support_ec)
                if com:
                    com['component']['trackValue'] = 'item_sku_' + str(sku)
                    if com['component'].has_key('action'):
                        com['component']['action']['trackValue'] = com['component']['trackValue']
                    elif com['component'].has_key('actions'):
                        com['component']['actions'][0]['trackValue'] = com['component']['trackValue']
                if com:
                    data['items'].append(com)
            data['flag'] = str(flag + FALL_PER_PAGE_NUM + 1)
        return '', data


def build_worthy_calendar(obj):
    com = {}
    cal = {}
    cal['componentType'] = 'calendarWorthy'
    cal['month'] = obj.get_component_month()
    cal['weekDay'] = obj.get_component_week_day()
    cal['monthOnly'] = obj.get_component_month_only()
    cal['yearShort'] = obj.get_component_year_short()
    cal['day'] = obj.get_component_day()
    cal['showTime'] = obj.get_component_show_time()
    cal['text'] = u'精选超值单品'
    com['component'] = cal
    return com
