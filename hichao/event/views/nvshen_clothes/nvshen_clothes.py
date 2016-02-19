# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.event.models.db import (
        dbsession_generator,
        dbsession_generator_write,
        shop_dbsession_generator,
        )
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.util.pack_data import pack_data
from hichao.event.models.nvshen_activity.goddess_record import (
    have_chance_for_prize,
    get_left_times_by_user_id,
    )
from hichao.user.models.user import get_user_by_id
from hichao.event.models.nvshen_activity.goddess_prize  import (
    get_all_prize_ids,
    get_prize_by_id,
    has_prize_left,
    get_prize_type_by_id, 
    had_not_won_big_prize,
    GoddessPrize,
    get_prize_by_rate,
    )

from hichao.event.models.nvshen_activity.goddess_winner import (
    GoddessWinner,
    add_winner,
    get_winner_by_use_id,
    get_today_winners_by_taday_time,
    get_all_winner_count,
    get_all_winners,
    )
from hichao.event.models.nvshen_activity.shop_user import get_id_by_name
from pyramid.response import Response
import json
from hichao.event.models.nvshen_activity.shop_user_coupon import add_coupon_to_user
from hichao.event.models.nvshen_activity.shop_user_bonus import add_bonus_to_user
from hichao.cache.cache import deco_cache
from random import randint, choice, shuffle
import datetime,time
from hichao.util.date_util import HOUR
from hichao.util.statsd_client import statsd
import json
import requests
from hichao.base.config import PROMOTE_URL

def get_prize_rate_list(todaytime):
    prize_ids = get_all_prize_ids(todaytime, use_cache = True)
    for index, prize_id in enumerate(prize_ids):
        if not has_prize_left(prize_id,todaytime):
            del prize_ids[index]
    prize_list1 = []
    prize_list2 = []
    prize_list3 = []
    for prize_id in prize_ids:
        print prize_ids
        prize = get_prize_by_id(prize_id, use_cache = True)
        if prize.prize_type == 1:
            prize_list1.append(prize)
        elif prize.prize_type == 2:
            prize_list2.append(prize)
        else:
            prize_list3.append(prize)
    return prize_list1,prize_list2,prize_list3

@statsd.timer('hichao_backend.r_goddess_clothes_patronize')
def goddess_clothes_patronize(user_id):
    today = datetime.date.today().strftime('%Y-%m-%d %H:%M:%S')
    today_time= datetime.datetime.strptime(today, "%Y-%m-%d %H:%M:%S")
    prize_list1,prize_list2,prize_list3 = get_prize_rate_list(today_time)
    sum_num = 0
    '''
    if len(prize_list1) > 0:
        if had_not_won_big_prize(user_id):
            luck_num = randint(1,1000)
            for prize in prize_list1:
                sum_num = sum_num + prize.rate*1000
                if sum_num >= luck_num:
                    if has_prize_left(prize.id,today_time):
                        return prize
    '''
    list_prize = prize_list2+prize_list3
    if len(list_prize) > 0 :
        if len(list_prize) == 5:
            res = randint(1,120)
            if res >0 and res < 41:
                prize_type = 2
                rate = 40
                prize = get_prize_by_rate(prize_type, rate, today_time, use_cache=True)
            elif res > 40 and res < 61:
                prize_type = 2
                rate = 20
                prize = get_prize_by_rate(prize_type, rate, today_time, use_cache=True)
            elif res > 60 and res < 83:
                prize_type = 3
                rate = 22
                prize = get_prize_by_rate(prize_type, rate, today_time, use_cache=True)
            elif res > 82 and res < 103:
                prize_type = 3
                rate = 20
                prize = get_prize_by_rate(prize_type, rate, today_time, use_cache=True)
            elif res > 102:
                prize_type = 3
                rate = 18
                prize = get_prize_by_rate(prize_type, rate, today_time, use_cache=True)
            if has_prize_left(prize.id,today_time):
                return prize
        else:
            rate = 0
            for prize in list_prize:
                if prize.rate > rate:
                    rate = prize.rate
            res = randint(1,rate)
            shuffle(list_prize)
            for prize in list_prize:
                sum_num = sum_num + prize.rate
                if sum_num >= res:
                    if has_prize_left(prize.id,today_time):
                        return prize
    return 0

