# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.base.celery.db import celery
from hichao.app.views.oauth2 import check_permission
from hichao.comment.models.sub_thread import add_subthread
from hichao.util.pack_data import pack_data
from hichao.base.config import (
        COMMENT_TYPE_THREAD,
        FALL_PER_PAGE_NUM,
        )
from hichao.forum.models.uv import thread_uv_incr
from hichao.forum.models.pv import tag_comment_count_incr
from hichao.forum.models.thread import update_thread_ts
from hichao.comment.models.comment import (
        get_comment_count,
        get_comment_count_for_thread,
        )
from hichao.post.models.post_comment import get_repost_comments
from hichao.util.comment_util import comment_is_illegal
from hichao.comment.models.sub_thread import (
        get_subthread_by_id,
        get_subthread_ids,
        get_subthread_ids_for_thread,
        )
from hichao.forum.models.thread import get_thread_by_id
from hichao.comment.models.sub_thread_img import add_subthread_imgs
from hichao.points.models.points import point_change
from hichao.comment import COMMENT_STATUS
from hichao.util.object_builder import build_lite_thread_by_id
from hichao.util.content_util import (
        content_to_crawl,
        filter_tag,
        )
from icehole_client.message_client import ThreadClient, CommentClient
from hichao.util.statsd_client import statsd
from hichao.user.models.refused_ip import ip_in_black_list
from hc.utils.ip import ip2long, long2ip
import datetime
import time
from hichao.cache.cache import delete_cache_by_key


@view_defaults(route_name = 'sub_thread')
class SubThreadView(View):
    def __init__(self, request):
        super(SubThreadView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_sub_thread.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        add_status = 0
        thread_id = self.request.params.get('thread_id', '')
        gf = self.request.params.get('gf', '')
        if not thread_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}
        repost = self.request.params.get('repost', '')
        repost = int(repost) if repost else 0
        sku_sids = self.request.params.get('skus', '')
        if sku_sids: sku_sids = [sku_sid for sku_sid in sku_sids.split(',') if sku_sid.isdigit()]
        if sku_sids: sku_sids = ','.join(sku_sids)
        content = self.request.params.get('content', '').strip()
        from_uid = int(self.user_id)
        if from_uid <= 0:
            self.error['error'] = 'User info expired.'
            self.error['errorCode'] = '20002'
            return '', {}
        comment_status = comment_is_illegal(from_uid, content)
        if comment_status != COMMENT_STATUS.TYPE.NORMAL:
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return COMMENT_STATUS.MSG[comment_status], {}
        ip = self.request.environ.get('HTTP_X_REAL_IP', '')
        if not ip: ip = self.request.client_addr
        int_ip = ip2long(ip)
        if ip_in_black_list(int_ip):
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return '您的IP已被列入黑名单！如有疑问请联系客服人员。', {}
        content = filter_tag(content)
        comment_id = self.request.params.get('comment_id', '')
        comment_id = int(comment_id) if comment_id else 0
        category_id = 0
        to_uid = 0
        thread_owner_id = 0
        thread = get_thread_by_id(thread_id)
        if thread.is_set_forbidden():
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return u'该帖子被设置为禁止回复。', {}
        thread_owner_id = thread.user_id
        category_id = thread.category_id
        if comment_id:
            subthread = get_subthread_by_id(comment_id)
            to_uid = subthread.from_uid
        else:
            to_uid = thread.user_id
        img_ids = self.request.params.get('image_ids', '')
        if img_ids:
            if thread.img_locked() and int(from_uid) != int(thread_owner_id):
                self.error['error'] = 'Operation failed.'
                self.error['errorCode'] = '30001'
                return u'该帖子仅限楼主发图。', {}
            img_ids = img_ids.split(',')
            img_ids = [int(id) for id in img_ids if id.isdigit()]
            if 0 in img_ids:
                self.error['error'] = 'Arguments error.'
                self.error['errorCode'] = '10001'
                return '部分图片上传出现错误，请重新上传图片。', {}
        else:
            img_ids = []
        has_img = 0
        if img_ids: has_img = 1
        floor = get_comment_count(COMMENT_TYPE_THREAD, thread_id, use_cache = False)
        floor = floor + 1 if floor else 1
        platform = 0
        if gf == 'web':
            platform = 1
        elif gf == 'iphone':
            platform = 2
        elif gf == 'android':
            platform = 3
        elif gf == 'ipad':
            platform = 4
        res_id = add_subthread(thread_id, content.decode('utf-8'), from_uid, to_uid, comment_id, datetime.datetime.now(),
                ip, has_img, floor, category_id, platform, sku_sids, repost)
        save_img_status = 0
        if res_id and has_img:
            save_img_status = add_subthread_imgs(res_id, map(int, img_ids))
        if not has_img: save_img_status = 1
        if res_id and save_img_status:
            add_status = 1
        else:
            if not res_id:
                self.error['error'] = 'Save thread failed.'
            else:
                self.error['error'] = 'Save imgs failed.'
            self.error['errorCode'] = '30001'
        if add_status:
            tag_ids = thread.tags
            tag_ids = [tag_id for tag_id in tag_ids.split(',') if tag_id.isdigit()]
            for tag_id in tag_ids:
                tag_comment_count_incr(tag_id)
        max_floor = get_comment_count_for_thread(COMMENT_TYPE_THREAD, thread_id, use_cache = False)
        if floor == 1:
            #get_subthread_ids_for_thread(thread_id, 0, FALL_PER_PAGE_NUM, 0, use_cache = False)
            key_asc = 'subthread_ids_for_thread_' + str(thread_id) + '_' + str(0) + '_' + str(FALL_PER_PAGE_NUM) + '_' + str(0)
            delete_cache_by_key(key_asc)
            #get_subthread_ids_for_thread(thread_id, 0, FALL_PER_PAGE_NUM, 1, use_cache = False)
            key_desc = 'subthread_ids_for_thread_' + str(thread_id) + '_' + str(0) + '_' + str(FALL_PER_PAGE_NUM) + '_' + str(1)
            delete_cache_by_key(key_desc)
        else:
            #get_subthread_ids_for_thread(thread_id, max_floor-1, FALL_PER_PAGE_NUM, 0, use_cache = False)
            key_asc = 'subthread_ids_for_thread_' + str(thread_id) + '_' + str(max_floor-1) + '_' + str(FALL_PER_PAGE_NUM) + '_' + str(0)
            delete_cache_by_key(key_asc)
            #get_subthread_ids_for_thread(thread_id, max_floor-1, FALL_PER_PAGE_NUM, 1, use_cache = False)
            key_desc = 'subthread_ids_for_thread_' + str(thread_id) + '_' + str(max_floor-1) + '_' + str(FALL_PER_PAGE_NUM) + '_' + str(1)
            delete_cache_by_key(key_desc)
        if repost:
            get_repost_comments(thread_id, use_cache = False)
        sync_user_post.delay(add_status, floor, from_uid, content, thread_id, thread_owner_id, res_id, to_uid, comment_id)
        return '', {}

