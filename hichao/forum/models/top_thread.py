# -*- coding:utf-8 -*-
from sqlalchemy import (
        Column,
        INTEGER,
        func,
        DateTime,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.forum.models.db import (
        Base,
        rdbsession_generator,
        threadlocal_dbsession_generator,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import (
        MINUTE,
        FIVE_MINUTES,
        )

import time
import datetime
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_forum_topthread')

class TopThreads(Base):
    __tablename__ = 'top_threads'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    thread_id = Column(INTEGER, nullable = False)
    category_id = Column(TINYINT)
    ts = Column(DateTime)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    pos = Column(INTEGER)
    review = Column(TINYINT)

    def __init__(self, thread_id, category_id, ts, start_time, end_time, pos, review):
        self.thread_id = thread_id
        self.category_id = category_id
        self.ts = ts
        self.start_time = start_time
        self.end_time = end_time
        self.pos = pos
        self.review = review

@timer
@deco_cache(prefix = 'top_thread_ids', recycle = MINUTE)
def get_top_thread_ids(category_id, offset = 0, num = 20):
    '''
    category_id = -1  >> 最热
    category_id = -2  >> 最新
    '''
    now = datetime.datetime.now()
    DBSession = rdbsession_generator()
    thread_ids = DBSession.query(TopThreads.thread_id).filter(TopThreads.category_id == category_id).filter(TopThreads.start_time 
            <= now).filter(TopThreads.end_time >= now).filter(TopThreads.review == 1).order_by(TopThreads.pos).offset(offset).limit(num).all()
    DBSession.close()
    thread_ids = [id[0] for id in thread_ids]
    return thread_ids

@timer
@deco_cache(prefix = 'all_top_thread_ids', recycle = FIVE_MINUTES)
def get_all_top_thread_ids(category_id):
    '''
    category_id = -1  >> 最热
    category_id = -2  >> 最新
    '''
    now = datetime.datetime.now()
    DBSession = rdbsession_generator()
    thread_ids = DBSession.query(TopThreads.thread_id).filter(TopThreads.category_id == category_id).filter(TopThreads.start_time 
            <= now).filter(TopThreads.end_time >= now).filter(TopThreads.review == 1).order_by(TopThreads.pos).all()
    DBSession.close()
    thread_ids = [id[0] for id in thread_ids]
    return thread_ids

