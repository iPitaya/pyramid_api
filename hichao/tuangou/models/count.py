#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from hichao.base.lib.redis import redis, redis_key
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_tuangou_count')

REDIS_TUANGOU_ATTEND_COUNT = redis_key.TuanGouAttendCount('%s') 
REDIS_TUANGOU_SKU_ATTEND_COUNT = redis_key.TuanGouAttendCount('%s') 

@timer
def tuangou_attend_new(user_id, item_id):
    return redis.sadd(REDIS_TUANGOU_ATTEND_COUNT%item_id, user_id)

@timer
def tuangou_attend_count(item_id):
    return redis.scard(REDIS_TUANGOU_ATTEND_COUNT%item_id)

@timer
def tuangou_sku_attend_new(user_id, item_id):
    return redis.sadd(REDIS_TUANGOU_SKU_ATTEND_COUNT%item_id, user_id)

@timer
def tuangou_sku_attend_count(item_id):
    return redis.scard(REDIS_TUANGOU_SKU_ATTEND_COUNT%item_id)

if __name__ == "__main__":
    pass

