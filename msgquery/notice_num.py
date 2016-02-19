#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hichao.base.lib.redis import redis, redis_key

REDIS_NOTICE_MSG_COUNT = redis_key.NoticeMsgCount()
REDIS_NOTICE_COMMENT_COUNT = redis_key.NoticeCommentCount()
REDIS_NOTICE_LIKE_COUNT = redis_key.NoticeLikeCount()

REDIS_NOTICE_MSG_ALL_COUNT = redis_key.NoticeMsgAllCount()

REDIS_NOTICE_MSG_ALL_TS_BY_UID = redis_key.NoticeMsgAllTsByUid()

NOTICE_COUNT = dict(
    msg = REDIS_NOTICE_MSG_COUNT,
    comment = REDIS_NOTICE_COMMENT_COUNT,
    like = REDIS_NOTICE_LIKE_COUNT,
    )

NOTICE_COUNT_CN = dict(
    msg = 'msgCount',
    comment = 'commentCount',
    like = 'likeCount',
)

def notice_new(user_id, _type):
    redis.hincrby(NOTICE_COUNT[_type], user_id)

def notice_rm(user_id, _type):
    redis.hset(NOTICE_COUNT[_type], user_id, 0)

def notice_count(user_id, _type):
    count = redis.hget(NOTICE_COUNT[_type], user_id)
    if count:
        return count
    else:
        return 0

def msg_all_new(item_id, ts):
    redis.zadd(REDIS_NOTICE_MSG_ALL_COUNT, item_id, ts)

def msg_all_count(ts):
    return redis.zcount(REDIS_NOTICE_MSG_ALL_COUNT, ts, 2147483648)

def msg_all_ts_by_uid_new(user_id, ts):
    redis.hset(REDIS_NOTICE_MSG_ALL_TS_BY_UID, user_id, ts)

def msg_all_ts_by_uid(user_id):
    return redis.hget(REDIS_NOTICE_MSG_ALL_TS_BY_UID, user_id)

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
