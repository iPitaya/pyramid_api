# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.forum.models.thread import (
        add_thread,
        get_thread_ids,
        delete_thread,
        update_thread_ts,
        )
from hichao.forum.models.thread_star import get_thread_stars
from hichao.base.views.view_base import View
from hichao.base.config import (
        MYSQL_MAX_TIMESTAMP,
        FALL_PER_PAGE_NUM,
        COMMENT_TYPE_THREAD,
        )
from hichao.base.celery.db import celery
from hichao.util.comment_util import comment_is_illegal
from hichao.app.views.oauth2 import check_permission
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        )
from hichao.util.object_builder import (
        build_thread_by_id,
        build_star_by_star_id,
        build_sub_threads_by_id,
        )
from hichao.util.component_builder import build_component_drop
from hichao.util.content_util import (
        content_to_crawl,
        filter_tag,
        )
from hichao.util.user_util import (
        #is_deletable,
        is_owner,
        )
from hichao.collect.models.thread import (
        thread_top_list_by_category,
        thread_top_list_all,
        )
from hichao.base.lib.redis import redis
from hichao.base.lib.timetool import today_days, day2days
from hichao.collect.models.thread import REDIS_THREAD_PUBLISH_DAYS, thread_collect_new
from hichao.collect.models.thread_top import (
        thread_top_n,
        thread_top_n_weekly,
        )
from hichao.forum.models.top_thread import (
        get_top_thread_ids,
        get_all_top_thread_ids,
        )
from hichao.forum.models.thread import get_thread_by_id
from hichao.forum.models.thread_img import add_thread_imgs
from hichao.forum.models.forum import (
        get_forum_cat_id_by_name,
        get_forum_name_by_cat_id,
        )
from hichao.forum.models.uv import thread_uv_incr
from hichao.forum.models.pv import (
    thread_pv_incr,
    tag_thread_count_incr,
    )
from hichao.forum.models.online import set_online_user
from hichao.points.models.points import point_change
from hichao.cache.cache import deco_cache
from hichao.util.date_util import HOUR
from hichao.patch.show_forum_patch import patch_ios_description_with_forum_v_3_3
from hichao.comment.models.sub_thread import add_subthread
from hichao.comment.models.sub_thread_img import add_subthread_imgs
from hichao.comment.models.comment import get_comment_count
from hichao.comment import COMMENT_STATUS
from hichao.util.statsd_client import statsd
from hichao.user.models.refused_ip import ip_in_black_list
from hc.utils.ip import ip2long, long2ip
from hichao.forum.models.tag import get_tag_id_by_tag
from hichao.util import rmq_client

import datetime
import time
import json

@deco_cache(prefix = 'main_thread_action', recycle = HOUR)
def get_main_thread_action(thread_id, use_cache = True):
    thread = get_thread_by_id(thread_id)
    return thread.to_ui_action()

@celery.task(ignore_result=True)
def sync_user_post(res_id, save_img_status, user_id, content, thread_id, msg):
    if res_id > 0:
        if thread_id == 0:
            content_to_crawl(int(user_id), content, res_id)
        else:
            content_to_crawl(int(user_id), content, thread_id)
        if save_img_status:
            if not thread_id:
                redis.hset(REDIS_THREAD_PUBLISH_DAYS, res_id, day2days(time.time()))
                thread_collect_new(-1, [res_id, ], n=0)
        if thread_id:
            update_thread_ts(thread_id)
            build_sub_threads_by_id(thread_id, use_cache = False)
        rmq_client.send(msg)
