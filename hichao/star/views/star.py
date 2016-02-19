# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.star.models.star import (
        get_star_by_star_id,
        get_selfie_star_ids,
        )
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        version_gt,
        )
from hichao.search.es import stars
from hichao.base.config import (
        FALL_PER_PAGE_NUM,
        CATEGORY_DICT,
        HOME_CATEGORY,
        MYSQL_MAX_INT,
        )
from hichao.timeline.models.timeline import (
        get_time_line_units_by_power,
        get_droptype_by_timeline_type_id,
        TIME_LINE,
        )
from hichao.util.component_builder import (
        build_component_star,
        build_component_calendar,
        build_component_drop,
        build_component_hangtag,
        )
from hichao.base.views.view_base import View
from hichao.util.object_builder import (
        build_star_by_star_id,
        build_star_detail_by_star_id,
        build_drop_by_timeline_unit_id,
        build_calendar_by_timeline_unit_id,
        build_hangtag_by_timeline_unit_id,
        build_flow_by_id,
        )
from hichao.collect.models.top import (
        star_top_n,
        star_top_n_count,
        )
from hichao.app.views.oauth2 import check_permission
from hichao.collect.models.star import star_collect_count
from icehole_client.Recommendation import RecommendationClient
from hichao.util.cps_util import check_cps_type
from hichao.util.statsd_client import statsd
import time
import random

star_collect_counter = star_collect_count

