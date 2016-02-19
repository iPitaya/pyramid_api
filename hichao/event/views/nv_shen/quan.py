# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.event.models.nv_shen.user_new import (
        add_nv_shen_user,
        is_nv_shen_user,
        alipay_related,
        )
from hichao.util.pack_data import pack_data
import datetime as dt
import re

re_phone = re.compile('(13|15|17|18)[0-9]{9}')
re_email = re.compile('^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$')

@view_defaults(route_name = 'event_nv_shen_quan')
class NvShenQuanView(View):
    def __init__(self, request):
        super(NvShenQuanView, self).__init__()
        self.request = request

    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        if self.user_id <= 0:
            return u'获取用户信息失败，请重新登录。', {'result':'0'}
        if is_nv_shen_user(self.user_id):
            return u'您已经领过女神券了哦。', {'result':'1'}
        alipay = self.request.params.get('alipay', '')
        if not alipay:
            return u'请输入您的支付宝账号。', {'result':'0'}
        if alipay_related(alipay):
            return u'该支付宝账号已经被其他用户使用。', {'result':'0'}
        res = check_alipay(alipay)
        if not res:
            return u'您的支付宝账号格式不正确，请重新输入。', {'result':'0'}
        result = add_nv_shen_user(self.user_id, alipay)
        if not result:
            return u'领取失败，请重新领取。', {'result':'0'}
        return '', {'result':'1'}

def check_alipay(alipay):
    if re_phone.match(alipay):
        return 1
    if re_email.match(alipay):
        return 1
    return 0