@view_defaults(route_name = 'thread')
class ThreadView(View):
    def __init__(self, request):
        super(ThreadView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_thread.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        return '', {'items':[]}
        thread_id = self.request.params.get('subject_id', '')
        gi = self.request.params.get('gi', '')
        if gi: thread_uv_incr(gi, thread_id)
        thread_pv_incr(thread_id)
        with_main = self.request.params.get('with_main', '')
        if not thread_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10001'
            return '', {}
        data = {}
        threads = build_sub_threads_by_id(thread_id)
        data['items'] = threads
        if with_main:
            data['main'] = get_main_thread_action(thread_id)
        return '', data

    @statsd.timer('hichao_backend.r_thread.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        #3.5.x版发帖
        img_ids = self.request.params.get('image_ids', '')
        category = self.request.params.get('category', '')
        content = self.request.params.get('content', '')
        title = self.request.params.get('title', '')
        forum_id = self.request.params.get('forum_id', '')
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        tag_ids = self.request.params.get('tags', '')
        sku_sids = self.request.params.get('skus', '')

        need_tag = 0
        if (gf == 'iphone' and version_ge(gv, '6.4.0')) or (gf == 'android' and version_ge(gv, '640')):
            need_tag = 1
        if need_tag:
            tag_ids = [tag_id for tag_id in tag_ids.split(',') if tag_id.isdigit()]
            if not tag_ids:
                self.error['error'] = 'Arguments missing'
                self.error['errorCode'] = '10001'
                return '请至少选择一个标签。', {}
            if len(tag_ids) > 5:
                self.error['error'] = 'Arguments error'
                self.error['errorCode'] = '10001'
                return '选择的标签太多了哦', {}
        if sku_sids: sku_sids = [sku_sid for sku_sid in sku_sids.split(',') if sku_sid.isdigit()]
        if sku_sids: sku_sids = ','.join(sku_sids)

        if not content:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10001'
            return '', {}
        if len(unicode(title)) > 24:
            self.error['error'] = 'The title is too long.'
            self.error['errorCode'] = '11005'
            return u'您的帖子标题太长，最多可输入24个汉字的长度。', {}
        from_uid = int(self.user_id)
        comment_status = comment_is_illegal(from_uid, content)
        if comment_status == COMMENT_STATUS.TYPE.NORMAL:
            if not need_tag:
                comment_status = comment_is_illegal(from_uid, title)
        if from_uid <= 0 or comment_status != COMMENT_STATUS.TYPE.NORMAL:
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

        platform = 0
        if gf == 'web':
            platform = 1
        elif gf == 'iphone':
            platform = 2
        elif gf == 'android':
            platform = 3
        elif gf == 'ipad':
            platform = 4

        content = filter_tag(content)
        title = filter_tag(title)
        category_name = ''
        if forum_id:
            category_name = get_forum_name_by_cat_id(forum_id)
        if category_name:
            category_id = forum_id
        else:
            category_id = get_forum_cat_id_by_name(category, '')
        if not need_tag:
            tag = category_name if category_name else category
            tag_id = get_tag_id_by_tag(tag)
            if tag_id: tag_ids = [tag_id]
            else: tag_ids = []
        if not tag_ids:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '参数错误，发布失败！', {}
        tag_ids = [str(tag_id) for tag_id in tag_ids]
        tag_ids = ','.join(tag_ids)
        thread_id = self.request.params.get('subject_id', '')
        image_id = 0 #旧版兼容，默认为0
        search_msg = {}#发送消息给搜索更新帖子
        if img_ids:
            img_ids = img_ids.split(',')
            img_ids = [int(id) for id in img_ids if id.isdigit()]
            if 0 in img_ids:
                self.error['error'] = 'Arguments error.'
                self.error['errorCode'] = '10001'
                return '部分图片上传出现错误，请重新上传图片。', {}
        else:
            img_ids = []
        if need_tag and not img_ids:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '请至少上传一张图片！', {}
        if not category_id: category_id = 0
        if thread_id:
            thread_id = int(thread_id)
            thread = get_thread_by_id(thread_id)
            if thread:
                category_id = thread.category_id
        else:
            thread_id = 0
        review = 1

        has_img = 0
        res_id = 0
        if img_ids: has_img = 1
        if thread_id == 0:
            res_id = add_thread(self.user_id, image_id, content, category_id, ip, title = title, has_img = has_img, platform = platform, tags = tag_ids, skus = sku_sids)
        else:
            floor = get_comment_count(COMMENT_TYPE_THREAD, thread_id, use_cache = False)
            floor = floor + 1 if floor else 1
            res_id = add_subthread(thread_id, content, self.user_id, self.user_id, 0, datetime.datetime.now(), ip,
                    has_img, floor, category_id, platform = platform)
        save_img_status = 0
        if res_id > 0:
            get_comment_count(COMMENT_TYPE_THREAD, thread_id, use_cache = False)
            if has_img:
                if thread_id == 0:
                    save_img_status = add_thread_imgs(res_id, map(int, img_ids))
                else:
                    save_img_status = add_subthread_imgs(res_id, map(int, img_ids))
            else:
                save_img_status = 1
        if not (res_id and save_img_status):
            if not res_id:
                self.error['error'] = 'Save thread failed.'
            else:
                self.error['error'] = 'Save imgs failed.'
            self.error['errorCode'] = '30001'
        img_ids = [str(img_id) for img_id in img_ids]
        if res_id > 0:
            search_msg['id'] = str(res_id)
            search_msg['category_id'] = str(category_id)
            search_msg['user_id'] = str(self.user_id)
            search_msg['img_id'] = ','.join(img_ids)
            search_msg['title'] = title
            search_msg['content'] = content
            search_msg['ts'] = str(time.time())
            search_msg['review'] = '1'
            search_msg['tags'] = tag_ids
            tag_ids = [tag_id for tag_id in tag_ids.split(',') if tag_id.isdigit()]
            for tag_id in tag_ids:
                tag_thread_count_incr(tag_id)
        rmq_client.send_thread(json.dumps(search_msg))
        sync_user_post.delay(res_id, save_img_status, self.user_id, content, thread_id, json.dumps(search_msg))
        return '', {}

    @statsd.timer('hichao_backend.r_thread.delete')
    @check_permission
    @view_config(request_method = 'DELETE', renderer = 'json')
    @pack_data
    def delete(self):
        self.error['error'] = 'Permission denied.'
        self.error['errorCode'] = '40001'
        return '', {}
        user_id = self.user_id
        thread_id = self.request.params.get('subjectId', '')
        if not thread_id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        res = delete_thread(user_id, thread_id)
        if res == 0:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return '', {}
        else:
            build_thread_by_id(thread_id, use_cache = False)
            get_thread_ids(MYSQL_MAX_TIMESTAMP, FALL_PER_PAGE_NUM, 0, use_cache = False)

            #point_change.delay(user_id, "post_thread", thread_id, time.time(), method="rm")
            return '', {'id':str(thread_id),}

@view_defaults(route_name = 'threads')
class ThreadsView(View):
    def __init__(self, request):
        super(ThreadsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_threads.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @patch_ios_description_with_forum_v_3_3
    @pack_data
    def get(self):
        category = self.request.params.get('category', '')
        _type = self.request.params.get('type', 'latest')
        flag = self.request.params.get('flag', '')
        app_from = self.request.params.get('gf', '')
        more_img = self.request.params.get('more_pic', '')
        crop = self.request.params.get('crop', '')
        crop = 1 if crop else 0
        if category:
            query_tp = get_forum_cat_id_by_name(category)
            if not query_tp:
                self.error['error'] = 'Arguments missing.'
                self.error['errorCode'] = '10002'
                return '', {}
        else:
            query_tp = 0

        if query_tp:
            gi = self.request.params.get('gi', '')
            set_online_user(gi, query_tp)

        # 下边这段注意。。。
        # 某些flag传回来会是字符串‘0’，此时使用 and or 语句，如果不返回list的话，
        # 会总是返回 or 后边的数据。。所以返回了list然后取第一个元素。。。
        if _type == 'latest':
            return self.get_latest_threads(query_tp, flag, self.user_id, crop, more_img)
        elif _type == 'hot':
            return self.get_hot_threads(query_tp, flag, self.user_id, crop, app_from, more_img)
        elif _type == 'link':
            flag = (flag != '' and [flag,] or [MYSQL_MAX_TIMESTAMP,])[0]
            return self.get_link_threads(flag)
        elif _type == 'weekly':
            flag = (flag != '' and [int(flag),] or [0,])[0]
            return self.get_weekly_hot_threads(flag, self.user_id, crop, more_img)
        else:
            return self.get_latest_threads(query_tp, flag, self.user_id, crop, more_img)
            #return self.get_hot_threads(query_tp, flag, self.user_id, crop, app_from, more_img)

    def get_latest_threads(self, tp, flag, user_id, crop = 0, more_img = ''):
        is_top = False
        if flag == '':
            is_top = True
            flag = 0
        elif flag.startswith('t'):
            is_top = True
            flag = int(flag[1:])
        top_ids = []
        has_next_page = False
        if is_top:
            ids = get_top_thread_ids(tp == 0 and -2 or tp, flag, FALL_PER_PAGE_NUM)
            top_ids = get_all_top_thread_ids(tp == 0 and -2 or tp)
            has_next_page = True
            if len(ids) < 10:
                is_top = False
                extend_ids = get_thread_ids(MYSQL_MAX_TIMESTAMP, FALL_PER_PAGE_NUM, tp)
                extend_ids = [int(id) for id in extend_ids if id not in top_ids]
                ids.extend(extend_ids)
        else:
            ids = get_thread_ids(flag, FALL_PER_PAGE_NUM, tp)
            if len(ids) == FALL_PER_PAGE_NUM:
                has_next_page = True
            top_ids = get_all_top_thread_ids(tp == 0 and -2 or tp)
            ids = [id for id in ids if id not in top_ids]

        data = {}
        data['items'] = []
        _flag = ''
        for id in ids:
            com = build_thread_by_id(id, crop, more_img)
            if com:
                #if self.user_id > 0 and is_deletable(self.user_id, com):
                #    com['component']['actions'][1]['isDeletable'] = '1'
                if self.user_id > 0 and is_owner(self.user_id, com):
                    com['component']['actions'][1]['isOwner'] = '1'
                if id in top_ids:
                    com['component']['status'] = 'premium'
                _flag = com['uts']
                del(com['uts'])
                data['items'].append(com)
        if has_next_page:
            if is_top:
                data['flag'] = 't' + str(flag + FALL_PER_PAGE_NUM)
            else:
                data['flag'] = str(_flag)
        return '', data

    def get_hot_threads(self, tp, flag, user_id, crop, platform, more_img = ''):
        no_drop = self.request.params.get('no_drop', '')
        is_top = False
        if flag == '':
            is_top = True
            flag = 0
        elif flag.startswith('t'):
            is_top = True
            flag = int(flag[1:])
        else:
            flag = int(flag)
        top_ids = []
        has_next_page = False
        first_page = False
        if is_top:
            first_page = True
            ids = get_top_thread_ids(tp == 0 and -1 or tp, flag, FALL_PER_PAGE_NUM)
            top_ids = get_all_top_thread_ids(tp == 0 and -1 or tp)
            has_next_page = True
            if len(ids) < 10:
                is_top = False
                flag = 0
                if tp == 0:
                    extend_ids = thread_top_n(offset = flag, limit = FALL_PER_PAGE_NUM)
                else:
                    extend_ids = thread_top_list_by_category(tp, offset = flag, limit = FALL_PER_PAGE_NUM)
                extend_ids = [int(id[0]) for id in extend_ids if int(id[0]) not in ids]
                ids.extend(extend_ids)
        else:
            if tp == 0:
                ids = thread_top_n(offset = flag, limit = FALL_PER_PAGE_NUM)
            else:
                ids = thread_top_list_by_category(tp, offset = flag, limit = FALL_PER_PAGE_NUM)
            ids = [int(id[0]) for id in ids]
            if len(ids) >= FALL_PER_PAGE_NUM:
                has_next_page = True
            top_ids = get_all_top_thread_ids(tp == 0 and -1 or tp)
            ids = [int(id) for id in ids if int(id) not in top_ids]
        data = {}
        data['items'] = []
        drop_first = True
        if no_drop: drop_first = False
        for id in ids:
            if platform != 'android' and first_page and drop_first:
                thread = get_thread_by_id(id)
                com = build_component_drop(thread)
                if com: drop_first = False
            else:
                com = build_thread_by_id(id, crop, more_img)
            if com:
                #if self.user_id > 0 and is_deletable(self.user_id, com):
                #    com['component']['actions'][1]['isDeletable'] = '1'
                if self.user_id > 0 and is_owner(self.user_id, com):
                    com['component']['actions'][1]['isOwner'] = '1'
                if id in top_ids:
                    com['component']['status'] = 'hot'
                data['items'].append(com)
        if has_next_page:
            if is_top:
                data['flag'] = 't' + str(flag + FALL_PER_PAGE_NUM)
            else:
                data['flag'] = str(flag + FALL_PER_PAGE_NUM + 1)
        return '', data

    def get_weekly_hot_threads(self, flag, user_id, crop, more_img = ''):
        ids = thread_top_n_weekly(offset = flag, limit = FALL_PER_PAGE_NUM)
        ids = [int(id[0]) for id in ids]
        data = {}
        data['items'] = []
        for id in ids:
            com = build_thread_by_id(id, crop, more_img)
            if com:
                #if self.user_id > 0 and is_deletable(self.user_id, com):
                #    com['component']['actions'][1]['isDeletable'] = '1'
                if self.user_id > 0 and is_owner(self.user_id, com):
                    com['component']['actions'][1]['isOwner'] = '1'
                data['items'].append(com)
        if len(ids) >= FALL_PER_PAGE_NUM:
            data['flag'] = str(flag + FALL_PER_PAGE_NUM + 1)
        return '', data

    def get_link_threads(self, flag):
        stars = get_thread_stars(flag, FALL_PER_PAGE_NUM)
        data = {}
        data['items'] = []
        for star in stars:
            com = build_star_by_star_id(star.star_id)
            flag = str(star.ts)
            if com:
                data['items'].append(com)
        if len(stars) >= FALL_PER_PAGE_NUM:
            data['flag'] = flag
        return '', data

