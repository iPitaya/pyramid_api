
# -*- coding: utf-8 -*-

import string
from datetime import datetime

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.renderers import render_to_response

from icehole_client.goods_manager_client import Client as Goods
from icehole_client.points_manager_client import Client as Points
from icehole_client.throne_client import ThroneClient
from icehole_interface.points.base import ttypes
from hichao.user.models.user import (
        get_user_info,
        get_user_by_id,
        update_user_info,
        update_user_location,
        )
from hichao.base.config.CDN import generate_fast_dfs_image_prefix
from hichao.base.views.view_base import View 

from hichao.util.statsd_client import timeit 
from hichao.app.views.oauth2 import check_permission 

g_order = ttypes.Sort()
g_result = ttypes.Result()
g_goods_status = ttypes.GoodsStatus()
g_activity = ttypes.Activity()
g_period_activity = ttypes.PeriodActivity()
timer = timeit('hichao_backend.points_system')

@view_defaults(route_name='points_system')
class PointsSystemViews(View):
    def __init__(self, request):
        super(PointsSystemViews, self).__init__()
        self.request = request

    @check_permission
    @view_config(match_param='fizzle=home',\
        request_method = 'GET',\
        renderer='points_system/home.html')
    def HomeView(self):
        self.reward_attendance()
        rv = self.get_home()
        self.set_access_token(rv)
        return rv

    @check_permission
    @view_config(match_param='fizzle=home_activity',\
        request_method = 'GET',\
        renderer='json')
    def HomeActivityView(self):
        rv = self.get_home_activity()
        #self.set_access_token(rv)
        return rv

    @check_permission
    @view_config(match_param='fizzle=payments_list',\
        request_method = 'GET',\
        renderer='points_system/payments_list.html')
    def PaymentsListView(self):
        rv = self.get_payments_list()
        self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=payments_list/data',\
        request_method = 'GET',\
        renderer='json')
    def PaymentsListData(self):
        rv = self.get_payments_list()
        self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=goods_list',\
        request_method = 'GET',\
        renderer='points_system/goods_list.html')
    def GoodsListView(self):
        dict_points = self.get_user_points()
        dict_goods = self.get_goods_list()
        rv = dict(dict_points.items() + dict_goods.items())
        self.set_access_token(rv)
        return rv

    @check_permission
    @view_config(match_param='fizzle=points',\
        request_method = 'GET', renderer='json')
    def PointsView(self):
        rv = self.get_user_points()
        #self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=goods_list/data',\
        request_method = 'GET', renderer='json')
    def GoodsListData(self):
        rv = self.get_goods_list()
        self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=order_list',\
        renderer='points_system/order_list.html')
    def OrderListView(self):
        handler_dict = dict()
        rv = self.get_order_list()
        self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=order_list/data',\
        request_method = 'GET', renderer='json')
    def OrderListData(self):
        rv = self.get_order_list()
        self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=goods',\
        request_method='GET',\
        renderer='points_system/goods.html')
    def GoodsView(self):
        rv = self.get_goods()
        self.set_access_token(rv)
        return rv

    @check_permission
    @view_config(match_param='fizzle=address',\
        request_method = 'POST',\
        renderer='points_system/order.html')
    @view_config(match_param='fizzle=order',\
        request_method = 'GET',\
        renderer='points_system/order.html')
    def OrderView(self):
        rv = dict()
        if self.request.method == 'POST':
            self.post_address()
        dict_address = self.get_address_base_info()
        dict_goods = self.get_goods_base_info()
        rv = dict(dict_address.items() + dict_goods.items())
        self.set_access_token(rv)
        return rv
    
    @check_permission
    @view_config(match_param='fizzle=order_result')
    def OrderResultView(self):
        access_token = self.request.params.get('access_token', '')
        access_token = self.access_token if len(self.access_token) \
            else self.request.headers.get('Access-Token','')
        rv = {'access_token':access_token}
        cond = string.atoi(self.request.params.get('result', '0'))
        result = None
        print 'result = ', cond
        if cond == 1:
            res = self.post_order()
            if res == g_result.Successful:
                result = render_to_response('points_system/msg_order_success.html',
                    rv, request=self.request)
            elif res == g_result.MorePointsIsRequired:
                result = render_to_response('points_system/msg_order_failed.html',
                    rv, request=self.request)
            else:
                print '************************** 其他原因导致购买失败 *****************************'
                pass
        elif cond == 0:
            result = render_to_response('points_system/msg_order_failed.html',
                rv, request=self.request)
        return result

    @check_permission
    @view_config(match_param='fizzle=address',\
        request_method = 'GET',\
        renderer='points_system/address.html')
    def AddressView(self):
        rv = self.get_address()
        self.set_access_token(rv)
        return rv

    @check_permission
    @view_config(match_param='fizzle=complete_data',\
        request_method = 'GET',\
        renderer='points_system/complete_data.html')
    def CompleteDataView(self):
        rv = self.get_improve_rule_desc()
        self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=DailyActiveTalent',\
        request_method = 'GET',\
        renderer='points_system/DailyActiveTalent.html')
    def DailyActiveTalentView(self):
        rv = self.get_period_activity_rule_desc()
        self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=DailyCreateThread',\
        request_method = 'GET',\
        renderer='points_system/DailyCreateThread.html')
    def DailyCreateThreadView(self):
        rv = self.get_period_activity_rule_desc()
        self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=DailyReplyThread', \
        request_method = 'GET', \
        renderer='points_system/DailyReplyThread.html')
    def DailyReplyThreadView(self):
        rv = self.get_period_activity_rule_desc()
        self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=DailyTopicSelected', \
        request_method = 'GET', \
        renderer='points_system/DailyTopicSelected.html')
    def DailyTopicSelectedView(self):
        rv = self.get_period_activity_rule_desc()
        self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=DailyTopicInForumHome', \
        request_method = 'GET', \
        renderer='points_system/DailyTopicInForumHome.html')
    def DailyTopicInForumHomeView(self):
        rv = self.get_period_activity_rule_desc()
        self.set_access_token(rv)
        return rv
 
    @check_permission
    @view_config(match_param='fizzle=DailyToipcInAppHomeDrop', \
        request_method = 'GET', \
        renderer='points_system/DailyToipcInAppHomeDrop.html')
    def DailyToipcInAppHomeDropView(self):
        rv = self.get_period_activity_rule_desc()
        self.set_access_token(rv)
        return rv

    @timer
    def get_goods(self):
        request = self.request
        goods_id = string.atoi(request.params.get('goods_id', '0'))
        goods = Goods()
        res = goods.GetGoodsList([goods_id])
        rv = dict()
        if len(res) != 0:
            res[0].points_price = int(res[0].points_price)
            res[0].image_url = generate_fast_dfs_image_prefix()\
                + res[0].image_url 
            res[0].multi_images = goods.GetGoodsMultiImages(res[0].source,\
                res[0].source_id)
            for item in res[0].multi_images:
                item.url = generate_fast_dfs_image_prefix() + item.url
            rv = {'goods':res[0]}
            rv['remain'] = res[0].inventory - res[0].shipment
        else:
            rv = {'goods':None}
        return rv

    def get_address_base_info(self):
        goods_id = string.atoi(self.request.params.get('goods_id', '0'))
        res = Goods().GetUser(int(self.user_id))
        user = {'points':res.points,
                'addressee':res.addressee,
                'phone':res.phone,
                'address':res.address}
        rv = {'user':user}
        return rv

    def get_goods_base_info(self):
        request = self.request
        goods_id = string.atoi(request.params.get('goods_id', '0'))
        goods = Goods()
        res = goods.GetGoodsList([goods_id])
        rv = dict()
        if len(res) != 0:
            make_image_url = lambda x: generate_fast_dfs_image_prefix() + \
                x.image_url + '?imageMogr2/thumbnail/!60p/quality/50'
            goods = {'id':res[0].id,
                     'title':res[0].title,
                     'points_price':int(res[0].points_price),
                     'remain': res[0].inventory - res[0].shipment,
                     'image_url':make_image_url(res[0])}
            rv = {'goods':goods}
        else:
            rv = {'goods':None}
        return rv

    @timer
    def get_payments_list(self):
        request = self.request
        user_id = self.user_id
        offset = string.atoi(request.params.get('offset', '0'))
        limit = string.atoi(request.params.get('limit', '0'))
        points_client = Points()
        id_list = points_client.GetPaymentsRecordIdList(user_id, offset, limit)
        if len(id_list) == 0:
            return {'payments_list':[]}
        res = points_client.GetPaymentsRecordList(user_id, id_list)
        if len(res) == 0:
            return {'payments_list':[]}

        data = list()

        def make_image_url(x):
            if len(x.image_url) == 0:
                return x.image_url
            if x.activity == g_activity.Shopping: 
                return generate_fast_dfs_image_prefix() + x.image_url + \
                '?imageMogr2/thumbnail/!40p/quality/50' 
            else:
                return generate_fast_dfs_image_prefix() + x.image_url
                
        data.extend([{'date':datetime\
                         .strptime(item.record_date,'%Y-%m-%d %H:%M:%S')\
                         .date()\
                         .strftime("%Y-%m-%d"),
                     'points':int(item.points),
                     'image_url':make_image_url(item),
                     'description':item.description}\
                     for item in res])
        rv = {'payments_list':data}
        return rv
    
    @timer
    def get_goods_list(self):
        request = self.request
        offset = string.atoi(request.params.get('offset', '0'))
        limit = string.atoi(request.params.get('limit', '0'))
        goods = Goods()
        id_list = goods.GetGoodsIdListByOnsaleDate(offset, limit, g_order.DESC)
        if len(id_list) == 0:
            return {'goods_list':[]}
        res = goods.GetGoodsList(id_list)
        if len(res) == 0:
            return {'goods_list':[]}
        data = list()
        for item in res:
            data.append({'id':item.id,
                         'title':item.title,
                         'source':item.source,
                         'inventory':item.inventory,
                         'remain':item.inventory - item.shipment,
                         'points_price':int(item.points_price),
                         'image_url':\
                             generate_fast_dfs_image_prefix() + \
                             item.image_url})
        rv = {'goods_list':data}
        return rv
    
    @timer
    def get_order_list(self):
        request = self.request
        user_id = self.user_id
        offset = string.atoi(request.params.get('offset', '0'))
        limit = string.atoi(request.params.get('limit', '0'))
        goods = Goods()
        id_list = goods.GetGoodsOrderIdListByDate(user_id, \
            offset, limit, g_order.DESC)
        if len(id_list) == 0:
            return {'order_list':[]}
        res = goods.GetGoodsOrderList(id_list)
        if len(res) == 0:
            return {'order_list':[]}
        data = list()
        status_desc = None
        for item in res:
            if item.status == 0:
                status_desc = u'已提交'
            elif item.status == 1:
                status_desc = u'已发货（请注意查收）'
            data.append({'id':item.id,
                         'status':item.status,
                         'status_desc':status_desc,
                         'points':int(item.points),
                         'goods_title':item.goods_title,
                         'goods_image_url':\
                             generate_fast_dfs_image_prefix() + \
                             item.goods_image_url})
        rv = {'order_list':data, 'user_id':user_id}
        return rv
    
    @timer
    def get_user_points(self):
        request = self.request
        user_id = self.user_id
        if user_id <= 0:
            return {'points': 0}
        res = Points().GetPoints(user_id)
        res = int(res)
        rv = {'points':res}
        return rv
    
    @timer
    def get_address(self):
        goods_id = string.atoi(self.request.params.get('goods_id', '0'))
        res = Goods().GetUser(int(self.user_id))
        rv = {'data':res, 'goods_id':goods_id}
        return rv
    
    @timer
    def post_address(self):
        request = self.request
        user_id = self.user_id
        rv = g_result.Successful
        goods_client = Goods()
        res = goods_client.GetUser(user_id)
        res.addressee = request.params.get('addressee', '').encode('utf-8')
        res.phone     = request.params.get('phone', '')
        res.zip_code  = string.atoi(request.params.get('zip_code', '0'))
        res.address   = request.params.get('address', '').encode('utf-8')
        rv = goods_client.UpdateUser(res)
        if rv != g_result.Successful:
            #todo: error log here
            pass
        return rv

    @timer
    def post_order(self):
        request = self.request
        user_id = self.user_id
        rv = g_result.Successful
        goods_id = string.atoi(request.params.get('goods_id', '0'))
        goods_num = string.atoi(request.params.get('goods_num', '0'))
        print 'goods_id =', goods_id
        print 'goods_num =', goods_num
        goods_client = Goods()
        try:
            rv = goods_client.InsertGoodsOrder(user_id, goods_id, goods_num)
        except Exception, e:
            print Excpetion, ':', e
        if rv != g_result.Successful:
            #todo: error log here
            pass
        return rv
    
    @timer
    def reward_attendance(self):
        request = self.request
        user_id = self.user_id
        attend = string.atoi(request.params.get(u'attend', '0'))
        res = None
        if attend == 1:
            res = Points().RewardPeriod(user_id, \
                g_period_activity.DailyAttendance)
            print 'res =', res
        
    @timer
    def get_home(self):
        print self.request
        request = self.request
        user_id = self.user_id
        rv = dict()
        if not user_id or user_id == 0:
            #todo: error log here
            return rv
        user = get_user_by_id(user_id)
        if not user:
            #todo: error log here
            return rv
        rv['user_name'] = user.get_component_user_name()
        rv['user_avatar'] = user.get_component_user_avatar()
        points_client = Points()
        res_points = points_client.GetPoints(user_id)
        rv['user_id'] = user_id
        rv['user_points'] = int(res_points)
        res_improve = points_client.GetImproveRewardingRecord(user_id)
        res_improve.points = int(res_improve.points)
        res_improve.points_limit = int(res_improve.points_limit)
        rv['ImproveRewarding'] = res_improve
        res_period = points_client.GetPeriodRewardingRecordList(user_id)
        for item in res_period:
            item.points = int(item.points)
            item.points_single = int(item.points_single)
            item.points_limit = int(item.points_limit)
            item.period_activity = int(item.period_activity)
            rv[g_period_activity._VALUES_TO_NAMES[item.period_activity]] = item
        return rv

    def get_improve_rewarding_record(self):
        points_client = Points()
        res = points_client.GetImproveRewardingRecord(self.user_id)
        res.points = int(res.points)
        res.points_limit = int(res.points_limit)
        rv = {'activity_id':0,
              'points':res.points,
              'points_single':res.points_limit,
              'points_limit':res.points_limit}
        return rv

    def get_period_activity_rewarding_record(self, period_activity):
        points_client = Points()
        res = points_client.GetPeriodRewardingRecord(self.user_id,\
            period_activity)
        res.points = int(res.points)
        res.points_single = int(res.points_single)
        res.points_limit = int(res.points_limit)
        res.period_activity = int(res.period_activity)
        rv = {'activity_id': res.period_activity,
              'points':res.points,
              'points_single':res.points_single,
              'points_limit':res.points_limit}
        return rv

    @timer
    def get_home_activity(self):
        rv = dict()
        id = self.request.params.get('activity_id', '-1')
        id = int(id)
        if id == 0:
            rv = self.get_improve_rewarding_record()
        elif id > 0 and id < g_period_activity.Unknown:
            rv = self.get_period_activity_rewarding_record(id)
        return rv
    
    @timer
    def get_improve_rule_desc(self):
        request = self.request
        points = string.atoi(request.params.get('points', '0'))
        points_single = string.atoi(request.params.get('points_limit', '0'))
        points_limit = string.atoi(request.params.get('points_limit', '0'))
        times_current = points/points_single
        times_limit = points_limit/points_single
        rv = {'times_current':times_current,
              'times_limit':times_limit,
              'points':points}
        return rv

    @timer   
    def get_period_activity_rule_desc(self):
        request = self.request
        points = string.atoi(request.params.get('points', '0'))
        points_single = string.atoi(request.params.get('points_single', '0'))
        points_limit = string.atoi(request.params.get('points_limit', '0'))
        times_current = points/points_single
        times_limit = points_limit/points_single
        rv = {'points':points,
              'times_current':times_current,
              'times_limit':times_limit}
        return rv

    def set_access_token(self, rv):
        rv['access_token'] = self.access_token.encode('utf-8')
