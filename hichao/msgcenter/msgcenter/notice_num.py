#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hichao.base.lib.redis import redis, redis_key, redis_slave

REDIS_NOTICE_MSG_COUNT = redis_key.NoticeMsgCount()
REDIS_NOTICE_COMMENT_COUNT = redis_key.NoticeCommentCount()
REDIS_NOTICE_LIKE_COUNT = redis_key.NoticeLikeCount()
REDIS_THREAD_COL_COUNT  = redis_key.ThreadCollectCount()

REDIS_NOTICE_MSG_ALL_TS_BY_UID = redis_key.NoticeMsgAllTsByUid()

NOTICE_COUNT = dict(
    msg = REDIS_NOTICE_MSG_COUNT,
    comment = REDIS_NOTICE_COMMENT_COUNT,
    like = REDIS_NOTICE_LIKE_COUNT,
    )

def notice_new(user_id, type):
    redis.hincrby(NOTICE_COUNT[type], user_id)


def notice_rm(user_id, type):
    redis.hset(NOTICE_COUNT[type], user_id, 0)

def notice_count(user_id, type):
    redis_slave.hget(NOTICE_COUNT[type], user_id)

def msg_all_ts_by_uid_new(user_id, ts):
    redis.hset(REDIS_NOTICE_MSG_ALL_TS_BY_UID, user_id, ts)

def thread_user_count(thread_id):
    return  redis_slave.hget(REDIS_THREAD_COL_COUNT, thread_id)

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

