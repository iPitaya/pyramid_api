# -*- coding:utf-8 -*-

from pyramid.view import (
    view_defaults,
    view_config,
)
from hichao.base.views.view_base import View
from hichao.base.config import (
    MYSQL_MAX_INT,
    FALL_PER_PAGE_NUM,
)
from hichao.util.pack_data import pack_data
from hichao.forum.models.star_user import get_staruser_ids
from hichao.forum.models.hot_star_user import get_hot_staruser_ids,get_hot_staruser_ids_by_type_id
from hichao.util.object_builder import (
    build_staruser_by_id,
    build_hot_staruser_list_by_id,
    build_staruser_by_user_id,
    build_user_by_user_id,
)
from hichao.util.statsd_client import statsd
from datetime import datetime
import time
from hichao.app.views.oauth2 import check_permission
from hichao.follow.models.follow import get_follow_list_by_user_id,get_fans_list_by_user_id,get_user_follow_status


@view_defaults(route_name='starusers')
class StarUsersView(View):

    def __init__(self, request):
        super(StarUsersView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_starusers.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        flag = int(flag) if flag else 0
        data = {}
        data['items'] = []
        ids = get_staruser_ids(flag, FALL_PER_PAGE_NUM)
        for id in ids:
            com = build_staruser_by_id(id)
            if com:
                data['items'].append(com)
        num = len(ids)
        if num >= FALL_PER_PAGE_NUM:
            data['flag'] = str(flag + num)
        return '', data


@view_defaults(route_name='hot_starusers')
class HotSatrUsersView(View):

    def __init__(self, request):
        super(HotSatrUsersView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_hot_staruser.get')
    @check_permission
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        flag = int(flag) if flag else 0
        type_str = self.request.params.get('type', '')
        '''
        flag = "2015-04-17 23:40:00"
        #flag = time.strftime("%Y-%m-%d %H:%M:%S", flag)
            if not flag:
                flag = datetime.now()
        else:
            flag = datetime.strptime(flag, "%Y-%m-%d %H:%M:%S")
        flag = time.mktime(flag.timetuple())
        flag = "2015-04-19 13:27:00"
        if flag:
            flag = time.strptime(flag, "%Y-%m-%d %H:%M:%S")
            #flag = time.mktime(flag)
        else:
            flag = time.localtime()
        '''
        data = {}
        data['items'] = []
        ids = []
        if not type_str:
            ids = get_hot_staruser_ids(flag,FALL_PER_PAGE_NUM)
        type_id = 0
        if str(type_str) == '3':
            type_id = 2    #红人
        elif str(type_str) == '4':
            type_id = 3    #设计师
        elif str(type_str) == '5':
            type_id = 4    #明星
        if type_id:
            ids = get_hot_staruser_ids_by_type_id(type_id,flag,FALL_PER_PAGE_NUM)
        for id in ids:
            com = build_hot_staruser_list_by_id(id)
            if com:
                isFollow = 0
                if self.user_id:
                    isFollow = get_user_follow_status(self.user_id,com['component']['userId'])
                com['component']['isFollow'] = str(isFollow)
                #com['component']['userTypeName'] = '红人'
                #com['component']['userTypeIcon'] = ''
                #com['component']['followType'] = 'hot'
                #flag = com['component']['flag']
                del(com['component']['flag'])
                data['items'].append(com)
        num = len(ids)
        if len(data['items']) >= FALL_PER_PAGE_NUM:
            data['flag'] = str(flag + num)
        return '', data

@view_defaults(route_name='followfans')
class FollowFansView(View):

    def __init__(self, request):
        super(FollowFansView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_followfans.get')
    @check_permission
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        user_id = self.request.params.get('id', '')
        if not user_id:
            self.error['error'] = 'User info error.'
            self.error['errorCode'] = '20002'
            return '', {}
        flag = self.request.params.get('flag', '')
        type_id = self.request.params.get('type', '')
        flag = int(flag) if flag else 0
        data = {}
        data['items'] = []
        #ids = get_staruser_ids(flag, FALL_PER_PAGE_NUM)
        ids = []
        if str(type_id) == '0':
            ids = get_follow_list_by_user_id(user_id,flag,FALL_PER_PAGE_NUM)
        else:
            ids = get_fans_list_by_user_id(user_id,flag,FALL_PER_PAGE_NUM)
        for id in ids:
            com = build_user_by_user_id(id)
            if com:
                isFollow = 0
                if self.user_id:
                    isFollow = get_user_follow_status(self.user_id,com['component']['userId'])
                com['component']['isFollow'] = str(isFollow)
                #com['component']['userTypeName'] = '红人'
                #com['component']['userTypeIcon'] = ''
                #com['component']['followType'] = 'hot'
                data['items'].append(com)
        num = len(ids)
        if num >= FALL_PER_PAGE_NUM:
            data['flag'] = str(flag + num)
        return '', data

