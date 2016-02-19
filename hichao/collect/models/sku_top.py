#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import time
from datetime import datetime,timedelta
import math
from redis import StrictRedis 
from hc.redis.key import RedisKey
from hichao.base.config import REDIS_CONFIG 
from hichao.collect.models.collect import REDIS_SKU_COL_COUNT 
from hichao.sku.models.sku import get_sku_by_id, Sku, get_recommend_sku_ids
from hichao.base.lib.redis import redis, redis_key, redis_slave, redis_slave_key
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_collect_sku_top')

#REDIS_SKU_TOP_N = redis_key.SkuTopN()
#REDIS_SKU_TOP_N_PRE_RELEASE = redis_key.SkuTopNPreRelease()

REDIS_SKU_TOP_N_NEW = redis_key.SkuTopNNew()

#def sku_top_n_new(sku_id, next_id=-1):
#    key = REDIS_SKU_TOP_N
#    key_pre = REDIS_SKU_TOP_N_PRE_RELEASE
#    next_id = int(next_id)
#
#    p = redis.pipeline(transaction=False)
#    p.lrem(key_pre, 1, sku_id)
#    p.lrem(key, 1, sku_id)
#
#    if next_id < 0:
#        p.lpush(key, sku_id)
#    elif next_id == 0:
#        p.rpush(key, sku_id)
#    else:
#        p.linsert(key, 'BEFORE', next_id, sku_id)    
#
#    r = p.execute()
#
#def sku_top_n_rm(sku_id):
#    return redis.lrem(REDIS_SKU_TOP_N, 1, sku_id)
#
#def sku_top_n_pre_new(sku_id, next_id=-1):
#    key = REDIS_SKU_TOP_N_PRE_RELEASE
#    next_id = int(next_id)
#
#    p = redis.pipeline(transaction=False)
#    p.lrem(key, 1, sku_id)
#    if next_id < 0:
#        p.lpush(key, sku_id)
#    elif next_id == 0:
#        p.rpush(key, sku_id)
#    else:
#        p.linsert(key, 'BEFORE', next_id, sku_id)    
#    r = p.execute()
#
#def sku_top_n_pre_rm(sku_id):
#    return redis.lrem(REDIS_SKU_TOP_N_PRE_RELEASE, 1, sku_id)
#
#def sku_top_n_pre_2_pub():
#    key_pre = REDIS_SKU_TOP_N_PRE_RELEASE
#    pre_list = redis.lrange(key_pre, 0, -1)
#    for i in pre_list[::-1]:
#        sku_top_n_new(i, next_id=-1)
#    
#
#def sku_top_n(offset=0, limit=20):
#    key = REDIS_SKU_TOP_N
#    return redis.lrange(key, offset, offset+limit)
#
#def sku_top_n_pre_release(offset=0, limit=20):
#    key = REDIS_SKU_TOP_N_PRE_RELEASE
#    return redis.lrange(key, offset, offset+limit)

@timer
def sku_top_n_hourly_by_python(start=1, end=7, score=0):
    #m = (M – 1) / (t + 2)^1.5 
    key = REDIS_SKU_TOP_N_NEW
    #redis.delete(key)

    now = datetime.now()
    start = now - timedelta(days=9)  
    end  = now - timedelta(days=1)
    

    offset = 0
    limit = 100
    c = 0

    while True:
        print offset, limit, start, end, '*'*20
        sku_count_list = get_recommend_sku_ids(offset=offset, limit=limit, start_time=start, end_time=end)
        i = 0
        for sku_id, dt, came_from in sku_count_list:
            i += 1
            #id, datetime.datetime
            v = redis_slave.hget(REDIS_SKU_COL_COUNT, sku_id)
            if came_from == '编辑' and v and int(v) >= score:
                t = (time.time() - float(time.mktime(dt.timetuple())))/3600
                n = int(v) / pow(t+2, 1.8)
                p = redis.zadd(key, n, sku_id)
                print sku_id, v, n, '*'*20
                c += 1
            else:
                redis.zrem(key, k)   
                pass
        print i, '#'*30
        if  i == 100:
            offset += limit 
        else:
            break
    print c
            
            

@timer
def sku_top_n_count():
    return redis_slave.zcard(REDIS_SKU_TOP_N_NEW)

@timer
def sku_top_n(offset=0, limit=20, reverse=0):
    key = REDIS_SKU_TOP_N_NEW
    return redis_slave.zrevrange(key, offset, offset+limit, withscores=True)

@timer
def sku_top_n_test():
    _list = redis_slave.zrange(REDIS_SKU_TOP_N_NEW, 0, -1)
    for i in _list:
        n = redis_slave.hget(REDIS_SKU_COL_COUNT, i)
        if int(n) < 50:
            print i, n

    pass

if __name__ == "__main__":
    sku_top_n_hourly_by_python(start=1, end=15, score=15)
    #sku_top_n_test()
    pass

