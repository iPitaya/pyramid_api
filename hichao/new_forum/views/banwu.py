# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.base.config import FALL_PER_PAGE_NUM
from hichao.util.pack_data import pack_data
from hichao.forum.models.banwu_tangzhu import get_tangzhu_ids
from hichao.util.object_builder import build_tangzhu_by_id
from hichao.cache.cache import deco_cache
from hichao.util.date_util import DAY
from hichao.util.cps_util import get_cps_key, cps_title_styles_dict
from hichao.util.statsd_client import statsd

import copy

@view_defaults(route_name = 'banwu_team')
class BanwuTeamView(View):
    def __init__(self, request):
        super(BanwuTeamView, self).__init__()
        self.request = request

    # 堂主不做分页，已定！
    @statsd.timer('hichao_backend.r_banwu_team.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        category_id = self.request.params.get('category_id', '')
        if not category_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        ids = get_tangzhu_ids(category_id)
        data = {}
        data['items'] = []
        for id in ids:
            com = build_tangzhu_by_id(id)
            if com: data['items'].append(com)
        data['applyAction'] = get_banwu_apply_action()
        return '', data

@deco_cache(prefix = 'banwu_apply_action', recycle = DAY)
def get_banwu_apply_action():
    url = 'http://test.hichao.com/wap/auth'
    means = 'push'
    title_style = copy.deepcopy(cps_title_styles_dict[get_cps_key('', '')])
    title_style['text'] = u'申请小主'
    title_style['picUrl'] = ''
    action = {
            'actionType':'webview',
            'titleStyle':title_style,
            'means':means,
            'webUrl':url,
            }
    return action