@view_defaults(route_name = 'goddess_clothes_lefttime')
class GoddessClothesLeftTime(View):
    def __init__(self, request):
        super(GoddessClothesLeftTime, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_goddess_clothes_lefttime.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        user_id = self.user_id
        if int(user_id)<1:
            self.error['error'] = 'user is not login.'
            self.error['errorCode'] = '20001'
            return Response(json.dumps(self.error ), content_type = 'application/json')
        try:
            com = {}
            user = get_user_by_id(user_id)
            com['userId'] = user_id
            username = user.get_component_user_name()
            if len(username)>10:
                username = username[:10]
            com['userName'] = username
            com['userAvatar'] = user.get_component_user_avatar()
            com['access_token'] = self.request.params.get("access_token")
            todaytime = datetime.datetime.now()
            today = todaytime.date()
            '判断用户每天抽奖次数'
            com['lefttimes'] = get_left_times_by_user_id(user_id,today,use_cache=True)
        except Exception,ex:
            print Exception,ex
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
        return '',com

@view_defaults(route_name = 'goddess_clothes_luck')
class GoddessClothesLuck(View):
    def __init__(self, request):
        super(GoddessClothesLuck, self).__init__()
        #request.response.headerlist.append(('Access-Control-Allow-Origin', '*'))
        self.request = request

    @statsd.timer('hichao_backend.r_goddess_clothes_luck.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        user_id = self.user_id
        if int(user_id)<1:
            self.error['error'] = 'user is not login.'
            self.error['errorCode'] = '20001'
            return Response(json.dumps(self.error ), content_type = 'application/json')
        try:
            com = {}
            dbsession = dbsession_generator()
            dbsession_write = dbsession_generator_write()
            shop_dbsession = shop_dbsession_generator()
            com['userId'] = user_id
            com['access_token'] = self.request.params.get("access_token")
            todaytime = datetime.datetime.now()
            today = todaytime.date()
            #判断抽奖机会是否已经用完，用完了就返回零，否则操作成功，返回1
            has = have_chance_for_prize(user_id,todaytime,dbsession_write)
            if has == 0:
                dbsession.commit()
                dbsession.close()
                com['lefttimes'] = get_left_times_by_user_id(user_id, today, use_cache=False)
                return u'今天的抽奖次数用完了哦',com
            prize = goddess_clothes_patronize(user_id)
            if not prize:
                dbsession.commit()
                dbsession.close()
                com['prize_args'] = 6
                com['lefttimes'] = get_left_times_by_user_id(user_id, today, use_cache=False)
                return u'哎呀，没有机会了，明天再来吧！',com
            else:
                #winner表添加字段
                _prize_id = prize.id
                _user_id = user_id
                _ts = todaytime
                _status = 0
                code = 1
                _remarks = 'goddess_clothes'
                one_winner = GoddessWinner(_prize_id,_user_id,_ts,_status,_remarks)
                add_winner(one_winner,dbsession_write)
                if prize.prize_type == 2:
                    #将红包写入商城红包表  
                    virtual_money_id =int(prize.get_virtual_money_id())
                    if virtual_money_id:
                        code = add_to_user(virtual_money_id, com['access_token'], type='bonus')
                elif prize.prize_type == 3:
                    #将优惠券写入商城优惠券表  
                    virtual_money_id = int(prize.get_virtual_money_id())
                    if virtual_money_id:
                        code = add_to_user(virtual_money_id, com['access_token'], type='promote')
                if code == 1:
                    dbsession.rollback()
                    com['prize_args'] = 6
                    com['lefttimes'] = get_left_times_by_user_id(user_id, today, use_cache=False)
                    return u'哎呀，没有机会了，明天再来吧！',com
                dbsession_write.commit()
                #返回数据
                prize_args = 6
                if prize.prize_type == 1:
                    prize_args = 2
                if prize.prize_type == 2:
                    if prize.rate == 40:
                        prize_args = 0
                    elif prize.rate == 20:
                        prize_args = 4 
                if prize.prize_type == 3:
                    if prize.rate == 22:
                        prize_args = 1
                    elif prize.rate == 18:
                        prize_args = 3
                    elif prize.rate == 20:
                        prize_args = 5
                com['prize_args'] = prize_args
                com['lefttimes'] = get_left_times_by_user_id(user_id, today, use_cache=False)
            return '',com
        except Exception,ex:
            dbsession_write.rollback()
            print Exception,ex
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return '',com
        finally:
            dbsession.close()
            dbsession_write.close()
            shop_dbsession.close()
            
@view_defaults(route_name = 'goddess_clothes_winners_list')
class GoddessClothesWinnersList(View):
    def __init__(self, request):
        super(GoddessClothesWinnersList, self).__init__()
        #request.response.headerlist.append(('Access-Control-Allow-Origin', '*'))
        self.request = request

    @statsd.timer('hichao_backend.r_goddess_clothes_winner_list.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self): 
        today_time = datetime.datetime.now()  
        data = {}
        data['sum_winners'] = get_all_winner_count()
        data['today_winners'] = get_today_winners_by_taday_time(today_time)
        data['items'] = []
        winners_list = get_all_winners() 
        for winner in winners_list:
            com = {}
            if winner:
                user = get_user_by_id(winner.get_winner_use_id())
                prize= get_prize_by_id(winner.get_winner_prize_id())
            if user:
                username = user.get_component_user_name()
                com['userId'] = user.id
            if len(username)>10:
                username = username[:10]
            com['userName'] = username
            if prize:
                com['prizeName'] = prize.get_prize_name()     
            data['items'].append(com) 
        return '',data


def add_to_user(id, access_token, type):
    url = PROMOTE_URL
    query = {}
    query['promote_ids'] = id
    query['token'] = access_token
    query['type'] = type
    query['isDisplay'] = 0
    try:
        rt = requests.post(url,query)
        result = json.loads(rt.content)
        if result:
            code = int(result['response']['code'])
            message = result['response']['msg']
    except Exception, e:
        print e
        code = 1
        message = 'fail'
    return code
