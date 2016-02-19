#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import time
import random
from hichao.base.lib.redis import redis, redis_key, redis_slave
from hichao.util.statsd_client import timeit

ONLINE_USERS = redis_key.ThreadOnlineUserByCategoryIdAndMinutes('%s-%s') 

ONLINE_LAST_MINUTES = 5

timer = timeit('hichao_backend.m_forum_online')

@timer
def set_online_user(user_id, category_id):
    now = int(time.time())
    expires = now + ONLINE_LAST_MINUTES * 60 + 10
    key = ONLINE_USERS % (category_id, now // 60)
    r1 = redis.sadd(key, user_id)
    r2 = redis.expireat(key, expires)
    

@timer
def _online_user_count(category_id):
    now = int(time.time()) // 60
    minutes = xrange(ONLINE_LAST_MINUTES)
    r = len(redis_slave.sunion( ONLINE_USERS % (category_id, now - x) for x in minutes))
    return r

@timer
def online_user_count(category_id):
    r = _online_user_count(category_id)
    r = r * 100 + random.randint(0, 99) + category_id
    return r




if __name__ == "__main__":
    pass

