#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import transaction
import traceback
from multiprocessing.dummy import Pool as ThreadPool

from hichao.base.lib.redis import redis, redis_key
from hichao.collect.models.db import Base, sync_dbsession_generator

from sqlalchemy import func

# 从Redis转到mysql
# star, sku, topic, thread

# Begin star

from hichao.collect.models.star import (
    CollectStar,
    REDIS_STAR_COL_BY_USER_ID,
    REDIS_STAR_COL_USER_BY_STAR_ID,
    REDIS_STAR_COL_COUNT,
    REDIS_STAR_COL_COUNT_BY_USER_ID,
)


def star_collect_list_by_user_id(user_id, offset=0, limit=18, reverse=0):
    key = REDIS_STAR_COL_BY_USER_ID % user_id
    if reverse ==0:
      _list = redis.zrevrange(key, offset, offset+limit, withscores=True)
    else:
      _list = redis.zrange(key, offset, offset+limit, withscores=True)
    return _list

def star_collect_trans(user_id, star_id, created_at):

    session = sync_dbsession_generator()
    star = CollectStar()
    s = None
    star.user_id = user_id
    star.star_id = star_id
    star.created_at = func.from_unixtime(created_at)

    try:
        session.add(star)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        traceback.print_exc()
        return None
    finally:
        session.close()

# Begin sku
from hichao.collect.models.sku import (
    CollectSku,
    REDIS_SKU_COL_USER_BY_SKU_ID,
    REDIS_SKU_COL_BY_USER_ID,
    REDIS_SKU_COL_COUNT,
    REDIS_SKU_COL_COUNT_BY_USER_ID,
)

def sku_collect_list_by_user_id(user_id, offset=0, limit=18, reverse=0):
    key = REDIS_SKU_COL_BY_USER_ID % user_id
    # zrange / zrevrange bounds are inclusive
    if reverse == 0:
       _list = redis.zrevrange(key, offset, offset+limit-1, withscores=True)
    else:
       _list = redis.zrange(key, offset, offset+limit-1, withscores=True)
    return _list

def sku_collect_trans(user_id, sku_id, created_at):

    session = sync_dbsession_generator()
    sku = CollectSku()
    s = None
    sku.user_id = user_id
    sku.sku_id = sku_id 
    sku.created_at = func.from_unixtime(created_at)

    try:
        session.add(sku)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        traceback.print_exc()
        return None
    finally:
        session.close()
    return sku

# Begin topic

from hichao.collect.models.topic import (
    CollectTopic,
    REDIS_TOPIC_COL_BY_USER_ID,
    REDIS_TOPIC_COL_USER_BY_TOPIC_ID,
    REDIS_TOPIC_COL_COUNT,
    REDIS_TOPIC_COL_COUNT_BY_USER_ID,
)

def topic_collect_list_by_user_id(user_id, offset=0, limit=18, reverse=0):
    key = REDIS_TOPIC_COL_BY_USER_ID%user_id
    try:
       if reverse == 0:
           _list = redis.zrevrange(key, offset, offset+limit, withscores=True)
       else:
           _list = redis.zrange(key, offset, offset+limit, withscores=True)
       return _list

    except Exception, ex:
       print Exception, ex
       return 0

def topic_collect_trans(user_id, topic_id, created_at):
    session = sync_dbsession_generator()
    topic = CollectTopic()
    topic.user_id = user_id
    topic.topic_id = topic_id 
    topic.created_at = func.from_unixtime(created_at)
    try:
        session.add(topic)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        traceback.print_exc()
        return None
    finally:
        session.close()

# Begin Thread

from hichao.collect.models.thread import (
    CollectThread,
    REDIS_THREAD_COL_BY_USER_ID,
    REDIS_THREAD_COL_USER_BY_THREAD_ID,
    REDIS_THREAD_COL_COUNT,
    REDIS_THREAD_COL_COUNT_BY_USER_ID,
)

def thread_collect_list_by_user_id(user_id, offset=0, limit=18, reverse=0):
    key = REDIS_THREAD_COL_BY_USER_ID%user_id
    try:
       if reverse == 0:
           _list = redis.zrevrange(key, offset, offset+limit, withscores=True)
       else:
           _list = redis.zrange(key, offset, offset+limit, withscores=True)
       return _list

    except Exception, ex:
       print Exception, ex
       return []

def thread_collect_trans(user_id, thread_id, created_at):
    session = sync_dbsession_generator()
    thread = CollectThread()
    thread.user_id = user_id
    thread.thread_id = thread_id 
    thread.created_at = func.from_unixtime(created_at)

    try:
        session.add(thread)
        transaction.commit()
    except Exception as ex:
        transaction.abort()
        print Exception, ex
        traceback.print_exc()
        return None
    finally:
        session.close()

def trans(user_id):
    # star
    star_list = star_collect_list_by_user_id(user_id, 0, -1)
    for star_id, created_at in star_list:
        star_collect_trans(user_id, star_id, created_at)
    sku_list = sku_collect_list_by_user_id(user_id, 0, -1)
    for sku_id, created_at in sku_list:
        sku_collect_trans(user_id, sku_id, created_at)
    topic_list = topic_collect_list_by_user_id(user_id, 0, -1)
    for topic_id, created_at in topic_list:
        topic_collect_trans(user_id, topic_id, created_at)
    thread_list = thread_collect_list_by_user_id(user_id, 0, -1)
    for thread_id, created_at in thread_list:
        thread_collect_trans(user_id, thread_id, created_at)



if __name__ == "__main__":
    pool = ThreadPool(20)
    results = pool.map(trans, [x for x in xrange(6000, 1200000)])
    pool.close()
    pool.join()
