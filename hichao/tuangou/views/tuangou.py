# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        )
from hichao.base.views.view_base import View

from hichao.tuangou.models.tuangouinfo import (
        get_buying_info_datablock_list,
        )

from hichao.app.views.oauth2 import (
        check_permission,
        )

from hichao.tuangou.models.count import (
        tuangou_attend_new,
        tuangou_sku_attend_new,
        )
from hichao.util.statsd_client import statsd

@view_defaults(route_name = 'tuan')
class Tuan(View):
    def __init__(self, request):
        super(Tuan, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_tuan.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        user_id=self.user_id
        flag = self.request.params.get('flag', '')
        with_main = self.request.params.get('with_main','')
        gf = self.request.params.get('gf','')
        gv = self.request.params.get('gv','')
        #if gv: gv = gv_float(gv)
        lite_action = 0
        support_ec = 0
        if (gf == 'android' and version_ge(gv, 70)) or (gf == 'iphone' and version_ge(gv, 5.5)):
            lite_action = 1
        if (gf == 'android' and version_ge(gv, 100)) or (gf == 'iphone' and version_ge(gv, 6.0)) or gf == 'ipad':
            support_ec = 1
        if with_main!='':
            with_main = True
        else:
            with_main = False

        if flag=='':
            flag=0
        else:
            flag=int(flag)
        tuan_id = self.request.params.get('tuan_id','')
        if tuan_id=="":
            tuan_id='0'
        id = int(tuan_id)
        if id==0:
            self.error['error']='Arguments error'
            self.error['errorCode']='10001'
            return '', {}
        data = get_buying_info_datablock_list(item_id=id, offset=flag, with_main=with_main,lite_action = lite_action, support_ec = support_ec)
        if flag==0:
            tuangou_attend_new(user_id, id)
        return '', data

