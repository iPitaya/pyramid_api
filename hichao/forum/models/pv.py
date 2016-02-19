#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from hichao.base.lib.redis import redis, redis_key, redis_slave
from hichao.util.statsd_client import timeit
from hichao.topic.config import TOPIC_PV_PREFIX
from hc.redis.count import Counter

timer = timeit('hichao_backend.m_forum_pv')

REDIS_THREAD_PV = redis_key.ThreadPV() 
REDIS_THREAD_FAKE_PV = redis_key.ThreadFakePV()
REDIS_TAG_THREAD_COUNT = redis_key.TagThreadCount()
REDIS_TAG_COMMENT_COUNT = redis_key.TagCommentCount()

@timer
def thread_pv_incr(item_id):
    return redis.hincrby(REDIS_THREAD_PV, item_id, 1)

@timer
def tag_thread_count_incr(item_id,incr=1):
    return redis.hincrby(REDIS_TAG_THREAD_COUNT, item_id, incr)

@timer
def tag_comment_count_incr(item_id, incr=1):
    return redis.hincrby(REDIS_TAG_COMMENT_COUNT, item_id, incr)

@timer
def tag_thread_count(item_id):
    count = redis_slave.hget(REDIS_TAG_THREAD_COUNT,item_id)
    if not count:
        count = 0
    return int(count)

@timer
def tag_comment_count(item_id):
    count = redis_slave.hget(REDIS_TAG_COMMENT_COUNT,item_id)
    if not count:
        count = 0
    return int(count)

@timer
def thread_pv_count(item_id):
    real_pv = redis_slave.hget(REDIS_THREAD_PV, item_id)
    fake_pv = redis_slave.hget(REDIS_THREAD_FAKE_PV, item_id)
    if not real_pv: real_pv = 0
    if not fake_pv: fake_pv = 0
    return int(real_pv) + int(fake_pv)

@timer
def topic_pv_count(item_id):
    pv_key = TOPIC_PV_PREFIX.format(item_id)
    pv_counter = Counter(redis)
    cnt = pv_counter._byID(pv_key)
    if not cnt: cnt = 0
    return cnt

if __name__ == "__main__":
    pass