@celery.task(ignore_result=True)
def sync_user_post(add_status, floor, from_uid, content, thread_id, thread_owner_id, res_id, to_uid, comment_id, repost):
    if add_status:
        time.sleep(0.05)
        #max_floor = get_comment_count_for_thread(COMMENT_TYPE_THREAD, thread_id, use_cache = False)
        #if floor == 1:
        #    get_subthread_ids_for_thread(thread_id, 0, FALL_PER_PAGE_NUM, 0, use_cache = False)
        #    get_subthread_ids_for_thread(thread_id, 0, FALL_PER_PAGE_NUM, 1, use_cache = False)
        #else:
        #    get_subthread_ids_for_thread(thread_id, max_floor-1, FALL_PER_PAGE_NUM, 0, use_cache = False)
        #    get_subthread_ids_for_thread(thread_id, max_floor-1, FALL_PER_PAGE_NUM, 1, use_cache = False)
        #if repost:
        #    get_repost_comments(thread_id,use_cache = False)
        update_thread_ts(thread_id)
        build_lite_thread_by_id(thread_id, 0, 1, use_cache = False)
        build_lite_thread_by_id(thread_id, 0, use_cache = False)
        build_lite_thread_by_id(thread_id, 1, use_cache = False)
        get_comment_count(COMMENT_TYPE_THREAD, thread_id, use_cache = False)
        content_to_crawl(from_uid, content, thread_id)
        msg_thread_client = ThreadClient()
        msg_comment_client = CommentClient()
        if int(from_uid) != int(to_uid):
            if int(from_uid) != int(thread_owner_id):
                msg_thread_client.msg_new(int(thread_owner_id), int(thread_id), int(from_uid), int(res_id), str(content), str(time.time()))
                if comment_id > 0:
                    res = msg_comment_client.msg_new(int(to_uid), int(thread_id), int(comment_id), int(from_uid), int(res_id), str(time.time()))
            else:
                if comment_id > 0:
                    msg_comment_client.msg_new(int(to_uid), int(thread_id), int(comment_id), int(from_uid), int(res_id), str(time.time()))
        else:
            if int(from_uid) != int(thread_owner_id):
                msg_thread_client.msg_new(int(thread_owner_id), int(thread_id), int(from_uid), int(res_id), str(content), str(time.time()))

