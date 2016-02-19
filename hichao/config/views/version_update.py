# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.util.statsd_client import statsd
from hichao.config.views.config  import  (
        category_config,
        iphone_app,
        iphone_lite_app,
        ipad_app,
        android_app,
        default_splash,
        mxyc_lite_ip_appkey,
        mxyc_lite_ad_appkey,
    )
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        version_eq,
        version_gt,
        )

@view_defaults(route_name = 'check_update')
class VersionUpdate(View):
    def __init__(self, request):
        super(VersionUpdate, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_check_update.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        app_version = self.request.params.get('gv', '0')
        app_from = self.request.params.get('gf', None)
        app_name = self.request.params.get('gn', '')
        _app = {}
        if app_from == 'android':
            if android_app['version'] and version_gt(android_app['version'], app_version):
                _app = android_app
        elif app_from == 'ipad':
            if ipad_app['version'] and version_gt(ipad_app['version'], app_version):
                _app = ipad_app
        elif app_name == 'mxyc_ip':
            if iphone_app['version'] and version_gt(iphone_app['version'], app_version):
                _app = iphone_app
        elif app_name == 'mxyc_lite_ip':
            if iphone_lite_app['version'] and version_gt(iphone_lite_app['version'], app_version):
                _app = iphone_lite_app
        result = {}
        result['app'] = _app
        return '',result
