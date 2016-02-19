#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from hichao.base.lib.redis import redis, redis_key
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_forum_uv')

REDIS_THREAD_UV = redis_key.ThreadUV('%s') 

@timer
def thread_uv_incr(user_id, item_id):
    return redis.sadd(REDIS_THREAD_UV%item_id, user_id)

@timer
def thread_uv_count(item_id):
    return redis.scard(REDIS_THREAD_UV%item_id)

if __name__ == "__main__":
    pass

