# -*- coding:utf-8 -*-

from hichao.comment.models.comment import get_comment_count
from hichao.user.models.refused_user import user_in_black_list
from hichao.forum.models.star_user import user_is_staruser
from hichao.cache import get_cache_client
from hichao.base.config import (
        COMMENT_TYPE_TOPIC,
        COMMENT_TYPE_DICT,
        )
from hichao.base.config.ui_action_type import (
        STAR_DETAIL,
        THREAD_DETAIL,
        )
from hichao.comment import COMMENT_STATUS
from hichao.util.content_util import (
        content_has_sensitive_words,
        content_has_urls,
        )

import functools
import md5
import time
import datetime
from hichao.forum.models.pv import thread_pv_count, topic_pv_count
from hichao.topic.config import TOPIC_PV_PREFIX, TOPIC_UV_PREFIX
from hichao.base.lib.redis import redis
from hc.redis.count import Counter, SetCounter
from hichao.theme.config import THEME_PV_PREFIX
from hichao.collect.models.fake import collect_count_new

comment_counter = get_comment_count
cache_client = get_cache_client()
support_actions = [STAR_DETAIL, THREAD_DETAIL]

def build_comment_count(comment_type = COMMENT_TYPE_TOPIC, more_actions = False):
    def _(func):
        @functools.wraps(func)
        def __(*args, **kw):
            obj = func(*args, **kw)
            if not obj: return obj
            if obj.has_key('id'):
                obj['commentCount'] = str(comment_counter(COMMENT_TYPE_DICT[comment_type], obj['id']))
            else:
                count = str(comment_counter(COMMENT_TYPE_DICT[comment_type], obj['component']['id']))
                obj['component']['commentCount'] = count
                if more_actions:
                    for action in obj['component']['actions']:
                        if not action: continue
                        if action['actionType'] not in support_actions: continue
                        action['commentCount'] = count
                else:
                    obj['component']['action']['commentCount'] = count
            return obj
        return __
    return _

def comment_is_illegal(user_id, comment):
    if comment.strip() == '':
        return COMMENT_STATUS.TYPE.EMPTY_CONTENT
    if content_has_urls(comment):
        if not user_is_staruser(user_id):
            return COMMENT_STATUS.TYPE.HAS_URL
    if too_fast_comment(user_id):
        return COMMENT_STATUS.TYPE.TOO_FAST
    sensitive_status = content_has_sensitive_words(comment)
    if sensitive_status == 1:
        # 未通过审核
        return COMMENT_STATUS.TYPE.UNAPPROVED
        #return COMMENT_STATUS.TYPE.REFUSED
    elif sensitive_status == 2:
        return COMMENT_STATUS.TYPE.CENSORING
    if user_in_black_list(user_id):
        return COMMENT_STATUS.TYPE.REFUSED
    #if too_long_comment(user_id, comment):
    #    return COMMENT_STATUS.TYPE.REFUSED
    #if same_comment(user_id, comment):
    #    return COMMENT_STATUS.TYPE.REFUSED
    return COMMENT_STATUS.TYPE.NORMAL

def same_comment(user_id, comment):
    mstr = "{0}{1}".format(user_id, comment)
    key = md5.new(mstr).hexdigest()
    res = cache_client.get(key)
    if res:
        return True
    else:
        cache_client.setex(key, 10, time.time())
        return False

def too_long_comment(user_id, comment):
    if len(comment) < 40:
        return False
    key = 'too_long_' + str(user_id)
    res = cache_client.get(key)
    if res is not None:
        return True
    else:
        cache_client.setex(key, 120, 1)
        return False

def too_fast_comment(user_id):
    mstr = 'user_comment_times_' + str(user_id)
    key = md5.new(mstr).hexdigest()
    res = cache_client.get(key)
    comment_limit_num = 5
    if datetime.datetime.now().hour < 7:
        comment_limit_num = 1
    if res is not None:
        res = int(res)
        if res > comment_limit_num:
            return True
        else:
            cache_client.setex(key, 60, res + 1)
            return False
    else:
        cache_client.setex(key, 60, 1)
        return False

def build_view_count(more_actions = False):
    def _(func):
        @functools.wraps(func)
        def __(*args, **kw):
            _obj = func(*args, **kw)
            if not _obj:
                return _obj
            if _obj['component']['componentType'] == 'topic':
                pv_key = TOPIC_PV_PREFIX.format(_obj['component']['id'])
                if _obj['component']['collectionType'] == 'topic':
                    pv_key = TOPIC_PV_PREFIX.format(_obj['component']['id'])
                if _obj['component']['collectionType'] == 'theme':
                    pv_key = THEME_PV_PREFIX.format(_obj['component']['id'])
                pv_counter = Counter(redis)
                cnt = pv_counter._byID(pv_key)
                if not cnt: cnt = 0
                if _obj['component']['collectionType'] == 'topic':
                    cnt = int(cnt) + int(collect_count_new(_obj['component']['id'],350,float(_obj['component']['unixtime'])))
                if _obj['component']['collectionType'] == 'theme':
                    cnt = int(cnt) + int(collect_count_new(_obj['component']['id'],300,float(_obj['component']['unixtime'])))
                _obj['component']['v'] = str(cnt)
                
            elif _obj['component']['componentType'] == 'fallLiteSubjectCell':
                cnt = str(thread_pv_count(_obj['component']['id']))
                cnt = int(cnt) + int(collect_count_new(_obj['component']['id'],150,float(_obj['component']['unixtime'])))
                _obj['component']['v'] = str(cnt)
                    
            return _obj
        return __
    return _

def build_view_topic_detail_count(more_actions = False):
    def _(func):
        @functools.wraps(func)
        def __(*args, **kw):
            _obj = func(*args, **kw)
            if not _obj:
                return _obj
            pv_key = TOPIC_PV_PREFIX.format(_obj['id'])
            pv_counter = Counter(redis)
            cnt = pv_counter._byID(pv_key)
            if not cnt: cnt = 0
            cnt = int(cnt) + int(collect_count_new(_obj['id'],350,float(_obj['unixtime'])))
            _obj['v'] = str(cnt)
            return _obj
        return __
    return _
