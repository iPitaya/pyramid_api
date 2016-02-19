#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
from hichao.base.lib.redis import redis, redis_key, redis_slave
from hichao.collect.models.db import Base, sync_dbsession_generator
from hichao.collect.models.fake import collect_count
from hichao.util.statsd_client import timeit
from hichao.base.config import COLLECTION_TYPE

from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    func
)
from sqlalchemy.exc import IntegrityError

import transaction

REDIS_TOPIC_COL_TOP = redis_key.TopicCollect()
REDIS_TOPIC_COL_BY_USER_ID = redis_key.TopicCollectByUserId('%s')
REDIS_TOPIC_COL_USER_BY_TOPIC_ID = redis_key.TopicCollectUserByTopicId('%s')
REDIS_TOPIC_COL_COUNT = redis_key.TopicCollectCount()
REDIS_TOPIC_COL_COUNT_BY_USER_ID = redis_key.TopicCollectCountByUserId()
#REDIS_TOPIC_COL_COUNT_ZSET  = redis_key.TopicCollectCountZset()
REDIS_TOPIC_COL_BY_CATEGORY_ID = redis_key.TopicCollectByCategoryId('%s')
REDIS_MIX_TOPIC_COL_BY_USER_ID = redis_key.MixTopicCollectByUserId('%s')

timer = timeit('hichao_backend.m_collect_topic')


class CollectTopic(Base):

    __tablename__ = 'topic'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    topic_id = Column(Integer)
    created_at = Column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.current_timestamp())

@timer
def topic_collect_new(user_id, topic_list, n=1):
    category_id = 1
    try:
        now = int(time.time())
        session = sync_dbsession_generator()
        topic_ids = [int(id) for id in topic_list]
        collected_ids = session.query(CollectTopic.topic_id).filter(CollectTopic.user_id == int(user_id)).filter(CollectTopic.topic_id.in_(topic_ids)).all()
        collected_ids = [int(id[0]) for id in collected_ids]
        uncollected_ids = [id for id in topic_ids if id not in collected_ids]
        uncollected_topics = []
        for topic_id in uncollected_ids:
            topic = CollectTopic()
            topic.user_id = user_id
            topic.topic_id = topic_id 
            topic.created_at = datetime.datetime.now() 
            uncollected_topics.append(topic)
        session.add_all(uncollected_topics)
        transaction.commit()
        with redis.pipeline(transaction=False) as p:
            for topic_id in topic_ids:
                p.zincrby(REDIS_TOPIC_COL_TOP, topic_id, n)
                p.zincrby(
                    REDIS_TOPIC_COL_BY_CATEGORY_ID %
                    category_id,
                    topic_id,
                    n)
                p.zadd(
                    REDIS_TOPIC_COL_USER_BY_TOPIC_ID %
                    topic_id,
                    now,
                    user_id)
                p.zadd(REDIS_TOPIC_COL_BY_USER_ID % user_id, now, topic_id)
                p.zadd(REDIS_MIX_TOPIC_COL_BY_USER_ID % user_id, now, '{0}:{1}'.format(COLLECTION_TYPE.CODE[COLLECTION_TYPE.TOPIC], topic_id))
                p.hincrby(REDIS_TOPIC_COL_COUNT, topic_id, n)
                p.hincrby(REDIS_TOPIC_COL_COUNT_BY_USER_ID, user_id, n)
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
def topic_collect_rm(user_id, category_id, topic_id):
    session = sync_dbsession_generator()

    try:
        session.query(
            CollectTopic).filter(
            CollectTopic.user_id == user_id,
            CollectTopic.topic_id == topic_id).delete(
        )
        with redis.pipeline(transaction=False) as p:
            p.zrem(REDIS_TOPIC_COL_USER_BY_TOPIC_ID % topic_id, user_id)
            p.zrem(REDIS_MIX_TOPIC_COL_BY_USER_ID % user_id, '{0}:{1}'.format(COLLECTION_TYPE.CODE[COLLECTION_TYPE.TOPIC], topic_id))
            p.zrem(REDIS_TOPIC_COL_BY_USER_ID % user_id, topic_id)
            p.zincrby(REDIS_TOPIC_COL_TOP, topic_id, -1)
            p.zincrby(
                REDIS_TOPIC_COL_BY_CATEGORY_ID %
                category_id,
                topic_id,
                -1)
            p.execute()
        transaction.commit()
    except Exception, ex:
        print Exception, ex
        return False 
    finally:
        session.close()
    return True 