@view_defaults(route_name = 'stars')
class StarView(View):
    def __init__(self, request):
        super(StarView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_stars.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        category = self.request.params.get('category', '')
        query = CATEGORY_DICT.get(category, '')
        if not query: query = category
        gv = self.request.params.get('gv', '')
        #if gv: gv = gv_float(gv)
        gf = self.request.params.get('gf', '')
        self.lite_action = 0
        if (version_ge(gv, 60) and gf == 'android') or (version_ge(gv, 5.2) and gf == 'iphone') or (version_ge(gv, 5.1) and gf == 'ipad'): self.lite_action = 1
        if query == HOME_CATEGORY.CATEGORY_QUERY_STR_LAST:
            return self.get_time_line()
        elif query == HOME_CATEGORY.CATEGORY_QUERY_STR_HOT:
            return self.get_hot_stars()
        elif query == HOME_CATEGORY.CATEGORY_QUERY_STR_GUESS:
            return self.get_guess_stars()
        elif query == HOME_CATEGORY.CATEGORY_QUERY_STR_SELFIE:
            return self.get_selfie_stars()
        else:
            return self.get_category(query)

    def get_time_line(self):
        data = {}
        flag = self.request.params.get('flag', '')
        crop = self.request.params.get('crop', '')
        crop = 1 if crop else 0
        tp = TIME_LINE.STAR
        gv = self.request.params.get('gv', '')
        #if gv: gv = gv_float(gv)
        gf = self.request.params.get('gf', '')
        support_thread = 0
        support_flow = 0
        support_webp = 0
        if gf == 'iphone':
            if version_ge(gv, 3.5):
                tp = TIME_LINE.STAR_V35
                support_thread = 1
            if version_ge(gv, 5.2):
                support_flow = 1
            if version_ge(gv, 6.0):
                support_webp = 1
        elif gf == 'android':
            if version_ge(gv, 45):
                tp = TIME_LINE.STAR_V35
                support_thread = 1
            if version_ge(gv, 60):
                support_flow = 1
        elif gf == 'ipad':
            if version_ge(gv, 2.0):
                tp = TIME_LINE.STAR_V35
            if version_ge(gv, 4.0):
                support_thread = 1
            if version_ge(gv, 5.1):
                support_flow = 1
        tip = ''
        if not flag:
            units = get_time_line_units_by_power(MYSQL_MAX_INT, FALL_PER_PAGE_NUM, tp)
            pin = self.request.params.get('pin', '')
            pin = (pin and [int(pin),] or [0,])[0]
            num = units[0].power - pin
            if pin and (num > 0):
                tip = '首页更新了{0}条内容。'.format(num)
                data['tip'] = tip
            data['lts'] = str(int(time.time()))
            data['pin'] = str(units[0].power)
        else:
            flag = int(flag)
            units = get_time_line_units_by_power(flag, FALL_PER_PAGE_NUM, tp)
        data['items'] = []
        for unit in units:
            flag = str(unit.power)
            component = ''
            if unit.type == 'star':
                component = build_star_by_star_id(unit.type_id, crop, self.lite_action, support_webp)
                if component:
                    component['component']['trackValue'] = 'star_latest_' + component['component']['id']
                    if component['component'].has_key('action'):
                        component['component']['action']['trackValue'] = component['component']['trackValue']
            elif unit.type == 'time':
                component = build_calendar_by_timeline_unit_id(tp, unit.id, support_webp)
            elif unit.type == 'drop' or unit.type == 'thread':
                component = build_drop_by_timeline_unit_id(tp, unit.id, support_webp)
            elif unit.type == 'timedrop' or unit.type == 'timetuan':
                #drop_type = unit.get_drop_type()
                drop_type = get_droptype_by_timeline_type_id(tp, unit.id)
                if drop_type == 'thread' and not support_thread:
                    component = build_calendar_by_timeline_unit_id(tp, unit.id, support_webp)
                else:
                    component = build_hangtag_by_timeline_unit_id(tp, unit.id, support_webp)
            elif unit.type == 'flow' and support_flow:
                component = build_flow_by_id(unit.type_id, support_webp)
            if component:
                if unit.type != 'star' or unit.type != 'time':
                    component['component']['showId'] = str(unit.id)
                    component['component']['showType'] = '{0};;{1}'.format(unit.get_component_type(), get_droptype_by_timeline_type_id(tp, unit.id))
                    component['component']['showTypeId'] = str(unit.get_component_type_id())
                data['items'].append(component)
        if len(units) == FALL_PER_PAGE_NUM:
            data['flag'] = flag
        return '', data

    def get_category(self, query):
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        support_webp = 0
        if (version_ge(gv, '6.0') and gf == 'iphone'):
            support_webp = 1
        flag = self.request.params.get('flag', '')
        flag = (flag and [int(flag),] or [0,])[0]
        crop = self.request.params.get('crop', '')
        crop = 1 if crop else 0
        ids = stars(query, flag, FALL_PER_PAGE_NUM)
        data = {}
        data['items'] = []
        for id in ids:
            component = build_star_by_star_id(id, crop, self.lite_action, support_webp)
            if component:
                data['items'].append(component)
        if len(ids) == FALL_PER_PAGE_NUM:
            data['flag'] = str(flag + FALL_PER_PAGE_NUM)
        return '', data

    def get_hot_stars(self):
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        support_webp = 0
        if (version_ge(gv, '6.0') and gf == 'iphone'):
            support_webp = 1
        flag = self.request.params.get('flag', '')
        crop = self.request.params.get('crop', '')
        crop = 1 if crop else 0
        cnt = int(star_top_n_count())
        #flag = flag != '' and int(flag) or random.randint(cnt/2, cnt)
        #if flag >= cnt: flag = 0
        if not flag:
            flag = 0
        flag = int(flag)
        ids = star_top_n(offset = flag, limit = FALL_PER_PAGE_NUM)
        ids = [int(float(id[0])) for id in ids]
        data = {}
        data['items'] = []
        for id in ids[0:FALL_PER_PAGE_NUM - 1]:
            com = build_star_by_star_id(id, crop, self.lite_action, support_webp)
            if com:
                com['component']['trackValue'] = 'star_hot_' + com['component']['id']
                if com['component'].has_key('action'):
                    com['component']['action']['trackValue'] = com['component']['trackValue']
                data['items'].append(com)
        if len(ids) >= FALL_PER_PAGE_NUM:
            data['flag'] = str(flag + FALL_PER_PAGE_NUM - 1)
        return '', data

    @check_permission
    def get_guess_stars(self):
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        support_webp = 0
        if (version_ge(gv, '6.0') and gf == 'iphone'):
            support_webp = 1
        GUESS_PER_PAGE_NUM = 12
        gi = self.request.params.get('gi', '')
        if not gi:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        flag = self.request.params.get('flag', '')
        flag = (flag and [int(flag),] or [0,])[0]
        crop = self.request.params.get('crop', '')
        crop = 1 if crop else 0
        if self.user_id > 0:
            user_id = int(self.user_id)
        else:
            user_id = 0
        rc = RecommendationClient()
        ids = rc.get(gi, flag, GUESS_PER_PAGE_NUM, user_id)
        data = {}
        data['items'] = []
        for id in ids:
            com = build_star_by_star_id(id, crop, self.lite_action, support_webp)
            if com:
                com['component']['trackValue'] = 'star_guess_' + com['component']['id']
                if com['component'].has_key('action'):
                    com['component']['action']['trackValue'] = com['component']['trackValue']
                data['items'].append(com)
        if len(ids) == GUESS_PER_PAGE_NUM:
            data['flag'] = str(flag + GUESS_PER_PAGE_NUM)
        return '', data

    def get_selfie_stars(self):
        flag = self.request.params.get('flag', '')
        flag = float(flag) if flag else MYSQL_MAX_INT
        crop = self.request.params.get('crop', '')
        crop = 1 if crop else 0
        ids = get_selfie_star_ids(flag, FALL_PER_PAGE_NUM)
        support_webp = 1
        data = {}
        data['items'] = []
        for id in ids:
            com = build_star_by_star_id(id, crop, self.lite_action, support_webp)
            if com:
                flag = str(com['timestamp'])
                del(com['timestamp'])
                data['items'].append(com)
        if len(ids) == FALL_PER_PAGE_NUM:
            data['flag'] = flag
        return '', data

@view_defaults(route_name = 'star')
class StarDetailView(View):
    def __init__(self, request):
        super(StarDetailView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_star.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        star_id = self.request.params.get('id', '')
        if not star_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        support_webp = 0
        support_ec = 0
        support_part_color = 0         #调取部位图的新获取方法：0不支持，1支持
        if (version_ge(gv, '6.0') and gf == 'iphone'):
            support_webp = 1
        if (version_ge(gv, '6.0') and gf == 'iphone') or (version_ge(gv, 100) and gf == 'android'):
            support_ec = 1
        if (version_ge(gv, '6.3.4') and gf == 'iphone') or (version_ge(gv, 634) and gf == 'android'):
            support_part_color = 1 
        data = build_star_detail_by_star_id(star_id, support_webp, support_ec, support_part_color)
        if data:
            count = star_collect_counter(star_id, data['unixtime'])
            if not count: count = 0
            data['collectionCount'] = str(count)
            del(data['unixtime'])
        return '', data

@view_defaults(route_name = 'webhotstarids')
class WebHotStarIdsView(View):
    def __init__(self, request):
        super(WebHotStarIdsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_webhotstarids.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        if not flag:
            flag = 0
        flag = int(flag)
        ids = star_top_n(offset = flag, limit = FALL_PER_PAGE_NUM)
        ids_str = ','.join(map(str, ids))
        data = {}
        data['ids'] = ids_str
        if len(ids) >= FALL_PER_PAGE_NUM:
            data['flag'] = str(flag + FALL_PER_PAGE_NUM )
        return '',data
