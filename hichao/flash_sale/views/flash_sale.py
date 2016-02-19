# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
    )

from hichao.app.views.oauth2 import check_permission
from hichao.base.views.view_base import View
from hichao.util.statsd_client import statsd
from hichao.flash_sale.models.flash_sale  import (
        get_flash_sale_tags_info,
        get_flash_sale_tags_info_with_endtime,
        )
from hichao.flash_sale.models.flash_sale_sku  import get_flash_sale_skus_by_flash_sale_id
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        version_gt,
        )
from hichao.flash_sale.models.count import flashsale_attend_new
from hichao.app.views.oauth2 import (
        check_permission,
        )
from hichao.base.config import FALL_PER_PAGE_NUM

@view_defaults(route_name = 'flash_sale')
class FlashSaleView(View):
    def __init__(self,request):
        super(FlashSaleView,self).__init__()
        self.request = request

    @statsd.timer('hichao_bachend.r_flashsale.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        data = {}
        items = get_flash_sale_tags_info()
        data['items'] = items
        return '',data


@view_defaults(route_name = 'flash_sale_skus')
class FlashSaleSkusView(View):
    def __init__(self,request):
        super(FlashSaleSkusView,self).__init__()
        self.request = request

    @statsd.timer('hichao_bachend.r_flash_sale_skus.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        data = {}
        flag = self.request.params.get('flag','')
        flashsale_id = self.request.params.get('flashsale_id','')
        if flashsale_id == '':
            self.error['error']='Arguments error'
            self.error['errorCode']='10001'
            return '',{}

        if not flag:
            flag = 0
        else:
            flag = int(flag)
        data = get_flash_sale_skus_by_flash_sale_id(int(flashsale_id), flag, FALL_PER_PAGE_NUM)
        if flag == 0:
            flashsale_attend_new(self.user_id,int(flashsale_id))
        if data:
            items_num = len(data['items'])
            if items_num >= FALL_PER_PAGE_NUM:
                flag = flag + items_num
                data['flag'] = flag
        return '',data
