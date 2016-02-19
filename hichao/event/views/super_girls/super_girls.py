# -*- coding:utf-8 -*-

from pyramid.view import (
    view_defaults,
    view_config,
    )
from hichao.util.pack_data import pack_data
from hichao.event.models.super_girls.sg_mobile import (
    add_super_girls_act_mobile,
    get_super_girls_act_mobile,
    sg_send_code,
    logger,
    )
from hichao.base.views.view_base import View
from hichao.user.models.user_register import check_tel_legal
from hichao.util.statsd_client import statsd
import datetime

@view_defaults(route_name = 'mgtv_sg_mobile')
class SGMobileView(View):
    def __init__(self, request):
        super(SGMobileView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mgtv_sg_mobile.post')
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        mobile = self.request.params.get('mobile', '').strip()
        if not mobile:
            self.error['error'] = 'Arguments missing'
            self.error['errorCode'] = '10001'
            return u'还没有输手机号哦~', {}
        if not check_tel_legal(mobile):
            self.error['error'] = 'Arguments error'
            self.error['errorCode'] = '10001'
            return u'手机号格式不正确哟~', {}
        logger.info('{0} {1} view add'.format(mobile, datetime.datetime.now()))
        mobile_user = get_super_girls_act_mobile(mobile)
        if mobile_user:
            logger.info('{0} {1} view got'.format(mobile, datetime.datetime.now()))
            self.error['error'] = 'Operation failed'
            self.error['errorCode'] = '30001'
            return u'这个手机号已经领过金币了哦~', {}
        res = add_super_girls_act_mobile(mobile)
        if res == -1:
            logger.info('{0} {1} view got'.format(mobile, datetime.datetime.now()))
            self.error['error'] = 'Operation failed'
            self.error['errorCode'] = '30001'
            return u'这个手机号已经领过金币了哦~', {}
        if res == 0:
            logger.info('{0} {1} view error'.format(mobile, datetime.datetime.now()))
            self.error['error'] = 'Operation failed'
            self.error['errorCode'] = '30001'
            return u'出错了，请稍候重试。。', {}
        res = sg_send_code(mobile)
        return '', {}

