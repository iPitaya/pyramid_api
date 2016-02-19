# -*- coding:utf-8 -*-

import time
import datetime
from hichao.base.lib.redis import redis, redis_key, redis_slave
from hichao.collect.models.db import Base, sync_dbsession_generator
from hichao.collect.models.fake import collect_count
from hichao.util.statsd_client import timeit

from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    func,
    )
from sqlalchemy.exc import IntegrityError
import transaction

REDIS_BRAND_COL_BY_USER_ID = redis_key.BrandCollectByUserId("%s")
REDIS_BRAND_COL_USER_BY_BRAND_ID = redis_key.BrandCollectUserByBrandId("%s")
REDIS_BRAND_COL_COUNT = redis_key.BrandCollectCount()
REDIS_BRAND_COL_COUNT_BY_USER_ID = redis_key.BrandCollectCountByUserId()

timer = timeit('hichao_backend.m_collect_brand')

class CollectBrand(Base):
    __tablename__ = 'brand'
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer)
    brand_id = Column(Integer)
    created_at = Column(TIMESTAMP(timezone = False), nullable = False, server_default = func.current_timestamp())

@timer
def brand_collect_new(user_id, brand_ids):
    try:
        now = int(time.time())
        session = sync_dbsession_generator()
        brand_ids = [int(id) for id in brand_ids if str(id).isdigit()]
        collected_ids = session.query(CollectBrand.brand_id).filter(CollectBrand.user_id == int(user_id)).filter(CollectBrand.brand_id.in_(brand_ids)).all()
        collected_ids = [int(id[0]) for id in collected_ids]
        uncollected_ids = [id for id in brand_ids if id not in collected_ids]
        uncollected_brands = []
        for brand_id in uncollected_ids:
            brand = CollectBrand()
            brand.user_id = user_id
            brand.brand_id = brand_id
            brand.created_at = datetime.datetime.now()
            uncollected_brands.append(brand)
        session.add_all(uncollected_brands)
        transaction.commit()
        with redis.pipeline(transaction = False) as p:
            for brand_id in brand_ids:
                p.zadd(REDIS_BRAND_COL_BY_USER_ID % user_id, now, brand_id)
                p.zadd(REDIS_BRAND_COL_USER_BY_BRAND_ID % brand_id, now, user_id)
                p.hincrby(REDIS_BRAND_COL_COUNT, brand_id, 1)
                p.hincrby(REDIS_BRAND_COL_COUNT_BY_USER_ID, user_id, 1)
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
def brand_collect_rm(user_id, brand_id):
    session = sync_dbsession_generator()
    try:
        session.query(CollectBrand).filter(
            CollectBrand.user_id == int(user_id),
            CollectBrand.brand_id == int(brand_id)).delete()
        transaction.commit()
        with redis.pipeline(transaction = False) as p:
            p.zrem(REDIS_BRAND_COL_BY_USER_ID % user_id, brand_id)
            p.zrem(REDIS_BRAND_COL_USER_BY_BRAND_ID % brand_id, user_id)
            p.hincrby(REDIS_BRAND_COL_COUNT, brand_id, -1)
            m, n = p.execute()
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        return False
    finally:
        session.close()
    return True

@timer
def brand_collect_count(brand_id, create_at):
    session = None
    s = 0
    try:
        s = redis_slave.hget(REDIS_BRAND_COL_COUNT, brand_id)
        if not s:
            session = sync_dbsession_generator()
            count = session.query(
                CollectBrand).filter(
                CollectBrand.brand_id == int(brand_id)).count()
            s = count
            r = redis.hset(REDIS_BRAND_COL_COUNT, brand_id, s)
    except Exception, ex:
        print Exception, ex
    finally:
        if session: session.close()
    return collect_count(brand_id, s, create_at)

@timer
def brand_count_by_user_id(user_id):
    return redis_slave.zcard(REDIS_BRAND_COL_BY_USER_ID % user_id)

@timer
def brand_collect_user_has_item(user_id, brand_id):
    try:
        return redis_slave.zscore(REDIS_BRAND_COL_BY_USER_ID % user_id, brand_id)
    except Exception, ex:
        print Exception, ex
        return False

@timer
def brand_collect_list_by_user_id(user_id, offset = 0, limit = 18, reverse = 0):
    key = REDIS_BRAND_COL_BY_USER_ID % user_id
    if reverse == 0:
        _list = redis_slave.zrevrange(key, offset, offset + limit)
    else:
        _list = redis_slave.zrange(key, offset, offset + limit)
    return _list


