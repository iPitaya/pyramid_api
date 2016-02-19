#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import math
from hichao.base.lib.redis import redis, redis_key, redis_slave
from hichao.collect.models.thread import REDIS_THREAD_TOP_N, REDIS_THREAD_PUBLISH_DAYS, \
        REDIS_THREAD_COL_COUNT, REDIS_THREAD_COL_COUNT_ZSET, REDIS_THREAD_TOP_N_WEEKLY
from hichao.forum.models.thread import get_thread_by_id
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_collect_thread_top')

thread_top_n_lua = """
    local pow = math.pow
    local floor = math.floor
    local T = 5 
    local ONE_DAY_SECOND = 60 * 60 * 24
    local today_days = floor(ARGV[1] /ONE_DAY_SECOND)

    local star_count_list = redis.call('HGETALL', KEYS[1])

    for k, v in pairs(star_count_list) do
        local days = redis.call('HGET', KEYS[2], k)
        if days then
            local t = today_days - days
            local N = redis.call('hget', KEYS[1], k)
            if type(N) ~= 'boolean' then
                local n  = N * (0.5^(t/T))
                local ok = redis.call('ZADD', KEYS[3], n, k)
            end
        end
    end

   """


_THREAD_TOP_N = redis.register_script(thread_top_n_lua)

@timer
def _thread_top_n():
    print 'thread', time.strftime('%Y-%m-%d %H:%M:%S')
    return _THREAD_TOP_N(keys=[REDIS_THREAD_COL_COUNT, REDIS_THREAD_PUBLISH_DAYS, REDIS_THREAD_TOP_N], args=[time.time()]) 

@timer
def thread_top_n_hourly_by_python(key, start=1, end=20, s=55):
    #m = (M – 1) / (t + 2)^1.5 
    #redis.delete(key)
    start = start * 24
    end = end * 24
    thread_count_list = redis_slave.hgetall(REDIS_THREAD_COL_COUNT)
    for k, v in thread_count_list.iteritems():
        thread = get_thread_by_id(k)

        if thread:
            t = time.time()- float(time.mktime(thread.ts.timetuple()))
            t = t /3600
            if v and int(v) >= s and start <= t <= end:
                print v, '*'*20
                n = int(v) / pow(t+2, 1.8)
                print key, 'start:', start, 't:',t, 'end:', end, 'k:', k,'v:', v,'n:', n, '*'*20
                p = redis.zadd(key, n, k)
            else:
                p = redis.zrem(key, k)   
                pass
                #print k, t, v, '#'*20

@timer
def thread_top_n(offset=0, limit=20, reverse=0):
    key = REDIS_THREAD_TOP_N
    return redis_slave.zrevrange(key, offset, offset+limit, withscores=True)

@timer
def thread_top_n_weekly(offset=0, limit=20, reverse=0):
    key = REDIS_THREAD_TOP_N_WEEKLY
    return redis_slave.zrevrange(key, offset, offset+limit, withscores=True)

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
    thread_top_n_hourly_by_python(REDIS_THREAD_TOP_N)
    thread_top_n_hourly_by_python(REDIS_THREAD_TOP_N_WEEKLY, start=3, end=9, s=30)
    #for i in thread_top_n():
    #    print redis.hget(REDIS_THREAD_COL_COUNT, i[0])
    #print thread_top_n_weekly()

