#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hichao.util.statsd_client import statsd
import time
import datetime
from hichao.base.lib.redis import redis, redis_key, redis_slave
from hichao.collect.models.fake import collect_count
from hichao.collect.models.db import Base, sync_dbsession_generator
from hichao.forum.models.thread import get_thread_category_id
from hichao.util.statsd_client import timeit

from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    func
)
from sqlalchemy.exc import IntegrityError

import transaction

REDIS_THREAD_COL_BY_CATEGORY_ID = redis_key.ThreadCollectByCategoryId('%s')
REDIS_THREAD_COL_BY_USER_ID = redis_key.ThreadCollectByUserId('%s')
REDIS_THREAD_COL_USER_BY_THREAD_ID = redis_key.ThreadCollectUserByThreadId(
    '%s')
REDIS_THREAD_COL_COUNT = redis_key.ThreadCollectCount()
REDIS_THREAD_COL_COUNT_BY_USER_ID = redis_key.ThreadCollectCountByUserId()
REDIS_THREAD_COL_COUNT_ZSET = redis_key.ThreadCollectCountZset()

REDIS_THREAD_TOP_N = redis_key.ThreadTopN()
REDIS_THREAD_TOP_N_WEEKLY = redis_key.ThreadTopNWeekly()
REDIS_THREAD_PUBLISH_DAYS = redis_key.ThreadPublishDays()

timer = timeit('hichao_backend.m_collect_thread')


class CollectThread(Base):
    __tablename__ = 'thread'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    thread_id = Column(Integer)
    created_at = Column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.current_timestamp())

# redis.delete(REDIS_THREAD_COL_COUNT)


@timer
def thread_collect_new(user_id, thread_list, n=1):
    try:
        now = int(time.time())
        session = sync_dbsession_generator()
        thread_ids = [int(id) for id in thread_list]
        collected_ids = session.query(CollectThread.thread_id).filter(CollectThread.user_id == int(user_id)).filter(CollectThread.thread_id.in_(thread_ids)).all()
        collected_ids = [int(id[0]) for id in collected_ids]
        uncollected_ids = [id for id in thread_ids if id not in collected_ids]
        uncollected_threads = []
        for thread_id in uncollected_ids:
            thread = CollectThread()
            thread.user_id = user_id
            thread.thread_id = thread_id
            thread.created_at = datetime.datetime.now() 
            uncollected_threads.append(thread)
        session.add_all(uncollected_threads)
        transaction.commit()
        with redis.pipeline(transaction=False) as p:
            for thread_id in thread_ids:
                category_id = get_thread_category_id(thread_id)
                p.zincrby(
                    REDIS_THREAD_COL_BY_CATEGORY_ID %
                    category_id,
                    thread_id,
                    n)
                p.zadd(
                    REDIS_THREAD_COL_USER_BY_THREAD_ID %
                    thread_id,
                    now,
                    user_id)
                p.zadd(REDIS_THREAD_COL_BY_USER_ID % user_id, now, thread_id)
                p.zincrby(REDIS_THREAD_COL_COUNT_ZSET, thread_id, n)
                p.hincrby(REDIS_THREAD_COL_COUNT, thread_id, n)
                p.hincrby(REDIS_THREAD_COL_COUNT_BY_USER_ID, user_id, n)
            p.execute()
    except IntegrityError:
        transaction.abort()
        return 0
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        return 0 
    finally:
        session.close()
    return 1

@timer
def thread_collect_rm(user_id, category_id, thread_id):
    session = sync_dbsession_generator()
    try:
        session.query(
            CollectThread).filter(
            CollectThread.user_id == user_id,
            CollectThread.thread_id == thread_id).delete(
        )
        transaction.commit()
        with redis.pipeline(transaction=False) as p:
            p.zrem(REDIS_THREAD_COL_USER_BY_THREAD_ID % thread_id, user_id)
            p.zrem(REDIS_THREAD_COL_BY_USER_ID % user_id, thread_id)
            p.zincrby(
                REDIS_THREAD_COL_BY_CATEGORY_ID %
                category_id,
                thread_id,
                -1)
            p.zincrby(REDIS_THREAD_COL_COUNT_ZSET, thread_id, -1)
            p.hincrby(REDIS_THREAD_COL_COUNT, thread_id, -1)
            p.execute()
    except Exception, ex:
        transaction.commit()
        print Exception, ex
        return 0
    return 1

