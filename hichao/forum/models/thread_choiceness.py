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

class ThreadChoiceness(Base):
    __tablename__ = 'thread_choiceness'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    user_id = Column( INTEGER)
    thread_id = Column( INTEGER)
    thread_img_id = Column( INTEGER)
    thread_title = Column(VARCHAR(100))
    thread_desc = Column(VARCHAR(100))
    ts = Column(TIMESTAMP)
    review = Column(TINYINT)
    pos = Column(INTEGER)

@timeit('hichao_backend.m_forum_threadchoiceness')
@deco_cache(prefix = 'choiceness_thread_ids', recycle = MINUTE)
def get_thread_choiceness_items():
    '''获取 购范 每日精选 的数据条目 '''
    DBSession = rdbsession_generator()
    items = DBSession.query(ThreadChoiceness).filter(ThreadChoiceness.review == 1).order_by(ThreadChoiceness.pos.desc()).all()
    DBSession.close()
    return items

@timeit('hichao_backend.m_forum_threadchoiceness_ids')
@deco_cache(prefix = 'thread_ids', recycle = MINUTE)
def get_thread_choiceness_ids(ts, num, use_cache = True):
    DBSession = rdbsession_generator()
    thread_ids = DBSession.query(ThreadChoiceness.id).filter(ThreadChoiceness.review == 1).filter(ThreadChoiceness.ts < ts).order_by(ThreadChoiceness.pos.desc()).limit(num).all()
    thread_ids = [thread[0] for thread in thread_ids]
    DBSession.close()
    return thread_ids

@timeit('hichao_backend.m_forum_thread_choiceness')
@deco_cache(prefix = 'choiceness_thread', recycle = MINUTE)
def get_choiceness_thread_by_id(id, use_cache = True):
    DBSession = rdbsession_generator()
    choiceness_thread = DBSession.query(ThreadChoiceness).filter(ThreadChoiceness.id == int(id)).filter(ThreadChoiceness.review == 1).first()
    DBSession.close()
    return choiceness_thread 
