#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime

from hichao.base.lib.redis import redis, redis_key
from hichao.base.lib.redis import redis_slave, redis_slave_key
from hichao.collect.models.db import Base, sync_dbsession_generator
from hichao.collect.models.fake import collect_count
from hichao.util.statsd_client import timeit
from hichao.sku.models.sku import Sku
from hichao.sku.models.db import slave_dbsession_generator as get_sku_session

from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    func
)
from sqlalchemy.exc import IntegrityError

import transaction

REDIS_SKU_COL_USER_BY_SKU_ID = redis_key.SkuCollectUserBySku('%s')
REDIS_SKU_COL_BY_USER_ID = redis_key.SkuCollectByUser('%s')
REDIS_SKU_COL_COUNT = redis_key.SkuCollectCount()
REDIS_SKU_COL_COUNT_BY_USER_ID = redis_key.SkuCollectCountByUserId()

timer = timeit('hichao_backend.m_collect_sku')


class CollectSku(Base):

    __tablename__ = 'sku'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    sku_id = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.current_timestamp())


@timer
def sku_collect_new(user_id, sku_ids):
    try:
        now = int(time.time())
        session = sync_dbsession_generator()
        sku_ids = {int(id) for id in sku_ids}
        collected_ids = session.query(CollectSku.sku_id).filter(
            CollectSku.user_id == int(user_id)).filter(CollectSku.sku_id.in_(sku_ids)).all()
        collected_ids = {int(id[0]) for id in collected_ids}
        uncollected_ids = sku_ids - collected_ids

        sku_session = get_sku_session()
        good_ids = [x[0] for x in sku_session.query(Sku.sku_id).filter(
            Sku.sku_id.in_(uncollected_ids)).all()]
        uncollected_skus = []
        for sku_id in good_ids:
            sku = CollectSku()
            sku.user_id = user_id
            sku.sku_id = sku_id
            sku.created_at = datetime.datetime.now()
            uncollected_skus.append(sku)
        session.add_all(uncollected_skus)
        transaction.commit()

        with redis.pipeline(transaction=False) as p:
            for sku_id in sku_ids:
                p.zadd(REDIS_SKU_COL_BY_USER_ID % user_id, now, sku_id)
                p.zadd(REDIS_SKU_COL_USER_BY_SKU_ID % sku_id, now, user_id)
                p.hincrby(REDIS_SKU_COL_COUNT, sku_id, 1)
                p.hincrby(REDIS_SKU_COL_COUNT_BY_USER_ID, user_id, 1)
            p.execute()
    except IntegrityError:
        transaction.abort()
        return 0
    except Exception as e:
        transaction.abort()
        print e
        return 0
    finally:
        session.close()
    return 1

@timer
def sku_collect_rm(user_id, sku_id):
    session = sync_dbsession_generator()

    try:
        session.query(
            CollectSku).filter(
            CollectSku.user_id == user_id,
            CollectSku.sku_id == sku_id).delete(
        )
        transaction.commit()

        with redis.pipeline(transaction=False) as p:
            p.zrem(REDIS_SKU_COL_BY_USER_ID % user_id, sku_id)
            p.zrem(REDIS_SKU_COL_USER_BY_SKU_ID % sku_id, user_id)
            m, n = p.execute()
            if m and n:
                return True
    except Exception, ex:
        transaction.abort()
        print Exception, ex
    finally:
        session.close()
    return False


@timer
def sku_collect_count(sku_id, created_at):
    session = None
    s = 0
    try:
        s = redis_slave.hget(REDIS_SKU_COL_COUNT, sku_id)
        if not s:
            session = sync_dbsession_generator()
            count = session.query(
                CollectSku).filter(
                CollectSku.sku_id == sku_id).count(
            )
            s = count
            r = redis.hset(REDIS_SKU_COL_COUNT, sku_id, s)
    except Exception, ex:
        print Exception, ex
    finally:
        if session: session.close()
    return collect_count(sku_id, s, created_at)


@timer
def sku_count_by_user_id(user_id):
    return redis_slave.zcard(REDIS_SKU_COL_BY_USER_ID % user_id)
    #session = sync_dbsession_generator()
    #c = 0
    #try:
    #    c = redis.hget(REDIS_SKU_COL_COUNT_BY_USER_ID, user_id)
    #    if not c:
    #        count = session.query(
    #            CollectSku).filter(
    #            CollectSku.user_id == user_id).count(
    #        )
    #        c = count
    #        redis.hset(REDIS_SKU_COL_COUNT_BY_USER_ID, user_id, c)
    #except Exception, ex:
    #    print Exception, ex
    #finally:
    #    session.close()
    #return c


@timer
def sku_collect_user_has_item(user_id, sku_id):
    #session = sync_dbsession_generator()
    try:
        return redis_slave.zscore(REDIS_SKU_COL_BY_USER_ID % user_id, sku_id)
    except Exception as e:
        print e
    return False

    # finally:
    # session.close()


@timer
def sku_collect_list_by_user_id(user_id, offset=0, limit=18, reverse=0):
    #session = sync_dbsession_generator()
    #l = []
    #if limit == -1:
    #    limit = sku_count_by_user_id(user_id)

    #try:
    #    l = session.query(
    #        CollectSku).filter(
    #        CollectSku.user_id == user_id).order_by(
    #        CollectSku.created_at.desc()).offset(
    #        offset).limit(
    #        limit).all(
    #    )
    #except Exception as e:
    #    print e 
    #finally:
    #    session.close()
    #return [item.sku_id for item in l]

    key = REDIS_SKU_COL_BY_USER_ID % user_id
    # zrange / zrevrange bounds are inclusive
    if reverse == 0:
       _list = redis_slave.zrevrange(key, offset, offset+limit-1)
    else:
       _list = redis_slave.zrange(key, offset, offset+limit-1)
    return _list

if __name__ == "__main__":
    pass
