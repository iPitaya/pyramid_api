# -*- coding: utf-8 -*-
import time
import math
from hichao.base.lib.redis import redis, redis_key, redis_slave, redis_slave_key
from hichao.collect.models.collect import  COLLECT_KEY_BY_TYPE
from hichao.collect.models.collect import REDIS_STAR_PUBLISH_DAYS, REDIS_STAR_TOP_N, REDIS_STAR_COL_COUNT,\
                    REDIS_STAR_PUBLISH_HOURS 
from hichao.star.models.star import get_star_by_star_id
from hichao.base.lib.timetool import day2days, today_days

#m = (M – 1) / (t + 2)^1.5 
star_top_n_hourly_lua = """
    local pow = math.pow
    local log = math.log
    local floor = math.floor
    local T = 5 
    local ONE_HOUR_SECOND = 60 * 60

    local star_count_list = redis.call('HGETALL', KEYS[1])

    for k, v in pairs(star_count_list) do
        local pub_ts  = redis.call('HGET', KEYS[2], k)
        if pub_ts then
            local t =  (floor(ARGV[1])- pub_ts)/ONE_HOUR_SECOND
            local N = redis.call('hget', KEYS[1], k)
            if type(N) ~= 'boolean' then
                local n  = log(N) /((t +2)^1.8)
                local ok = redis.call('ZADD', KEYS[3], n, k)
            end
        end
    end

   """

# m = M * (1/2) ^ (t/T)
star_top_n_daily_lua = """
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

_STAR_TOP_N_HOURLY = redis.register_script(star_top_n_hourly_lua)

def _star_top_n_hourly():
    redis.delete(REDIS_STAR_TOP_N)
    print time.strftime('%Y-%m-%d %H:%M:%S')
    ts = time.time()
    return _STAR_TOP_N_HOURLY(keys=[REDIS_STAR_COL_COUNT, REDIS_STAR_PUBLISH_HOURS, REDIS_STAR_TOP_N], args=[ts]) 

_STAR_TOP_N_DAILY = redis.register_script(star_top_n_daily_lua)

def _star_top_n_daily():
    print time.strftime('%Y-%m-%d %H:%M:%S')
    return _STAR_TOP_N_DAILY(keys=[REDIS_STAR_COL_COUNT, REDIS_STAR_PUBLISH_DAYS, REDIS_STAR_TOP_N], args=[time.time()]) 

def star_top_n(offset=0, limit=20, reverse=0):
    key = REDIS_STAR_TOP_N
    #top_n()
    return redis_slave.zrevrange(key, offset, offset+limit, withscores=True)

def star_pub_days(star_id):
    return redis_slave.hget(REDIS_STAR_PUBLISH_DAYS, star_id)

def star_pub_hours(star_id):
    return redis_slave.hget(REDIS_STAR_PUBLISH_HOURS, star_id)

def star_col_count(star_id):
    return redis_slave.hget(REDIS_STAR_COL_COUNT, star_id)

def star_top_n_score(star_id):
    return redis_slave.zscore(REDIS_STAR_TOP_N, star_id)

def star_top_n_daily_by_python():
    #redis.delete(REDIS_STAR_TOP_N)
    T = 5
    star_count_list = redis_slave.hgetall(REDIS_STAR_COL_COUNT)
    for k, v in star_count_list.iteritems():
        days = redis_slave.hget(REDIS_STAR_PUBLISH_DAYS, k)
        print  k, days , '*'*20
        if days:
            t = today_days() - int(days)
            if v:
                n = int(v)* pow(0.5, (t/T))
                redis.zadd(REDIS_STAR_TOP_N, k, n)
                if n > 1000:
                    print k, t, v, n, 'yes'
            else:
                print k, t, v, 'noo'

def star_top_n_hourly_by_python():
    #m = (M – 1) / (t + 2)^1.5 
    #redis.delete(REDIS_STAR_TOP_N)
    star_count_list = redis_slave.hgetall(REDIS_STAR_COL_COUNT)
    min_ts = int(time.time())
    for k, v in star_count_list.iteritems():
        pub_ts = redis_slave.hget(REDIS_STAR_PUBLISH_HOURS, k)

        if k and pub_ts:
            t = (time.time() - float(pub_ts))/3600
            if v:
                if int(v) >= 150 and 24 <= t <= 480:
                    if float(pub_ts) < min_ts: min_ts = pub_ts
                    n = int(v) / pow(t+2, 1.8)
                    p = redis.zadd(REDIS_STAR_TOP_N, n, k)
                else:
                    redis.zrem(REDIS_STAR_TOP_N, k)   
                    pass
                #print k, t, v, 'noo'
    print min_ts

def star_top_n_count():
    return redis_slave.zcard(REDIS_STAR_TOP_N)

def generate_star_publish_days():
    redis.delete(REDIS_STAR_PUBLISH_DAYS)
    a = []
    star_count_list = redis.hkeys(REDIS_STAR_COL_COUNT)
    for i in star_count_list:
        if i:
            star = get_star_by_star_id(i)
            if star:
                days = day2days(star.publish_date)
                redis.hset(REDIS_STAR_PUBLISH_DAYS, i, days)
            else:
                a.append(i) 
    

def generate_star_publish_hours():
    a = []
    star_count_list = redis.hkeys(REDIS_STAR_COL_COUNT) 
    for i in star_count_list:
        if i:
            try:
                i = int(i)
            except:
                continue
            if not i: continue
            star = get_star_by_star_id(i)
            if star:
                redis.hset(REDIS_STAR_PUBLISH_HOURS, i, star.publish_date)
            else:
                a.append(i) 
    print a

   

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
    generate_star_publish_hours()
    #generate_star_publish_days()
    #_star_top_n_hourly()
    star_top_n_hourly_by_python()
    #_star_top_n_daily()
    #star_top_n_by_python()
    #print star_pub_days(80968)
    #print star_pub_hours(80968)
    #print star_col_count(80968)
    #print star_top_n_score(80961)
    #print star_top_n()

