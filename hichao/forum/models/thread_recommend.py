# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        DATETIME,
        TIMESTAMP,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.forum.models.db import (
        Base,
        rdbsession_generator,
        )
from hichao.util.date_util import MINUTE
from hichao.cache.cache import deco_cache
from hichao.util.statsd_client import timeit
from hichao.base.config import FALL_PER_PAGE_NUM
import datetime

class ThreadRecommend(Base):
    __tablename__ = 'thread_recommend'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    type = Column(VARCHAR(32), nullable = False, default = 'thread')
    type_id = Column('thread_id', INTEGER)
    user_id = Column(INTEGER)
    start_time = Column(DATETIME)
    end_time = Column(DATETIME)
    review = Column(TINYINT)
    last_update_ts = Column(TIMESTAMP)
    pos = Column(INTEGER)
    is_top = Column(TINYINT)

class HomeRecommend(Base):
    __tablename__ = 'home_recommend'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    type = Column(VARCHAR(32), nullable = False, default = 'thread')
    type_id = Column(INTEGER)
    nav_id = Column(INTEGER)
    user_id = Column(INTEGER)
    start_time = Column(DATETIME)
    end_time = Column(DATETIME)
    review = Column(TINYINT)
    last_update_ts = Column(TIMESTAMP)
    pos = Column(INTEGER)
    is_top = Column(TINYINT)


@timeit('hichao_backend.m_forum_threadrecommend')
@deco_cache(prefix = 'new_recommend_thread_ids', recycle = MINUTE)
def get_recommend_thread_ids(flag = 0, limit = FALL_PER_PAGE_NUM):
    DBSession = rdbsession_generator()
    ids = DBSession.query(ThreadRecommend.type, ThreadRecommend.type_id).filter(
        ThreadRecommend.review == 1).order_by(ThreadRecommend.is_top.desc()).order_by(ThreadRecommend.pos.desc()).offset(flag).limit(limit).all()
    DBSession.close()
    return ids

@timeit('hichao_backend.m_forum_homerecommend')
@deco_cache(prefix = 'home_recommend_thread_ids_by_nav_id', recycle = MINUTE)
def get_home_recommend_thread_ids_by_nav_id(nav_id, flag = 0, limit = FALL_PER_PAGE_NUM):
    DBSession = rdbsession_generator()
    curr_time = datetime.datetime.now()
    ids = DBSession.query(HomeRecommend.type, HomeRecommend.type_id).filter(HomeRecommend.nav_id == nav_id).filter(HomeRecommend.start_time<=curr_time).filter(HomeRecommend.end_time>=curr_time).filter(
        HomeRecommend.review == 1).order_by(HomeRecommend.is_top.desc()).order_by(HomeRecommend.pos.desc()).offset(flag).limit(limit).all()
    DBSession.close()
    return ids

