# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        BIGINT,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.forum.models.db import (
        Base,
        rdbsession_generator,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import (
        FIVE_MINUTES,
        MONTH,
        )
from hichao.util.statsd_client import timeit
from hichao.base.models.base_component import BaseComponent

timer = timeit('hichao_backend.m_forum')

class Forum(Base, BaseComponent):
    __tablename__ = 'bankuai'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    topic_id = Column(INTEGER, nullable = False)
    name = Column(VARCHAR(255), nullable = False)
    description = Column(VARCHAR(255))
    review = Column(TINYINT, nullable = False, default = 1)
    ts = Column(BIGINT)
    url = Column(VARCHAR(255))
    category_id = Column(INTEGER, nullable = False, default = 0)
    pos = Column(INTEGER, nullable = False, default = 0)

@timer
@deco_cache(prefix = 'all_forums', recycle = FIVE_MINUTES)
def get_all_forums(use_cache = True):
    DBSession = rdbsession_generator()
    forums = DBSession.query(Forum.name, Forum.url, Forum.category_id).filter(Forum.review == 1).order_by(Forum.pos.desc()).all()
    DBSession.close()
    return forums

@timer
@deco_cache(prefix = 'forum_name_to_cat_id', recycle = MONTH)
def get_forum_cat_id_by_name(name, use_cache = True):
    DBSession = rdbsession_generator()
    forum_id = DBSession.query(Forum.category_id).filter(Forum.name == name).first()
    if forum_id: forum_id = forum_id[0]
    DBSession.close()
    return forum_id

@timer
@deco_cache(prefix = 'forum_cat_id_to_name', recycle = FIVE_MINUTES)
def get_forum_name_by_cat_id(cat_id, use_cache = True):
    DBSession = rdbsession_generator()
    name = DBSession.query(Forum.name).filter(Forum.category_id == int(cat_id)).filter(Forum.review == 1).first()
    if name: name = name[0]
    else: name = None
    DBSession.close()
    return name

@timer
@deco_cache(prefix = 'forum_by_id', recycle = FIVE_MINUTES)
def get_forum_by_id(cat_id, use_cache = True):
    DBSession = rdbsession_generator()
    forum = DBSession.query(Forum.name, Forum.url, Forum.category_id).filter(Forum.category_id == int(cat_id)).filter(Forum.review == 1).first()
    DBSession.close()
    return forum

