# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        version_eq,
        )
from hichao.base.views.view_base import View
from hichao.util.statsd_client import statsd, timeit
from hichao.config.models.splash import (
        get_last_splash_version,
        get_match_splash,
        )
import time
from hichao.banner.models.banner_CMS import get_banner_components_by_flags_dict

@view_defaults(route_name = 'splash')
class SplashView(View):
    def __init__(self, request):
        super(SplashView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_splash.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        if not get_last_splash_version():
            return '', {}
        gs = self.request.params.get('gs', '')
        width = 0
        height = 1
        if 'x' in gs:
            width, height = gs.split('x', 1)
            width = int(width) if width.isdigit() else 0
            height = int(height) if height.isdigit() else 1
        splash = get_match_splash(width, height)
        data = {}
        data['items'] = []
        if splash:
            sp = {}
            sp['picUrl'] = splash.get_component_pic_url()
            sp['action'] = {}
            data['items'].append(sp)
        return '', data


@view_defaults(route_name = 'cms_splash')
class CMSSplashView(View):
    def __init__(self, request):
        super(CMSSplashView, self).__init__()
        self.request = request
        self.SPLASH_960 = [
                ['app_second_960'],
        ]
        self.SPLASH_1136 = [
                ['app_second_1136'],
        ]

    @statsd.timer('hichao_backend.r_cms_splash.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        # iphone6 750 * 1334
        # iphone5s 640 * 1136
        data = {}
        gs = self.request.params.get('gs', '')
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        if not gs: gs = '640x1136'
        width, height = gs.split('x', 1)
        SPLASH = self.get_match_splash_cms(width, height)
        comType = 'cell'
        null_row_support = 1
        #兼容ios的bug
        support_action = 1
        splash_items = []
        items = []
        if gf == 'iphone' and version_ge('6.1.0',gv):
            support_action = 0
        splash_items = get_banner_components_by_flags_dict(SPLASH,comType,null_row_support)
        ''' 应付苹果审核 '''
        SPLASH_APPLE = [
                        ['appreview_splash'],
                        ]
        apple_items = get_banner_components_by_flags_dict(SPLASH_APPLE,comType,null_row_support)
        if apple_items:
            if gf == 'iphone' and version_eq(gv,apple_items[0]['component']['title']):
                apple_items[0]['component']['action']['title'] = ''
                apple_items[0]['component']['action']['titleStyle'] = {}
                splash_items = apple_items
        for item in splash_items:
            sp_dt = {}
            if item['component']:
                if support_action:
                    sp_dt['action'] = item['component']['action']
                else:
                    sp_dt['action'] = {}
                sp_dt['picUrl'] = item['component']['picUrl']
            items.append(sp_dt)
        if items:
            data['items'] = items
        return '',data

    def get_match_splash_cms(self, width, height):
        width, height = int(width), int(height)
        sp_960_w = 640
        sp_960_h = 960
        sp_1136_w = 640
        sp_1136_h = 1136
        diff_960 = abs(float(sp_960_w + width)/(sp_960_h + height) - float(sp_960_w)/sp_960_h)
        diff_1136 = abs(float(sp_1136_w + width)/(sp_1136_h + height) - float(sp_1136_w)/sp_1136_h)
        return self.SPLASH_960 if diff_960 < diff_1136 else self.SPLASH_1136

