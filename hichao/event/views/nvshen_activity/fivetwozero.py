# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.event.models.db import (
        dbsession_generator,
        shop_dbsession_generator,
        )
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.util.pack_data import pack_data
from hichao.event.models.nvshen_activity.goddess_record import (
    have_chance_for_prize,
    get_left_times_by_user_id,
    get_record_by_user_id,
    get_number_record,
    add_record,
    update_record,
    reduce_times,
    )
from hichao.user.models.user import get_user_by_id
from hichao.event.models.nvshen_activity.goddess_prize  import (
    get_all_prize_ids,
    get_prize_by_id,
    has_prize_left,
    get_prize_type_by_id, 
    had_not_won_big_prize,
    )
from hichao.event.models.nvshen_activity.goddess_winner import (
    GoddessWinner,
    add_winner,
    get_all_winner_ids,
    get_winner_by_id,
    get_winner_by_use_id,
    )
from hichao.event.models.nvshen_activity.shop_user import get_id_by_name
from pyramid.response import Response
import json
from hichao.event.models.nvshen_activity.shop_user_coupon import add_coupon_to_user
from hichao.event.models.nvshen_activity.shop_user_bonus import add_bonus_to_user
from hichao.cache.cache import deco_cache
from random import randint
import datetime,time
from hichao.util.date_util import HOUR
from hichao.util.statsd_client import statsd

@deco_cache(prefix='prize_rate_list', recycle=HOUR)
def get_prize_rate_list(today_time):
    prize_ids = get_all_prize_ids(today_time)
    prize_list1 = []
    prize_list2 = []
    prize_list3 = []
    for prize_id in prize_ids:
        prize = get_prize_by_id(prize_id)
        if prize.prize_type ==1:
            prize_list1.append(prize)
        elif prize.prize_type == 2:
            prize_list2.append(prize)
        else:
            prize_list3.append(prize)
    return prize_list1,prize_list2,prize_list3

@statsd.timer('hichao_backend.r_goddess_patronize')
def goddess_patronize(user_id):
    today_time = datetime.datetime.now()    
    prize_list1,prize_list2,prize_list3 = get_prize_rate_list(today_time)
    sum_num = 0
    if had_not_won_big_prize(user_id):
        luck_num = randint(1,10000)
        for prize in prize_list1:
            sum_num = sum_num +prize.rate*100
            if sum_num >= luck_num:
                if has_prize_left(prize.id,today_time):                
                    return prize
    luck_num = randint(1,2)
    sum_num = 0
    if luck_num==1:
        luck_num = randint(1,100)
        for prize in prize_list2:
            sum_num = sum_num +prize.rate
            if sum_num >= luck_num:
                if has_prize_left(prize.id,today_time):
                    return prize
    elif luck_num==2:
        luck_num = randint(1,100)
        for prize in prize_list3:
            sum_num = sum_num +prize.rate
            if sum_num >= luck_num:
                if has_prize_left(prize.id,today_time):
                    return prize
    return 0


