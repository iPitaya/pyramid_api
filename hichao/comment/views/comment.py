# -*- coding: utf-8 -*-
from pyramid.view import view_defaults
from pyramid.view import view_config
from hichao.base.views.view_base import View, require_type
from hichao.app.views.oauth2 import check_permission
from hichao.comment.models.comment import (
        get_comment_ids,
        add_comment,
        delete_comment,
        get_comment_count,
        get_comment_by_id,
        )
from hichao.comment.models.sub_thread import get_subthread_ids
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        version_eq,
        )
from hichao.util.object_builder import (
        build_comment_by_id,
        build_rtf_comment_by_id,
        build_subthread_with_user_id,
        build_comment_with_user_id,
        build_comment_as_subthread_by_id,
        )
from hichao.util.comment_util import (
        comment_is_illegal,
        )
from hichao.util.user_util import is_deletable
from hichao.util.content_util import (
        content_to_crawl,
        filter_tag,
        )
from hichao.base.config import (
        MYSQL_MAX_INT,
        COMMENT_NUM_PER_PAGE,
        COMMENT_TYPE_DICT,
        COMMENT_TYPE_STAR,
        COMMENT_TYPE_TOPIC,
        COMMENT_TYPE_THREAD,
        COMMENT_TYPE_THEME,
        COMMENT_TYPE_NEWS,
        )
from hichao.comment import COMMENT_STATUS
from hichao.forum.models.uv import thread_uv_incr
from hichao.forum.models.pv import thread_pv_incr
from hichao.forum.models.thread import (
        get_thread_by_id,
        update_thread_ts,
        )
from hichao.comment.models.sub_thread import (
        add_subthread,
        get_subthread_by_id,
        )
from icehole_client.message_client import ThreadClient, CommentClient
from hichao.util.statsd_client import statsd

import json
import time
import datetime


