# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.util.pack_data import (
        pack_data,
        version_gt,
        )
from hichao.base.views.view_base import View
from hichao.util.object_builder import (
        build_star_skus_by_star_id,
        CpsType,
        )
from hichao.util.statsd_client import statsd

notice_url = 'http://hichao.com/android_taobao/notice.htm'

@view_defaults(route_name = 'star_clues')
class StarClue(View):
    def __init__(self, request):
        super(StarClue, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_star_clues.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        star_id = int(self.request.params.get('id', -1))
        gf = self.request.params.get('gf', '')
        cps_type = CpsType.IPHONE
        if gf == 'ipad':
            cps_type = CpsType.IPAD
        items = build_star_skus_by_star_id(star_id, cps_type)
        data = {}
        data['items'] = items
        #=========================单品详情android返回强制升级页面兼容代码。。。===========================
        platform = self.request.params.get('gf', '')
        if platform == 'android':
            app_version = self.request.params.get('gv', '')
            #if app_version: app_version = int(app_version)
            if version_gt(30, app_version):
                for item in data['items']:
                    for _item in item['itemList']:
                        _item['component']['action']['link'] = notice_url
        #=================================================================================================
        return '', data

