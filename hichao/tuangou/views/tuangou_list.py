# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.util.pack_data import pack_data
from hichao.base.views.view_base import View

from hichao.tuangou.models.tuangoulist import (
        get_buying_datablock_list,
        get_starting_buying_datablock_list,
        )
from hichao.util.statsd_client import statsd

notice_url = 'http://hichao.com/android_taobao/notice.htm'

@view_defaults(route_name = 'tuan_list')
class TuanList(View):
    def __init__(self, request):
        super(TuanList, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_tuan_list.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag','')
        visit = self.request.params.get('visit','')
        if flag=='':
            flag=0
        else:
            flag = int(flag)
        
        if visit == 'starting':
            data = get_starting_buying_datablock_list(offset=flag)
        else:
            data = get_buying_datablock_list(offset=flag)            
        return '', data

