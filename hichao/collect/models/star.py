#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
from hichao.base.lib.redis import redis, redis_key
from hichao.base.lib.redis import redis_slave, redis_slave_key
from hichao.collect.models.db import Base, sync_dbsession_generator
from hichao.collect.models.fake import collect_count

from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    func
)
from sqlalchemy.exc import IntegrityError
from hichao.util.statsd_client import timeit

import transaction

REDIS_STAR_COL_BY_USER_ID = redis_key.StarCollectByUser('%s')
REDIS_STAR_COL_USER_BY_STAR_ID = redis_key.StarCollectUserByStar('%s')
REDIS_STAR_COL_COUNT = redis_key.StarCollectCount()
REDIS_STAR_COL_COUNT_BY_USER_ID = redis_key.StarCollectCountByUserId()

timer = timeit('hichao_backend.m_collect_star')



class CollectStar(Base):

    __tablename__ = 'star'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    star_id = Column(Integer)
    created_at = Column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.current_timestamp())

@timer
def star_collect_new(user_id, star_ids):
    try:
        now = int(time.time())
        session = sync_dbsession_generator()
        star_ids = [int(id) for id in star_ids]
        collected_ids = session.query(CollectStar.star_id).filter(CollectStar.user_id == int(user_id)).filter(CollectStar.star_id.in_(star_ids)).all()
        collected_ids = [int(id[0]) for id in collected_ids]
        uncollected_ids = [id for id in star_ids if id not in collected_ids]
        uncollected_stars = []
        for star_id in uncollected_ids:
            star = CollectStar()
            star.user_id = user_id
            star.star_id = star_id
            star.created_at = datetime.datetime.now()
            uncollected_stars.append(star)
        session.add_all(uncollected_stars)
        transaction.commit()
        with redis.pipeline(transaction = False) as p:
            for star_id in star_ids:
                p.zadd(REDIS_STAR_COL_BY_USER_ID % user_id, now, star_id)
                p.zadd(REDIS_STAR_COL_USER_BY_STAR_ID % star_id, now, user_id)
                p.hincrby(REDIS_STAR_COL_COUNT, star_id, 1)
                p.hincrby(REDIS_STAR_COL_COUNT_BY_USER_ID, user_id, 1)
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
def star_collect_rm(user_id, star_id):
    session = sync_dbsession_generator()

    try:
        session.query(
            CollectStar).filter(
            CollectStar.user_id == user_id,
            CollectStar.star_id == star_id).delete(
        )
        transaction.commit()

        with redis.pipeline(transaction=False) as p:
            p.zrem(REDIS_STAR_COL_BY_USER_ID % user_id, star_id)
            p.zrem(REDIS_STAR_COL_USER_BY_STAR_ID % star_id, user_id)
            m, n = p.execute()

    except Exception, ex:
        transaction.abort()
        print Exception, ex
        return False
    finally:
        session.close()
    return True

@timer
def star_collect_count(star_id, created_at):
    session = None
    s = 0
    try:
        s = redis_slave.hget(REDIS_STAR_COL_COUNT, star_id)
        if not s:
            #  get into mysql
            session = sync_dbsession_generator()
            count = session.query(
                CollectStar).filter(
                CollectStar.star_id == star_id).count(
            )
            s = count
            # set redis
            r = redis.hset(REDIS_STAR_COL_COUNT, star_id, s)
    except Exception, ex:
        print Exception, ex
    finally:
        if session: session.close()
    return collect_count(star_id, int(s) + 350, created_at)

@timer
def star_count_by_user_id(user_id):
    #session = sync_dbsession_generator()
    return redis_slave.zcard(REDIS_STAR_COL_BY_USER_ID % user_id)
    #try:
    #    c = redis.hget(REDIS_STAR_COL_COUNT_BY_USER_ID, user_id)
    #    if not c:
    #        count = session.query(
    #            CollectStar).filter(
    #            CollectStar.user_id == user_id).count(
    #        )
    #        c = count
    #        redis.hset(REDIS_STAR_COL_COUNT_BY_USER_ID, user_id, c)
    #except Exception, ex:
    #    print Exception, ex
    #    c = 0
    #finally:
    #    session.close()
    #return c

@timer
def star_collect_user_has_item(user_id, star_id):
    #session = sync_dbsession_generator()
    try:
        return redis_slave.zscore(REDIS_STAR_COL_BY_USER_ID % user_id, star_id)
    except Exception ,ex:
        print Exception, ex
        # 如果没有的时候去mysql 查询是不可接受的, 这里的逻辑和缓存是很不一样的
        #r = session.query(CollectStar).filter(CollectStar.user_id==uesr_id, CollectStar.star_id==star_id).first()
        # if r:
        #    set redis 需要思考的地方
        # return r

        return False
    # finally:
    #    session.close()

@timer
def star_collect_list_by_user_id(user_id, offset=0, limit=18, reverse=0):
    #session = sync_dbsession_generator()
    #l = []
    #if limit == -1:
    #    limit = star_count_by_user_id(user_id)
    #try:
    #    l = session.query(
    #        CollectStar).filter(
    #        CollectStar.user_id == user_id,).order_by(
    #        CollectStar.created_at.desc()).offset(
    #        offset).limit(
    #        limit).all(
    #    )
    #except Exception, ex:
    #    print Exception, ex
    #finally:
    #    session.close()
    #return [item.star_id for item in l]

    key = REDIS_STAR_COL_BY_USER_ID % user_id
    if reverse ==0:
      _list = redis_slave.zrevrange(key, offset, offset+limit)
    else:
      _list = redis_slave.zrange(key, offset, offset+limit)
    return _list

if __name__ == "__main__":
    pass
