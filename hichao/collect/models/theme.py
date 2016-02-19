# -*- coding:utf-8 -*-

import time
import datetime
from hichao.base.lib.redis import (
        redis,
        redis_key,
        redis_slave,
        )
from hichao.collect.models.db import (
        Base,
        sync_dbsession_generator,
        )
from hichao.collect.models.fake import collect_count
from hichao.util.statsd_client import timeit
from hichao.collect.models.topic import (
        REDIS_TOPIC_COL_BY_USER_ID,
        REDIS_TOPIC_COL_USER_BY_TOPIC_ID,
        REDIS_TOPIC_COL_COUNT,
        REDIS_TOPIC_COL_COUNT_BY_USER_ID,
        )
from sqlalchemy import (
        Column,
        Integer,
        TIMESTAMP,
        func,
        )
from sqlalchemy.exc import IntegrityError

import transaction

REDIS_THEME_COL_BY_USER_ID = REDIS_TOPIC_COL_BY_USER_ID
REDIS_THEME_COL_USER_BY_THEME_ID = REDIS_TOPIC_COL_USER_BY_TOPIC_ID
REDIS_THEME_COL_COUNT = REDIS_TOPIC_COL_COUNT
REDIS_THEME_COL_COUNT_BY_USER_ID = REDIS_TOPIC_COL_COUNT_BY_USER_ID

timer = timeit('hichao_backend.m_collect_theme')

class CollectTheme(Base):
    __tablename__ = 'theme'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    theme_id = Column(Integer)
    created_at = Column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.current_timestamp())

def build_theme_id_as_topic_id(theme_id):
    return 't{0}'.format(theme_id)

def unpack_topic_id_to_theme_id(topic_id):
    return topic_id.replace('t', '')

@timer
def theme_collect_new(user_id, theme_ids):
    try:
        now = int(time.time())
        session = sync_dbsession_generator()
        theme_ids = [int(id) for id in theme_ids if str(id).isdigit()]
        collected_ids = session.query(CollectTheme.theme_id).filter(CollectTheme.user_id == int(user_id)).filter(CollectTheme.theme_id.in_(theme_ids)).all()
        collected_ids = [int(id[0]) for id in collected_ids]
        uncollected_ids = [id for id in theme_ids if id not in collected_ids]
        uncollected_themes = []
        for theme_id in uncollected_ids:
            theme = CollectTheme()
            theme.user_id = user_id
            theme.theme_id = theme_id
            theme.created_at = datetime.datetime.now()
            uncollected_themes.append(theme)
        session.add_all(uncollected_themes)
        transaction.commit()
        with redis.pipeline(transaction = False) as p:
            for theme_id in theme_ids:
                theme_id = build_theme_id_as_topic_id(theme_id)
                p.zadd(REDIS_THEME_COL_BY_USER_ID % user_id, now, theme_id)
                p.zadd(REDIS_THEME_COL_USER_BY_THEME_ID % theme_id, now, user_id)
                p.hincrby(REDIS_THEME_COL_COUNT, theme_id, 1)
                p.hincrby(REDIS_THEME_COL_COUNT_BY_USER_ID, user_id, 1)
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
def theme_collect_rm(user_id, theme_id):
    session = sync_dbsession_generator()
    try:
        session.query(CollectTheme).filter(
            CollectTheme.user_id == int(user_id),
            CollectTheme.theme_id == int(theme_id)).delete()
        transaction.commit()
        with redis.pipeline(transaction = False) as p:
            theme_id = build_theme_id_as_topic_id(theme_id)
            p.zrem(REDIS_THEME_COL_BY_USER_ID % user_id, theme_id)
            p.zrem(REDIS_THEME_COL_USER_BY_THEME_ID % theme_id, user_id)
            m, n = p.execute()
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        return False
    finally:
        session.close()
    return True

@timer
def theme_collect_count(theme_id, created_at):
    session = None
    s = 0
    try:
        s = redis_slave.hget(REDIS_THEME_COL_COUNT, build_theme_id_as_topic_id(theme_id))
        if not s:
            session = sync_dbsession_generator()
            count = session.query(
                CollectTheme).filter(
                CollectTheme.theme_id == int(theme_id)).count()
            s = count
            r = redis.hset(REDIS_THEME_COL_COUNT, build_theme_id_as_topic_id(theme_id), s)
    except Exception, ex:
        print Exception, ex
    finally:
        if session: session.close()
    return collect_count(theme_id, s, created_at)

@timer
def theme_count_by_user_id(user_id):
    return redis_slave.zcard(REDIS_THEME_COL_BY_USER_ID % user_id)

@timer
def theme_collect_user_has_item(user_id, theme_id):
    try:
        theme_id = build_theme_id_as_topic_id(theme_id)
        return redis_slave.zscore(REDIS_THEME_COL_BY_USER_ID % user_id, theme_id)
    except Exception, ex:
        print Exception, ex
        return False

@timer
def theme_collect_list_by_user_id(user_id, offset = 0, limit = 18, reverse = 0):
    key = REDIS_THEME_COL_BY_USER_ID % user_id
    if reverse == 0:
        _list = redis_slave.zrevrange(key, offset, offset + limit)
    else:
        _list = redis_slave.zrange(key, offset, offset + limit)
    return _list

