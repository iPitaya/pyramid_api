# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        TIMESTAMP,
        func,
        )
from hichao.timeline.models.db import (
        rdbsession_generator,
        Base,
        )
from hichao.base.models.base_component import BaseComponent
from hichao.base.config import FALL_PER_PAGE_NUM
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE
from hichao.util.statsd_client import timeit

class HotThreads(Base, BaseComponent):
    __tablename__ = 'hot_threads'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    type = Column(VARCHAR(32), nullable = False)
    type_id = Column(INTEGER)
    ts = Column(TIMESTAMP, nullable = False)

    def __init__(self, id, type, type_id, ts):
        self.type = type
        self.type_id = type_id
        self.ts = ts

    def get_type_id(self):
        return self.type_id

    def get_type(self):
        return self.type

    def get_id(self):
        return self.id

@timeit('hichao_backend.m_timeline_hotthread')
@deco_cache(prefix = 'hot_thread_ids', recycle = MINUTE)
def get_hot_thread_ids(offset, limit = FALL_PER_PAGE_NUM, use_cache = True):
    DBSession = rdbsession_generator()
    hot_thread_ids = DBSession.query(HotThreads).filter(HotThreads.id > offset).order_by(HotThreads.id).limit(limit).all()
    DBSession.close()
    return hot_thread_ids

