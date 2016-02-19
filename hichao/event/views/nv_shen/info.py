# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.util.pack_data import pack_data
from hichao.event.models.db import dbsession_generator
from hichao.event.models.nv_shen.user_new import (
        NvShenUserNew,
        get_nv_shen_user,
        )
from hichao.event.models.nv_shen.prize_count import (
        NvShenPrizeCount,
        get_today_prize_count,
        get_all_prize_count,
        )
from hichao.event.models.nv_shen.prize_new import (
        NvShenPrizeNew,
        get_today_users,
        get_prize_info,
        )
from hichao.user.models.user import get_user_by_id
from random import randint
from sqlalchemy import func
import datetime

@view_defaults(route_name = 'event_nv_shen_info')
class NvShenInfoView(View):
    def __init__(self, request):
        super(NvShenInfoView, self).__init__()
        self.request = request

    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        users = get_today_users()
        items = []
        for user_id in users:
            item = {}
            user = get_user_by_id(user_id)
            if not user: continue
            info = get_prize_info(user_id)
            if not info: continue
            user_info = get_nv_shen_user(user_id)
            if not user_info: continue
            alipay = user_info.alipay
            item['username'] = user.get_component_user_name()
            item['alipay'] = '{0}xxxx{1}'.format(alipay[:3], alipay[-3:])
            item['price'] = str(info.price)
            items.append(item)
        cnt = get_today_prize_count()
        total = get_all_prize_count()
        return u'', {'users':items, 'count':str(cnt), 'all_count':str(total)}

    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        if self.user_id <= 0:
            return u'获取用户信息失败，请重新登录。', {'result':'0'}
        try:
            DBSession = dbsession_generator()
            today = datetime.datetime.now().date()
            ts_today = today.strftime('%Y-%m-%d')
            result = 0
            left_time = 0
            prize = DBSession.query(NvShenPrizeNew).filter(NvShenPrizeNew.user_id == self.user_id).filter(NvShenPrizeNew.create_ts >= ts_today).first()
            prize_count = DBSession.query(NvShenPrizeCount).filter(NvShenPrizeCount.user_id == self.user_id).filter(NvShenPrizeCount.create_ts >= ts_today).first()
            if not prize_count:
                prize_count = NvShenPrizeCount(self.user_id, lottery_count = 3, is_win = 0)
            if prize_count.lottery_count < 1:
                DBSession.commit()
                return u'今天的抽奖次数已经用完了哦。', {'result':'0', 'left_time':str(left_time), 'price':'0'}
            if prize:
                prize_count.lottery_count = prize_count.lottery_count - 1
                left_time = prize_count.lottery_count
                DBSession.add(prize_count)
                DBSession.commit()
                return u'', {'result':'1', 'left_time':str(left_time), 'price':'0'}
            res = randint(1, 100)
            result = 0
            price = 0
            if res < 3:
                x = randint(6, 195)
                if x < 6:
                    cnt = DBSession.query(func.count(NvShenPrizeNew.id)).filter(NvShenPrizeNew.price == 100).filter(NvShenPrizeNew.create_ts >= ts_today).filter(NvShenPrizeNew.review ==1).first()
                    if not cnt: cnt = 0
                    else: cnt = cnt[0]
                    if cnt > 4: result = 0
                    else: result = 1
                    price = 100
                elif x > 5 and x < 16:
                    cnt = DBSession.query(func.count(NvShenPrizeNew.id)).filter(NvShenPrizeNew.price == 50).filter(NvShenPrizeNew.create_ts >= ts_today).filter(NvShenPrizeNew.review ==1).first()
                    if not cnt: cnt = 0
                    else: cnt = cnt[0]
                    if cnt > 9: result = 0
                    else: result = 1
                    price = 50
                elif x > 15 and x < 46:
                    cnt = DBSession.query(func.count(NvShenPrizeNew.id)).filter(NvShenPrizeNew.price == 20).filter(NvShenPrizeNew.create_ts >= ts_today).filter(NvShenPrizeNew.review ==1).first()
                    if not cnt: cnt = 0
                    else: cnt = cnt[0]
                    if cnt > 29: result = 0
                    else: result = 1
                    price = 20
                elif x > 45 and x < 96:
                    cnt = DBSession.query(func.count(NvShenPrizeNew.id)).filter(NvShenPrizeNew.price == 10).filter(NvShenPrizeNew.create_ts >= ts_today).filter(NvShenPrizeNew.review ==1).first()
                    if not cnt: cnt = 0
                    else: cnt = cnt[0]
                    if cnt > 49: result = 0
                    else: result = 1
                    price = 10
                elif x > 95:
                    cnt = DBSession.query(func.count(NvShenPrizeNew.id)).filter(NvShenPrizeNew.price == 5).filter(NvShenPrizeNew.create_ts >= ts_today).filter(NvShenPrizeNew.review ==1).first()
                    if not cnt: cnt = 0
                    else: cnt = cnt[0]
                    if cnt > 99: result = 0
                    else: result = 1
                    price = 5
            prize_count.lottery_count = prize_count.lottery_count - 1
            left_time = prize_count.lottery_count
            if result:
                prize_count.is_win = 1
                prize = NvShenPrizeNew(price, self.user_id)
                DBSession.add(prize)
            DBSession.add(prize_count)
            DBSession.commit()
            if result:
                return u'', {'result':'1', 'left_time':str(left_time), 'price':str(price)}
            else:
                return u'', {'result':'1', 'left_time':str(left_time), 'price':'0'}
        except Exception, ex:
            print Exception, ex
            DBSession.rollback()
            return u'>_< 出错了，再试试看。', {'result':'0'}
        finally:
            DBSession.close()
            if result: get_today_users(use_cache = False)

