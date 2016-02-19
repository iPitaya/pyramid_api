# -*- coding: utf-8 -*-
from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from hichao.base.views.view_base import View
from hichao.base.lib.require import require, RequirementException
from hichao.user.models.user import (
        get_location_info,
        )
from hichao.util.pack_data import pack_data
from hichao.util.statsd_client import statsd


@view_defaults(route_name='location')
class UserInfoView(View):
    def __init__(self, request):
        super(UserInfoView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_location.get')
    @view_config(request_method='GET', renderer = 'json')
    @pack_data
    def get(self):
        lat = self.request.params.get('lat','')
        lon = self.request.params.get('lon','')
        data = get_location_info(lat,lon)
        return '', data


if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