@timer
def thread_user_has_item(user_id, thread_id):
    return redis_slave.zscore(REDIS_THREAD_COL_BY_USER_ID % user_id, thread_id)

@timer
def thread_top_list_by_category(category_id, offset=0, limit=18, reverse=0):
    key = REDIS_THREAD_COL_BY_CATEGORY_ID % category_id
    try:
        if reverse == 0:
            _list = redis_slave.zrevrange(
                key,
                offset,
                offset +
                limit,
                withscores=True)
        else:
            _list = redis_slave.zrange(key, offset, offset + limit, withscores=True)
        return _list
    except Exception, ex:
        print Exception, ex
    return []


@timer
def thread_top_list_all(offset=0, limit=18, reverse=0):
    key = REDIS_THREAD_COL_COUNT_ZSET
    try:
        if reverse == 0:
            _list = redis_slave.zrevrange(
                key,
                offset,
                offset +
                limit,
                withscores=True)
        else:
            _list = redis_slave.zrange(key, offset, offset + limit, withscores=True)
        return _list
    except Exception, ex:
        print Exception, ex
    return []


@timer
def thread_collect_user_list_by_thread_id(
        thread_id, offset=0, limit=18, reverse=0):
    key = REDIS_THREAD_COL_USER_BY_THREAD_ID % thread_id
    try:
        if reverse == 0:
            _list = redis_slave.zrevrange(
                key,
                offset,
                offset +
                limit,
                withscores=True)
        else:
            _list = redis_slave.zrange(key, offset, offset + limit, withscores=True)
        return _list

    except Exception, ex:
        print Exception, ex
    return []


@timer
def thread_collect_list_by_user_id(user_id, offset=0, limit=18, reverse=0):
    key = REDIS_THREAD_COL_BY_USER_ID%user_id
    try:
       if reverse == 0:
           _list = redis_slave.zrevrange(key, offset, offset+limit)
       else:
           _list = redis_slave.zrange(key, offset, offset+limit)
       return _list

    except Exception, ex:
       print Exception, ex
       return []
    #session = sync_dbsession_generator()
    #l = []
    #if limit == -1:
    #    limit = thread_count_by_user_id(user_id)
    #try:
    #    l = session.query(
    #        CollectThread).filter(
    #        CollectThread.user_id == user_id).order_by(
    #        CollectThread.created_at.desc()).offset(
    #        offset).limit(
    #        limit).all(
    #    )
    #except Exception, ex:
    #    print Exception, ex
    #finally:
    #    session.close()
    #return [item.thread_id for item in l]

@timer
def thread_user_count(thread_id, ts=1):
    s = redis_slave.hget(REDIS_THREAD_COL_COUNT, thread_id)
    # return  collect_count(thread_id, s, ts)
    return s

@timer
def thread_count_by_user_id(user_id):
    return redis_slave.zcard(REDIS_THREAD_COL_BY_USER_ID % user_id)
    #session = sync_dbsession_generator()
    #try:
    #    c = redis.hget(REDIS_THREAD_COL_COUNT_BY_USER_ID, user_id)
    #    if not c:
    #        count = session.query(
    #            CollectThread).filter(
    #            CollectThread.user_id == user_id).count(
    #        )
    #        c = count
    #        redis.hset(REDIS_THREAD_COL_COUNT_BY_USER_ID, user_id, c)
    #    return c
    #except Exception, ex:
    #    print Exception, ex
    #    return 0
    #finally:
    #    session.close()
def get_thread_collect_status(thread_id, user_id):
    result = 0
    session = sync_dbsession_generator()
    items = session.query(CollectThread.thread_id).filter(CollectThread.user_id == int(user_id)).filter(CollectThread.thread_id==thread_id).first()
    if items:
        result = 1
    return result
