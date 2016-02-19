# -*- coding:utf-8 -*-

from pyramid.view import (
    view_defaults,
    view_config,
    )
from hichao.base.views.view_base import View
from hichao.util.statsd_client import statsd
from hichao.util.pack_data import pack_data
from hichao.post.models.post import get_post_by_id
from hichao.post.models.post_comment import (
    get_repost_comments,
    get_norepost_post_comment_ids_by_ids,
    get_post_comments_by_id,
    )
from hichao.app.views.oauth2 import check_permission
from hichao.util.object_builder import (
    build_post_comment_by_obj,
    build_post_by_post_id,
    )
from hichao.comment.models.sub_thread import (
    get_subthread_ids_for_thread,
    get_subthreads_by_id,
    )
from hichao.util.component_builder import build_component_post_subthread
from hichao.base.config import FALL_PER_PAGE_NUM
from hichao.follow.models.follow import get_user_follow_status


@view_defaults(route_name = 'post')
class PostView(View):
    def __init__(self, request):
        super(PostView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_post.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        post_id = self.request.params.get('id', '')
        if not post_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        post = get_post_by_id(post_id)
        if not post:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return u'内容不存在。', {}
        post_comments = get_repost_comments(post_id)
        data = {}
        post_coms = []
        split_items = 1
        inner_redirect = 1
        support_webp = 1
        support_brandstore = 1
        post_coms.append(build_post_by_post_id(post.id))
        for comment in post_comments:
            if comment:
                post_coms.append(build_post_comment_by_obj(comment.id, 'comment', obj = comment))
        data['items'] = post_coms
        data['tags'] = post.get_component_tags()
        data['user'] = post.get_component_user()
        data['user']['isfocus'] = str(
            get_user_follow_status(self.user_id, data['user']['userId']))
        _type = post.get_user_type_name();
        if _type:
             data['user']['userTypeName'] = _type.get('userTypeName')
             data['user']['followType'] = _type.get('followType')
        else:
             data['user']['userTypeName'] = ''
             data['user']['followType'] = ''
        data['likedUsers'] = post.get_component_liked_users()
        data['shareAction'] = post.get_share_action()
        data['id'] = post.id
        data['title'] = post.get_component_title()
        return '', data

@view_defaults(route_name = 'post_comments')
class PostCommentsView(View):
    def __init__(self, request):
        super(PostCommentsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_post_comments.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        post_id = self.request.params.get('id', '')
        flag = self.request.params.get('flag', '')
        if not post_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        if not flag:
            flag = 0
            limit=3
        else:
            limit = FALL_PER_PAGE_NUM
        comments_ids = get_norepost_post_comment_ids_by_ids(post_id,int(flag),limit)
        data = {}
        if comments_ids:
            comments = get_post_comments_by_id(comments_ids)
            data['items'] = []
            for item in comments:
                com = build_component_post_subthread(item)
                data['items'].append(com)
        if len(comments_ids) >= FALL_PER_PAGE_NUM:
            data['flag'] = str(int(flag) + FALL_PER_PAGE_NUM)
        elif len(comments_ids) == 3 and int(flag) == 0:
            data['flag'] = '3'
        return '',data
