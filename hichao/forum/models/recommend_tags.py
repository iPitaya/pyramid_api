# -*- coding:utf-8 -*-

from sqlalchemy import (
    INTEGER,
    Column,
    VARCHAR,
)
from hichao.util.date_util import MINUTE, WEEK
from hichao.util.statsd_client import timeit
from sqlalchemy.dialects.mysql import TINYINT
from hichao.forum.models.db import (
    Base,
    rdbsession_generator,
)
from hichao.forum.models.tag import get_tags_by_id
from hichao.util.statsd_client import timeit
from hichao.cache.cache import deco_cache

timer = timeit('hichao_backend.m_forum_recommend_tag')


class RecommendTag(Base):
    __tablename__ = 'tag_recommend'
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    tag_id = Column(INTEGER(unsigned=True), nullable=False, default=0)
    review = Column(TINYINT, nullable=False, default=0)
    pos = Column(INTEGER(unsigned=True), nullable=False, default=0)

class Navigator(Base):
    __tablename__ = 'nav'
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(VARCHAR(256), nullable = False)
    tag_id = Column(INTEGER(unsigned=True), nullable=False, default=0)
    category_id = Column(INTEGER(unsigned=True), nullable=False)
    review = Column(TINYINT, nullable=False, default=0)
    pos = Column(INTEGER(unsigned=True), nullable=False, default=0)

#获取社区首页导航
@timer
#@deco_cache(prefix = 'forum_navigator', recycle = WEEK)
def get_forum_navigator(limit =5, use_cache=True):
    DBSession = rdbsession_generator()
    id_names = DBSession.query(Navigator.id, Navigator.name).filter(Navigator.review == 1).order_by(Navigator.pos.desc()).limit(limit).all()
    DBSession.close()
    tab_list = []
    for item in id_names:
        com = {}
        com['nav_id'] = item[0]
        com['nav_name'] = item[1]
        tab_list.append(com)
    return tab_list

@timer
@deco_cache(prefix = 'forum_navigator_tab', recycle=MINUTE)
def get_navigator_by_nav_id(nav_id, use_cache=True):
    DBSession = rdbsession_generator()
    navigator = DBSession.query(Navigator).filter(Navigator.id==nav_id).filter(Navigator.review==1).first()
    DBSession.close()
    return navigator

@timer
@deco_cache(prefix = 'forum_recmd_tag_ids', recycle = MINUTE)
def get_recommend_tag_ids(use_cache=True):
    DBSession = rdbsession_generator()
    tag_ids = DBSession.query(RecommendTag.tag_id).filter(RecommendTag.review == 1).order_by(RecommendTag.pos.desc()).all()
    if tag_ids: tag_ids = [tag_id[0] for tag_id in tag_ids]
    DBSession.close()
    return tag_ids

@timer
@deco_cache(prefix = 'forum_recmd_tags', recycle = MINUTE)
def get_recommend_tags(use_cache=False):
    recommend_tag_ids = get_recommend_tag_ids(use_cache = use_cache)
    return get_tags_by_id(recommend_tag_ids, use_cache = use_cache)

