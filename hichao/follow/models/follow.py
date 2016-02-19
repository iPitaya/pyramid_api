#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
from hichao.base.lib.redis import redis, redis_key
from hichao.base.lib.redis import redis_slave, redis_slave_key
from hichao.follow.models.db import Base, rdbsession_generator, dbsession_generator
from hichao.base.config import (
    FOLLOWING_TYPE,
    )  

from sqlalchemy import (
    Column,
    Integer,
    TIMESTAMP,
    func,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.exc import IntegrityError 
from hichao.util.statsd_client import timeit
from hichao.cache.cache import (
        deco_cache,
        )
from hichao.util.date_util import HOUR, DAY, FIVE_MINUTES,WEEK

import transaction

#根据用户id获得其粉丝数
REDIS_FANS_USER_COUNT_BY_USER_ID = redis_key.FansUserCountByUserID()
REDIS_FOLLOW_USER_COUNT_BY_USER_ID = redis_key.FollowUserCountByUserID()
timer = timeit('hichao_backend.m_collect_star')

class Follows(Base):

    __tablename__ = 'follows'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    following_id = Column(Integer)
    following_type =Column(TINYINT)
    create_ts = Column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.current_timestamp())

#现在定关注和取消关注读mysql
@timer
def forum_follow_new(user_id, following_user_id):
    status = get_user_follow_status(user_id, following_user_id)
    if status:
        return True
    else:
        try:
            now = int(time.time())
            session = dbsession_generator()
            follow = Follows()
            follow.user_id = user_id
            follow.following_id = following_user_id
            follow.following_type = 0
            follow.created_ts = now
            session.add(follow)
            transaction.commit()
            get_user_follow_status(user_id,following_user_id, use_cache = False)
            with redis.pipeline(transaction=False) as p:
                 p.hincrby(REDIS_FANS_USER_COUNT_BY_USER_ID, following_user_id, 1)
                 p.hincrby(REDIS_FOLLOW_USER_COUNT_BY_USER_ID, user_id, 1)
                 p.execute()
        except IntegrityError:
            transaction.abort()
            return False
        except Exception, ex:
            transaction.abort()
            print Exception, ex
            return False
        finally:
            session.close()
            return True

@timer
def forum_follow_del(user_id, following_user_id):
    try:
        session = dbsession_generator()
        session.query(
            Follows).filter(
            Follows.user_id == user_id,
            Follows.following_id == following_user_id).delete()
        transaction.commit()
        get_user_follow_status(user_id,following_user_id, use_cache = False)
        with redis.pipeline(transaction=False) as p:
            p.hincrby(REDIS_FANS_USER_COUNT_BY_USER_ID, following_user_id, -1)
            p.hincrby(REDIS_FOLLOW_USER_COUNT_BY_USER_ID, user_id, -1)
            p.execute()
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        return False
    finally:
        session.close()
        return True

#获得关注数
@timer
def forum_following_count(user_id):
    count = 0
    try:
        session = rdbsession_generator()
        count_query = session.query(
            Follows).filter(
            Follows.user_id == user_id).count()
        count = count_query
    except Exception, ex:
        print Exception, ex
    finally:
        session.close()
    return count

#获得粉丝数
@timer
def forum_followed_count(following_user_id):
    count = 0
    try:
        session = rdbsession_generator()
        count_query = session.query(
            Follows).filter(
            Follows.following_id == following_user_id).count()
        count = count_query
    except Exception, ex:
        print Exception, ex
    finally:
        session.close()
    return count

@timer
def following_id_list_by_user_id(user_id):
    user_ids = [] 
    try:
        session = rdbsession_generator()
        user_id_list = session.query(
            Follows.following_id, Follows.following_type).filter(Follows.user_id == user_id)
        _hot_list = user_id_list.filter(Follows.following_type == FOLLOWING_TYPE.CODE[FOLLOWING_TYPE.HOT]).all()
        _star_list = user_id_list.filter(Follows.following_type == FOLLOWING_TYPE.CODE[FOLLOWING_TYPE.STAR]).all()
        _designer_list = user_id_list.filter(Follows.following_type == FOLLOWING_TYPE.CODE[FOLLOWING_TYPE.DESIGN]).all()
        hot_ids = [hl[0] for hl in _hot_list]
        user_ids.append(hot_ids)
        star_ids = [sl[0] for sl in _star_list]
        user_ids.append(star_ids)
        designer_ids = [dl[0] for dl in _designer_list]
        user_ids.append(designer_ids)
    except Exception, ex:
        print Exception, ex
    finally:
        session.close()
    return user_ids

@timer
def get_following_user_ids_by_user_id(user_id):
    user_ids = []
    try:
        session = rdbsession_generator()
        user_ids = session.query(
            Follows.following_id).filter(Follows.user_id == user_id)
        user_ids = [user_id[0] for user_id in user_ids]
    except Exception, ex:
        print Exception, ex
    finally:
        session.close()
    return user_ids

@timer
@deco_cache(prefix = 'follow_status', recycle = HOUR)
def get_user_follow_status(user_id,following_user_id, use_cache = True):
    result = 0
    try:
        session = rdbsession_generator()
        item = session.query(
            Follows).filter(
            Follows.user_id == int(user_id),Follows.following_id == int(following_user_id)).first()
        if item:
            result = 1
    except Exception,e:
        print e
    finally:
        session.close()
    return result

@timer
def get_follow_list_by_user_id(user_id,flag,limit):
    ids = []
    try:
        session = rdbsession_generator()
        items = session.query(Follows).filter(Follows.user_id == user_id).offset(flag).limit(limit)
    except Exception,e:
        print e
    finally:
        session.close()
    ids = [item.following_id for item in items]
    return ids

@timer
def get_fans_list_by_user_id(user_id,flag,limit):
    ids = []
    try:
        session = rdbsession_generator()
        items = session.query(Follows).filter(Follows.following_id == user_id).offset(flag).limit(limit)
    except Exception,e:
        print e
    finally:
        session.close()
    ids = [item.user_id for item in items]
    return ids


if __name__ == "__main__":
    pass