@timer
def topic_user_has_item(user_id, topic_id):
    # 因为大部分专题或明星图用户是没有收藏的，所以没有走mysql
    return redis_slave.zscore(REDIS_TOPIC_COL_BY_USER_ID % user_id, topic_id)

@timer
def topic_top_list(offset=0, limit=18, reverse=0):
    key = REDIS_TOPIC_COL_TOP
    try:
        if reverse == 0:
            _list = redis_slave.zrevrange(
                key,
                offset,
                offset + limit,
                withscores=True)
        else:
            _list = redis_slave.zrange(key, offset, offset + limit, withscores=True)
        return _list
    except Exception, ex:
        print Exception, ex
    return []


@timer
def topic_top_list_by_category(category_id, offset=0, limit=18, reverse=0):
    key = REDIS_TOPIC_COL_BY_CATEGORY_ID % category_id
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
def topic_collect_user_list_by_topic_id(
        topic_id, offset=0, limit=18, reverse=0):
    key = REDIS_TOPIC_COL_USER_BY_TOPIC_ID % topic_id
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
        return 0


@timer
def topic_collect_list_by_user_id(user_id, offset=0, limit=18, reverse=0):
    key = REDIS_TOPIC_COL_BY_USER_ID%user_id
    try:
       if reverse == 0:
           _list = redis_slave.zrevrange(key, offset, offset+limit)
       else:
           _list = redis_slave.zrange(key, offset, offset+limit)
       return _list

    except Exception, ex:
       print Exception, ex
       return 0

    #session = sync_dbsession_generator()
    #l = []
    #if limit == -1:
    #    limit = topic_count_by_user_id(user_id)
    #try:
    #    l = session.query(
    #        CollectTopic).filter(
    #        CollectTopic.user_id == user_id).order_by(
    #        CollectTopic.created_at.desc()).offset(
    #        offset).limit(
    #        limit).all(
    #    )
    #except Exception, ex:
    #    print Exception, ex
    #finally:
    #    session.close()
    #return [item.topic_id for item in l]

@timer
def topic_user_count(topic_id, ts=1):
    session = None
    c = 0
    try:
        c = redis_slave.hget(REDIS_TOPIC_COL_COUNT, topic_id)
        if c: c = int(c)
        else: c = 0
        if not c:
            session = sync_dbsession_generator()
            count = session.query(
                CollectTopic).filter(
                CollectTopic.topic_id == topic_id).count(
            )
            c = count
            # set redis
            r = redis.hset(REDIS_TOPIC_COL_COUNT, topic_id, c)
    except Exception, ex:
        print Exception, ex
    finally:
        if session: session.close()
    return collect_count(topic_id, c, ts)

@timer
def topic_count_by_user_id(user_id):
    return redis_slave.zcard(REDIS_TOPIC_COL_BY_USER_ID % user_id)
    #session = sync_dbsession_generator()
    #try:
    #    c = redis.hget(REDIS_TOPIC_COL_COUNT_BY_USER_ID, user_id)
    #    if not c:
    #        count = session.query(
    #            CollectTopic).filter(
    #            CollectTopic.user_id == user_id).count(
    #        )
    #        c = count
    #        redis.hset(REDIS_TOPIC_COL_COUNT_BY_USER_ID, user_id, c)
    #    return c
    #except Exception, ex:
    #    print Exception, ex
    #    return 0
    #finally:
    #    session.close()

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
