# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.feed.models.follow import Follow
from hichao.app.views.oauth2 import check_permission
from hichao.util.pack_data import pack_data
from hichao.base.views.view_base import View,require_type
from hichao.base.config import (
        FOLLOWING_TYPE,
        )
from hichao.util.statsd_client import statsd
from icehole_client.follow_client import FollowClient, FollowType
from hichao.follow.models.follow import (
        forum_follow_del,
        forum_follow_new,
        following_id_list_by_user_id,
        )

@view_defaults(route_name = 'follow')
class FollowView(View):
    def __init__(self, request):
        super(FollowView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_follow.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        return self.handle('follow')

    @statsd.timer('hichao_backend.r_follow.delete')
    @check_permission
    @view_config(request_method = 'DELETE', renderer = 'json')
    @pack_data
    def delete(self):
        return self.handle('unfollow')

    def handle(self, act):
        follow_type = self.request.params.get('type', '')
        if follow_type != 'user':
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        uid = int(self.user_id)
        if uid <= 0:
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return '', {}
        follow_id = self.request.params.get('type_id', '')
        status = False
        if follow_type == 'user':
            # 自己关注自己
            #if int(follow_id) == uid:
            #    self.error['error'] = 'Operation failed.'
            #    self.error['errorCode'] = '30001'
            #    return '', {}
            #follower = Follow(uid)
            client = FollowClient()
            follow_id = int(follow_id)
            uid = int(uid)
            if act == 'follow':
                #status = follower.follow(follow_id)
                status = client.follow(uid, follow_id, FollowType.USER)
            elif act == 'unfollow':
                #status = follower.unfollow(follow_id)
                status = client.unfollow(uid, follow_id, FollowType.USER)
        if not status:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
        return '', {}

#6.4.0 新版社区关注接口
@view_defaults(route_name = 'new_forum_follow')
class NewForumFollowView(View):
    def __init__(self, request):
        super(NewForumFollowView, self).__init__()
        self.request = request

    #新增加关注接口
    @statsd.timer('hichao_backend.r_new_forum_follow.post')
    @check_permission
    #@require_type
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        return self.handle('follow')

    #取消关注接口
    @statsd.timer('hichao_backend.r_follow.delete')
    @check_permission
    #@require_type
    @view_config(request_method = 'DELETE', renderer = 'json')
    @pack_data
    def delete(self):
        return self.handle('unfollow')

    def handle(self, act):
        _type = self.request.params.get('type', '')
        user_id = self.request.params.get('user_id', '')
        if user_id <= 0:
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return '', {}
        following_id = self.request.params.get('following_id', '')
        if not following_id:
            self.error['error'] = 'Argument error'
            self.error['errorCode'] = '10001'
            return '',{}
        #following_code = FOLLOWING_TYPE.CODE[_type]
        if user_id == following_id:
            self.error['error'] = 'Argument error'
            self.error['errorCode'] = '10001'
            return '',{}
        status = False
        user_id = int(user_id)
        following_id = int(following_id)
        #following_code = int(following_code)
        if act == 'follow':
            status = forum_follow_new(user_id, following_id)
        elif act == 'unfollow':
            status = forum_follow_del(user_id, following_id)
        if not status:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return '', {}
        return '', {}

@view_defaults(route_name='following_ids')
class FollowingIdsView(View):
    def __init__(self, request):
        super(FollowingIdsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_collection_ids.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        data = {}
        user_id = self.request.params.get('user_id', '')
        following_user_ids = following_id_list_by_user_id(user_id)
        if following_user_ids:
            hot_ids = ','.join(map(str, following_user_ids[0]))
            data['hot_ids'] = hot_ids
            star_ids = ','.join(map(str, following_user_ids[1]))
            data['star_ids'] = star_ids
            designer_ids = ','.join(map(str, following_user_ids[2]))
            data['designer_ids'] = designer_ids
        return '', data

