# -*- coding:utf-8 -*-
import redis
from hichao.cache import get_cache_client
import time
import datetime
#from hichao.base.config  import CACHE_CONFIG

#pool = redis.ConnectionPool(**CACHE_CONFIG)
#cache_client = redis.StrictRedis(connection_pool=pool)
cache_client = get_cache_client()

EXPIRED_TIME_OUT = 24*60*60
SEND_NUM = 5
SEND_NUM_NOTICE = 20

IMG_CODE_TIME_OUT = 10*60

def get_num_count_from_redis(key):
    key = 'count:' + key
    value = cache_client.get(key)
    if not value:
        EXPIRED_TIME_OUT = time.mktime((datetime.date.today()+datetime.timedelta(days =1)).timetuple()) - time.time()
        EXPIRED_TIME_OUT = int(EXPIRED_TIME_OUT)
        num = cache_client.setex(key, EXPIRED_TIME_OUT, SEND_NUM)
        value = SEND_NUM
    return value

def minus_num_from_redis(key):
    key = 'count:' + key
    value = cache_client.get(key)
    if value:
        if int(value) > 0:
            num = cache_client.incrby(key,-1)

def get_num_count_from_redis_notice(key):
    key = 'notice_count:' + key
    value = cache_client.get(key)
    if value:
        if int(value) > 0:
            num = cache_client.incrby(key,-1)
    else:
        EXPIRED_TIME_OUT = time.mktime((datetime.date.today()+datetime.timedelta(days =1)).timetuple()) - time.time()
        EXPIRED_TIME_OUT = int(EXPIRED_TIME_OUT)
        num = cache_client.setex(key, EXPIRED_TIME_OUT, SEND_NUM_NOTICE - 1)
        value = SEND_NUM_NOTICE - 1
    return value

def set_img_code_redis(key,code):
    key = 'img_code:'+key
    rl = cache_client.setex(key, IMG_CODE_TIME_OUT, code)
    print key,code,rl
    return rl

def get_img_code_redis(key):
    key = 'img_code:'+key
    value = cache_client.get(key)
    if value:
        cache_client.delete(key)
    return value