@view_defaults(route_name = 'event_nv_shen_check_order')
class NvShenCheckOrderView(View):
    def __init__(self, request):
        super(NvShenCheckOrderView, self).__init__()
        self.request = request

    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        if self.user_id <= 0:
            return u'获取用户信息失败，请重新登录。', {'result':'0'}
        order_id = self.request.params.get('order_id', '')
        if not order_id:
            return u'请输入订单号！', {'result':'0'}
        try:
            cnt = get_today_prize_count()
            if cnt >= 100:
                return u'今天的奖品已经被领完了哦。', {'result':'0'}
            DBSession = dbsession_generator()
            order = DBSession.query(NvShenOrder).filter(NvShenOrder.order_id == order_id).filter(NvShenOrder.is_active == 1).first()
            if not order:
                DBSession.commit()
                #return u'无效的订单号！', {'result':'0'}
                return u'', {'result':'1'}
            if order.lottery_count < 1:
                DBSession.commit()
                return u'该订单号已经抽过奖了哦。', {'result':'0'} 
            return u'可以开始抽奖了哦~', {'result':'1'}
        except Exception, ex:
            print Exception, ex
            DBSession.rollback()
            return u'', {'result':'0'}
        finally:
            DBSession.close()

@view_defaults(route_name = 'event_nv_shen_user_info')
class NvShenUserInfoView(View):
    def __init__(self, request):
        super(NvShenUserInfoView, self).__init__()
        self.request = request

    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        if self.user_id <= 0:
            return u'获取用户信息失败，请重新登录。', {'result':'0'}
        try:
            today = datetime.datetime.now().date()
            ts_today = today.strftime('%Y-%m-%d')
            DBSession = dbsession_generator()
            user = get_nv_shen_user(self.user_id)
            if not user:
                DBSession.commit()
                return u'您还没有领取女神券哦。', {'result':'0', 'left_time':'0'}
            prize_count = DBSession.query(NvShenPrizeCount).filter(NvShenPrizeCount.user_id == self.user_id).filter(NvShenPrizeCount.create_ts >= ts_today).first()
            if not prize_count:
                DBSession.commit()
                return u'', {'result':'1', 'left_time':'3', 'alipay':user.alipay}
            left_time = prize_count.lottery_count
            DBSession.commit()
            return u'', {'result':'1', 'left_time':str(left_time), 'alipay':user.alipay}
        except Exception, ex:
            print Exception, ex
            DBSession.rollback()
            return u'出错了，再试一下吧。', {'result':'0', 'left_time':'0', }
        finally:
            DBSession.close()

    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        return '', {}
        if self.user_id <= 0:
            return u'获取用户信息失败，请重新登录。', {'result':'0'}
        order_id = self.request.params.get('order_id', '')
        if not order_id:
            return u'请输入订单号！', {'result':'0'}
        alipay = self.request.params.get('alipay', '')
        if not alipay:
            return u'请输入您的手机号。', {'result':'0'}
        try:
            DBSession = dbsession_generator()
            prize_user = DBSession.query(NvShenPrize).filter(NvShenPrize.order_id == order_id).first()
            if not prize_user:
                DBSession.commit()
                return u'该订单号没有中奖哦。', {'result':'0'}
            elif int(prize_user.user_id) != int(self.user_id):
                return u'该订单关联的账户与您的账户不匹配。', {'result':'0'}
            else:
                prize_user.alipay = alipay
                DBSession.add(prize_user)
                DBSession.commit()
                return u'', {'result':'1'}
        except Exception, ex:
            print Exception, ex
            DBSession.rollback()
            return u'出错了！请重新提交。', {'result':'0'}
        finally:
            DBSession.close()


