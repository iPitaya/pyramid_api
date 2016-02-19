# -*- coding:utf-8 -*-

import time
import datetime
from hichao.base.lib.redis import (
        redis,
        redis_key,
        redis_slave,
        redis_slave_key,
        )
from hichao.collect.models.db import Base, sync_dbsession_generator
from hichao.collect.models.fake import collect_count

from sqlalchemy import (
        Column,
        Integer,
        TIMESTAMP,
        func,
        )
from sqlalchemy.exc import IntegrityError
from hichao.util.statsd_client import timeit

import transaction


REDIS_NEWS_COL_BY_USER_ID = redis_key.NewsCollectByUser('%s')
REDIS_NEWS_COL_USER_BY_NEWS_ID = redis_key.NewsCollectUserByNews('%s')
REDIS_NEWS_COL_COUNT = redis_key.NewsCollectCount()
REDIS_NEWS_COL_COUNT_BY_USER_ID = redis_key.NewsCollectCountByUserId()

timer = timeit('hichao_backend.m_collect_news')

class CollectNews(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    news_id = Column(Integer)
    created_at = Column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.current_timestamp())

@timer
def news_collect_new(user_id, news_ids):
    try:
        now = int(time.time())
        session = sync_dbsession_generator()
        news_ids = [int(id) for id in news_ids]
        collected_ids = session.query(CollectNews.news_id).filter(CollectNews.user_id == int(user_id)).filter(CollectNews.news_id.in_(news_ids)).all()
        collected_ids = [int(id[0]) for id in collected_ids]
        uncollected_ids = [id for id in news_ids if id not in collected_ids]
        uncollected_news = []
        for news_id in uncollected_ids:
            news = CollectNews()
            news.user_id = user_id
            news.news_id = news_id
            news.created_at = datetime.datetime.now()
            uncollected_news.append(news)
        session.add_all(uncollected_news)
        transaction.commit()
        with redis.pipeline(transaction = False) as p:
            for news_id in news_ids:
                p.zadd(REDIS_NEWS_COL_BY_USER_ID % user_id, now, news_id)
                p.zadd(REDIS_NEWS_COL_USER_BY_NEWS_ID % news_id, now, user_id)
                p.hincrby(REDIS_NEWS_COL_COUNT, news_id, 1)
                p.hincrby(REDIS_NEWS_COL_COUNT_BY_USER_ID, user_id, 1)
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
def news_collect_rm(user_id, news_id):
    session = sync_dbsession_generator()
    try:
        session.query(CollectNews).filter(
            CollectNews.user_id == user_id,
            CollectNews.news_id == news_id
            ).delete()
        transaction.commit()
        with redis.pipeline(transaction = False) as p:
            p.zrem(REDIS_NEWS_COL_BY_USER_ID % user_id, news_id)
            p.zrem(REDIS_NEWS_COL_USER_BY_NEWS_ID % news_id, user_id)
            m, n = p.execute()
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        return False
    finally:
        session.close()
    return True

@timer
def news_collect_count(news_id, created_at):
    session = None
    s = 0
    try:
        s = redis_slave.hget(REDIS_NEWS_COL_COUNT, news_id)
        if not s:
            session = sync_dbsession_generator()
            count = session.query(
                CollectNews).filter(
                CollectNews.news_id == news_id).count()
            s = count
            r = redis.hget(REDIS_NEWS_COL_COUNT, news_id, s)
    except Exception, ex:
        print Exception, ex
    finally:
        if session: session.close()
    return collect_count(news_id, s, created_at)

@timer
def news_count_by_user_id(user_id):
    return redis_slave.zcard(REDIS_NEWS_COL_BY_USER_ID % user_id)

@timer
def news_collect_user_has_item(user_id, news_id):
    try:
        return redis_slave.zscore(REDIS_NEWS_COL_BY_USER_ID % user_id, news_id)
    except Exception, ex:
        print Exception, ex
        return False

@timer
def news_collect_list_by_user_id(user_id, offset = 0, limit = 18, reverse = 0):
    key = REDIS_NEWS_COL_BY_USER_ID % user_id
    if reverse == 0:
        _list = redis_slave.zrevrange(key, offset, offset+limit)
    else:
        _list = redis_slave.zrange(key, offset, offset+limit)
    return _list