@view_defaults(route_name='comments')
class CommentView(View):
    def __init__(self, request):
        super(CommentView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_comments.get')
    @check_permission
    @require_type
    @view_config(request_method='GET', renderer = 'json')
    @pack_data
    def get(self):
        _type = COMMENT_TYPE_DICT.get(self.type, '')
        if not _type:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        last_id = self.request.params.get('flag', '')
        item_id = self.request.params.get('id', '')
        rtf = self.request.params.get('rtf', '')
        asc = self.request.params.get('asc', '')
        rtf = rtf == '1' and 1 or 0
        gv = self.request.params.get('gv', '')
        #if gv: gv = gv_float(gv)
        gf = self.request.params.get('gf', '')
        asc = asc == '1' and 1 or 0
        if _type == COMMENT_TYPE_TOPIC or _type == COMMENT_TYPE_NEWS:
            if (gf == 'iphone' and version_ge(gv, 5.3)) or (gf == 'android' and version_ge(gv, 61)) or (gf == 'ipad' and version_ge(gv, 5.0)):
                asc = 0
        if asc == 1:
            last_id = int(last_id) if last_id else 0
        else:
            if _type == COMMENT_TYPE_THREAD:
                last_floor = get_comment_count(COMMENT_TYPE_THREAD, item_id)
                last_id = last_id != '' and int(last_id) or last_floor + 1
            else:
                last_id = last_id != '' and int(last_id) or MYSQL_MAX_INT
        if _type == COMMENT_TYPE_THREAD:
            gi = self.request.params.get('gi', '')
            if gi: thread_uv_incr(gi, item_id)
            thread_pv_incr(item_id)
        lite_user_action = 0
        as_subthread = 0
        if (gf == 'android' and version_ge(gv, 50)) or (gf == 'iphone' and version_ge(gv, 4)) or (gf == 'ipad' and version_ge(gv, 5.0)):
            lite_user_action = 1
        if _type == COMMENT_TYPE_TOPIC or _type == COMMENT_TYPE_NEWS or _type == COMMENT_TYPE_THEME:
            if (gf == 'iphone' and version_ge(gv, 5.3)) or (gf == 'android' and version_ge(gv, 61)) or (gf == 'ipad' and version_ge(gv, 5.0)):
                as_subthread = 1
                rtf = 1
        comment_ids = []
        if _type == COMMENT_TYPE_THREAD:
            if asc:
                sfloor = last_id
                bfloor = last_id + COMMENT_NUM_PER_PAGE
            else:
                bfloor = last_id
                sfloor = last_id - COMMENT_NUM_PER_PAGE
            comment_ids = get_subthread_ids(item_id, sfloor, bfloor)
            if not asc:
                comment_ids.reverse()
        else:
            comment_ids = get_comment_ids(_type, item_id, last_id, COMMENT_NUM_PER_PAGE, asc)
        data = {}
        data['items'] = []
        need_subthread = 0
        need_with_img = 0
        if rtf and _type == COMMENT_TYPE_THREAD:
            if gf == 'android' and version_ge(gv, 45):
                need_subthread = 1
            elif gf == 'iphone' and version_ge(gv, 3.5):
                need_with_img = 1
        for id in comment_ids[0:COMMENT_NUM_PER_PAGE - 1]:
            if rtf:
                if need_subthread:
                    com = build_subthread_with_user_id(id, lite_user_action, self.user_id)
                elif as_subthread:
                    com = build_comment_as_subthread_by_id(_type, id)
                else:
                    com = build_rtf_comment_by_id(_type, id, need_with_img, lite_user_action, self.user_id)
                    if _type != COMMENT_TYPE_THREAD:
                        if self.user_id > 0 and is_deletable(self.user_id, com):
                            com['component']['isDeletable'] = '1'
                if com and _type == COMMENT_TYPE_THREAD:
                    if asc:
                        bfloor = com['flag']
                    else:
                        sfloor = com['flag']
                    del(com['flag'])
            else:
                com = build_comment_with_user_id(_type, id, self.user_id)
            if com:
                data['items'].append(com)
        data['total'] = str(get_comment_count(_type, item_id))
        if _type == COMMENT_TYPE_THREAD:
            if asc:
                if len(comment_ids) > 0:
                    data['flag'] = str(bfloor + 1)
                else:
                    data['flag'] = str(last_id)
            else:
                if sfloor > 1:
                    data['flag'] = str(sfloor - 1)
        else:
            if len(comment_ids) >= COMMENT_NUM_PER_PAGE:
                data['flag'] = str(comment_ids[-1])
        ################################2.3 iphone 兼容代码。##########################
        if data['total'] == '0':
            platform = self.request.params.get('gf', '')
            version = self.request.params.get('gv', '')
            if platform == 'iphone':
                if version_eq(version, '1.0') or version_eq(version, '2.3'):
                    data['total'] = '1'
                    data['items'] = [{'component':{'userName':'明星小助手', 'content':'还木有评论哦，快来抢个沙发吧～',
                        'floor':'', 'publishDate':'刚刚', 'componentType':'comment',
                        'userAvatar':'http://img1.hichao.com/images/images/20130718/510508a1-6974-4351-9e69-9cb1910e3fd2.png', 'action':{}}},]
        ###############################################################################
        return '', data

    @statsd.timer('hichao_backend.r_comments.post')
    @check_permission
    @require_type
    @view_config(request_method='POST', renderer = 'json')
    @pack_data
    def post(self):
        from_uid = int(self.user_id)
        content = self.request.params.get('content', '').strip()
        item_id = self.request.params.get('id', '')
        comment_id = self.request.params.get('comment_id', '')
        gf = self.request.params.get('gf', '')
        if not from_uid or from_uid <= 0:
            self.error['error'] = 'Check user failed.'
            self.error['errorCode'] = '20001'
            return '', {}
        comment_status = comment_is_illegal(from_uid, content)
        if comment_status != COMMENT_STATUS.TYPE.NORMAL:
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return COMMENT_STATUS.MSG[comment_status], {}
        content = filter_tag(content)
        _type = COMMENT_TYPE_DICT.get(self.type, '')
        if not _type:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        comment_id = comment_id and int(comment_id) or 0
        thread_owner_id = 0
        to_uid = 0
        ip = self.request.environ.get('HTTP_X_REAL_IP', '')
        if not ip: ip = self.request.client_addr

        platform = 0
        if gf == 'web':
            platform = 1
        elif gf == 'iphone':
            platform = 2
        elif gf == 'android':
            platform = 3
        elif gf == 'ipad':
            platform = 4

        if _type == COMMENT_TYPE_THREAD:
            thread = get_thread_by_id(item_id)
            if thread.is_set_forbidden():
                self.error['error'] = 'Operation failed.'
                self.error['errorCode'] = '30001'
                return u'该帖子被设置为禁止回复。', {}
            category_id = thread.category_id
            thread_owner_id = thread.user_id
            if comment_id:
                sub_thread = get_subthread_by_id(comment_id)
                to_uid = sub_thread.from_uid
            else:
                to_uid = thread.user_id
            floor = get_comment_count(COMMENT_TYPE_THREAD, item_id, use_cache = False)
            floor = floor + 1 if floor else 1
            has_img = 0

            re = add_subthread(item_id, content.decode('utf-8'), from_uid, to_uid, comment_id,
                    datetime.datetime.now(), ip, has_img, floor, category_id, platform = platform)
        else:
            re = add_comment(_type, item_id, from_uid, comment_id, content.decode('utf-8'), comment_status, ip = ip, platform = platform)
        if re > 0:
            if _type == COMMENT_TYPE_THREAD:
                update_thread_ts(item_id)
                get_comment_count(COMMENT_TYPE_THREAD, item_id, use_cache = False)
                content_to_crawl(from_uid, content, item_id)
                msg_thread_client = ThreadClient()
                msg_comment_client = CommentClient()
                if int(from_uid) != int(to_uid):
                    if int(from_uid) != int(thread_owner_id):
                        msg_thread_client.msg_new(int(thread_owner_id), int(item_id), int(from_uid), int(re), str(content), str(time.time()))
                        if comment_id > 0:
                            msg_comment_client.msg_new(int(to_uid), int(item_id), int(comment_id), int(from_uid), int(re), str(time.time()))
                    else:
                        if comment_id > 0:
                            msg_comment_client.msg_new(int(to_uid), int(item_id), int(comment_id), int(from_uid), int(re), str(time.time()))
                else:
                    if int(from_uid) != int(thread_owner_id):
                        msg_thread_client.msg_new(int(thread_owner_id), int(item_id), int(from_uid), int(re), str(content), str(time.time()))
            if _type == COMMENT_TYPE_TOPIC or _type == COMMENT_TYPE_THEME:
                content_to_crawl(from_uid, content, 0)
        else:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
        return '', {}

    @statsd.timer('hichao_backend.r_comments.delete')
    @check_permission
    @require_type
    @view_config(request_method = 'DELETE', renderer = 'json')
    @pack_data
    def delete(self):
        user_id = self.user_id
        comment_id = self.request.params.get('comment_id', '')
        _type = COMMENT_TYPE_DICT.get(self.type, '')
        if not comment_id or not _type:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        res = delete_comment(_type,user_id, comment_id)
        if res == 1:
            build_rtf_comment_by_id(_type, comment_id, use_cache = False)
            return '', {}
        else:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return '', {}

