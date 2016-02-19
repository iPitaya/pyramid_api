# -*- coding: utf-8 -*- 
from hichao.base.lib.redis import redis, redis_key
from hichao.util.statsd_client import timeit
from hichao.collect.models.fake import collect_count
timer = timeit('hichao_backend.m_flashsale_count')
REDIS_FLASHSALE_ATTEND_COUNT = redis_key.FlashSaleAttendCount('%s') 
@timer
def flashsale_attend_new(user_id, item_id):
    ''' redis 存放 有多少登录用户访问了该单品  '''
    return redis.sadd(REDIS_FLASHSALE_ATTEND_COUNT%item_id, user_id)

@timer
def flashsale_attend_count(item_id):
    ''' 获得该单品被多少登录用户访问 '''
    return redis.scard(REDIS_FLASHSALE_ATTEND_COUNT%item_id)

def get_peopleCount_by_sku_id(sku_id,publish_time):
    ''' 计算peopleCount 通过某些方式  '''
    #count = flashsale_attend_count(int(sku_id))
    count = collect_count(int(sku_id)%1000087, int(sku_id)%67, publish_time) + 1024
    return count
