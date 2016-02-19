# -*- coding: utf-8 -*-
from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from hichao.base.views.view_base import View
from hichao.base.lib.require import require, RequirementException
from hichao.user.models.user import user_new
from hichao.util.pack_data import pack_data
from hichao.app.views.oauth2 import check_permission
from hichao.forum.models.star_user import user_is_staruser
from hichao.util.statsd_client import statsd
from random import randint
from hichao.user.models.user  import add_user_avatar
from hichao.user.models.user  import get_user_by_id
from hichao.collect.models.star import star_count_by_user_id
from hichao.collect.models.sku import sku_count_by_user_id
from hichao.collect.models.topic import topic_count_by_user_id
from hichao.collect.models.thread import thread_count_by_user_id
from hichao.collect.models.brand import brand_count_by_user_id
from hichao.forum.models.thread import get_thread_count_by_user_id
from hichao.shop.models.goods_member import get_goods_count as get_member_goods_count
from hichao.util.ecshop_interface_util import get_user_hongbao_cupon_msg

@view_defaults(route_name='users')
class UserView(View):
    def __init__(self, request):
        super(UserView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_users.get')
    @view_config(request_method='GET', renderer = 'json')
    def get(self):
        resp = dict()
        token = self.request.params['token']
        resp["error"] = token
        return Response(resp)

    @statsd.timer('hichao_backend.r_users.post')
    @view_config(request_method='POST')
    def post(self):
        return Response('post')

    @statsd.timer('hichao_backend.r_users.delete')
    @view_config(request_method='DELETE')
    def delete(self):
        return Response('delete')

@view_defaults(route_name = 'check_subject_permission')
class CheckUserPermission(View):
    def __init__(self, request):
        super(CheckUserPermission, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_checn_subject_permission.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        if user_is_staruser(self.user_id):
            return '', {'link':'1'}
        return '', {'link':'0'}

@view_defaults(route_name = 'update_avatar')
class UpdateAvatarView(View):
    def __init__(self, request):
        super(UpdateAvatarView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_update_avatar.put')
    @check_permission
    @view_config(request_method = 'PUT', renderer = 'json')
    @pack_data
    def put(self):
        img_id = self.request.params.get('img_id','')
        data = {}
        if not img_id:
            self.error['error'] = 'sign Arguments error'
            self.error['errorCode'] = '10001'
            return '',{}
        if self.user_id < 1:
            self.error['error'] = 'User info expired.'
            self.error['errorCode'] = '20002'
            return '', {}
        status, _ = add_user_avatar(self.user_id,int(img_id))
        if not status:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
        get_user_by_id(self.user_id, use_cache = False)
        return '', {}

@view_defaults(route_name = 'user_space_numbers')
class UserSpaceNumberView(View):
    def __init__(self, request):
        super(UserSpaceNumberView, self).__init__()
        self.request = request

    @statsd.timer("hichao_backend.r_user_space_numbers.get")
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        token = self.request.params.get('access_token','')
        gv = self.request.params.get('gv','')
        if self.user_id < 1:
            return '', {}
        data = {}
        star_total = star_count_by_user_id(self.user_id)
        sku_total = sku_count_by_user_id(self.user_id)
        topic_total = topic_count_by_user_id(self.user_id)
        thread_total = thread_count_by_user_id(self.user_id)
        brand_total = brand_count_by_user_id(self.user_id)
        post_total = get_thread_count_by_user_id(self.user_id)
        member_goods_total = get_member_goods_count()
        # 优惠券
        coupon_total = '0'
        # 红包
        bonus_total = '0'
        d_attr = {'userid':self.user_id}
        msg = get_user_hongbao_cupon_msg('mxyc_ios',self.user_id,'user.promote.data',token,gv,d_attr)
        if msg:
            coupon_total = msg['coupon_amount']
            bonus_total = msg['bounsCount']
        data['starTotal'] = str(star_total)
        data['skuTotal'] = str(sku_total)
        data['topicTotal'] = str(topic_total)
        data['subjectTotal'] = str(thread_total)
        data['brandTotal'] = str(brand_total)
        data['postTotal'] = str(post_total)
        data['memberGoodsTotal'] = str(member_goods_total)
        data['couponTotal'] = str(coupon_total)
        data['bonusTotal'] = str(bonus_total)
        return '', data

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