@view_defaults(route_name = 'luck_homepage')
class GoddessHomePage(View):
    def __init__(self,request):
        super(GoddessHomePage, self).__init__()
        #request.response.headerlist.append(('Access-Control-Allow-Origin', '*'))
        self.request = request
    
    @statsd.timer('hichao_backend.r_goddess_homepage.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        num = get_number_record()
        com = {}
        com['sumNumber'] = str(1537289 +num)
        access_token= self.request.params.get("access_token")
        if access_token:
            com['access_token'] = access_token
        return '',com
        
        

@view_defaults(route_name = 'luck_draw')
class GoddessLuckDraw(View):
    def __init__(self, request):
        super(GoddessLuckDraw, self).__init__()
        #request.response.headerlist.append(('Access-Control-Allow-Origin', '*'))
        self.request = request

    @statsd.timer('hichao_backend.r_goddess_luck_draw.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'nvshen_activity/prize.html')
    @pack_data
    def post(self):
        user_id = self.user_id
        if int(user_id)<1:
            res = {}
            res['error'] = 'user is not login.'
            res['errorCode'] = '20001'
            res['message'] = ''
            res['data'] = {}
            #res['data']['appApi'] = app_api
            return Response(json.dumps(res), content_type = 'application/json')
        try:
            com = {}
            dbsession = dbsession_generator()
            shop_dbsession = shop_dbsession_generator()
            user = get_user_by_id(user_id)
            com['userId'] = user_id
            username = user.get_component_user_name()
            if len(username)>10:
                username = username[:10]
            com['userName'] = username
            com['userAvatar'] = user.get_component_user_avatar()
            com['access_token'] = self.request.params.get("access_token")
            todaytime = datetime.datetime.now()
            '判断抽奖机会是否已经用完，用完了就返回零，没有用完但是更新record数据库失败，就返回2，否则操作成功，返回1'           
            has = have_chance_for_prize(user_id,todaytime,dbsession)
            if has == 0:
                dbsession.commit()
                dbsession.close()
                com['prizeType'] = 0
                com['lefttimes'] = get_left_times_by_user_id(user_id,todaytime)
                return u'今天的抽奖次数用完了哦',com
            elif has == 2:
                dbsession.rollback()
                dbsession.close()
                com['prizeType'] = 0
                com['lefttimes'] = get_left_times_by_user_id(user_id,todaytime) 
                self.error['error'] = 'Operation failed.'
                self.error['errorCode'] = '30001'               
                return u'今天的抽奖次数用完了哦',com
            prize = goddess_patronize(user_id)
            if not prize:
                dbsession.commit()
                dbsession.close()
                com['prizeType'] = 0
                com['lefttimes'] = get_left_times_by_user_id(user_id,todaytime)
                return u'对不起，你本次抽奖没有中哦，再来一次',com
            else:
                'winner表添加字段'
                _prize_id = prize.id
                _user_id = user_id
                _ts = todaytime
                _status = 0
                one_winner = GoddessWinner(_prize_id,_user_id,_ts,_status)
                add_winner(one_winner,dbsession)
                if prize.prize_type == 2:
                    '将红包写入商城红包表'  
                    today_time =todaytime.strftime("%Y-%m-%d %H:%M:%S")
                    timeArray = time.strptime(today_time, "%Y-%m-%d %H:%M:%S")
                    virtual_money_id =int(prize.get_virtual_money_id())
                    if virtual_money_id:
                        shop_user_id = get_id_by_name(user_id)
                        add_bonus_to_user(virtual_money_id, shop_user_id, timeArray, shop_dbsession)
                elif prize.prize_type == 3:
                    '将优惠券写入商城优惠券表'  
                    today_time =todaytime.strftime("%Y-%m-%d %H:%M:%S")
                    timeArray = time.strptime(today_time, "%Y-%m-%d %H:%M:%S")
                    virtual_money_id = int(prize.get_virtual_money_id())
                    if virtual_money_id:
                        shop_user_id = get_id_by_name(user_id)
                        add_coupon_to_user(virtual_money_id, shop_user_id, timeArray, shop_dbsession)
                dbsession.commit()
                shop_dbsession.commit()
                #返回数据到中奖提示页面               
                com['prizeId'] = prize.get_prize_id()
                com['prizeName'] = prize.get_prize_name()
                com['prizeImage'] = prize.get_prize_image()
                com['prizeType'] = prize.prize_type  #添加一个action
                com['lefttimes'] = get_left_times_by_user_id(user_id,todaytime)
            return '',com
        except Exception,ex:
            dbsession.rollback()
            shop_dbsession.rollback()
            print Exception,ex
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return '',com
        finally:
            dbsession.close()
            shop_dbsession.close()
        
@view_defaults(route_name = 'winners_list')
class GoddessWinnersList(View):
    def __init__(self, request):
        super(GoddessWinnersList, self).__init__()
        #request.response.headerlist.append(('Access-Control-Allow-Origin', '*'))
        self.request = request

    @statsd.timer('hichao_backend.r_goddess_winner_list.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        winner_ids = get_all_winner_ids()
        data = {}
        data['item'] = []
        for winner_id in winner_ids:
            com = {}
            winner = get_winner_by_id(winner_id)
            if winner:
                user = get_user_by_id(winner.get_winner_use_id())
                prize= get_prize_by_id(winner.get_winner_prize_id())
            if user:
                username = user.get_component_user_name()
            if len(username)>10:
                username = username[:10]
            com['userName'] = username
            if prize:
                com['prizeName'] = prize.get_prize_name()
            data['item'].append(com)
        return '',data
        
@view_defaults(route_name = 'update_winner_info')
class GoddessUpdateWinnerinfo(View):
    def __init__(self, request):
        super(GoddessUpdateWinnerinfo, self).__init__()
        #request.response.headerlist.append(('Access-Control-Allow-Origin', '*'))
        self.request = request
    
    @statsd.timer('hichao_backend.r_goddess_winner_info.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        user_id = self.user_id
        if int(user_id)<1:
            self.error['error'] = 'User is not login.'
            self.error['errorCode'] = '20001'
            return u'用户信息获取失败，请登录',{'return':'0'}
        winners = get_winner_by_use_id(user_id)
        if not winners:
            return u'对不起，您没有中奖记录，不需要填写个人信息',{'return':'0'}
        else:
            winner = winners[0]
            com = {}
            com['name'] = winner.name
            com['address'] = winner.address
            com['telephone'] = winner.tel
            com['postcode'] = winner.postcode
            com['access_token'] = self.request.params.get("access_token")
        return '',com
    
    @statsd.timer('hichao_backend.r_goddess_winner_info.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        user_id = self.user_id
        if int(user_id)<1:
            self.error['error'] = 'User is not login.'
            self.error['errorCode'] = '20001'
            return u'用户信息获取失败，请登录',{'return':'0'}
        winners = get_winner_by_use_id(user_id)
        if not winners:
            return u'对不起，您没有中奖记录，不需要填写个人信息',{'return':'0'}
        _name = self.request.params.get("name",'')
        _address = self.request.params.get("address",'')
        #_remarks = self.request.params.get("userRemarks",'')
        _tel = self.request.params.get("telephone",'')
        _postcode = self.request.params.get("postcode",'')
        for winner in winners:
            prize_type = get_prize_type_by_id(winner.get_winner_prize_id())
            if prize_type == 1:
                if _name:
                    winner.name = _name
                if _address:
                    winner.address = _address
                #winner.remarks = _remarks
                if _tel:
                    winner.tel = _tel
                if _postcode and len(_postcode) < 10:
                    winner.postcode = int(_postcode)
                try:
                    dbsession = dbsession_generator()
                    dbsession.add(winner)
                    dbsession.commit()
                except Exception,ex:
                    dbsession.rollback()
                    print Exception,ex
                    self.error['error'] = 'Operation failed.'
                    self.error['errorCode'] = '30001'
                    return u'更新信息失败',{'return':'0'}
            else:
                pass
        "填表之后 有没有表单要处理"
        com = {}
        com['status'] = "success"
        com['access_token'] = self.request.params.get("access_token")
        return '',com
    
@view_defaults(route_name = 'goddess_shared')
class GoddessShared(View):
    def __init__(self, request):
        super(GoddessShared, self).__init__()
        #request.response.headerlist.append(('Access-Control-Allow-Origin', '*'))
        self.request = request
        
    @statsd.timer('hichao_backend.r_goddess_shared.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        user_id = self.user_id
        if int(user_id)<1:
            self.error['error'] = 'User is not login.'
            self.error['errorCode'] = '20001'
            return u'用户信息获取失败，请登录',{'return':'0'}
        try:
            DBSession = dbsession_generator()
            today_time = datetime.datetime.now()
            userrecord = get_record_by_user_id(user_id,today_time)
            if not userrecord:
                userrecord = add_record(user_id,today_time,DBSession,times = 0)
            if not userrecord.shared:
                userrecord.shared = 1
                reduce_times(userrecord,today_time,DBSession)
                DBSession.commit()
                DBSession.close()
                lefttimes = str(get_left_times_by_user_id(user_id,today_time))
                return u"The first shared!",{'lefttimes':lefttimes}
            else:
                lefttimes = str(get_left_times_by_user_id(user_id,today_time))
                return u"shared success!",{'lefttimes':lefttimes}   
        except Exception,ex:
            DBSession.rollback()
            DBSession.close()            
            print Exception,ex
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return u"分享失败!",{'return':'0'}

if __name__ == '__main__':
    today_time = datetime.datetime.now()    
    print has_prize_left(14, today_time)

