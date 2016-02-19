# -*- coding:utf-8 -*-
from sqlalchemy import (
    Column,
    VARCHAR,
    TEXT,
    BIGINT,
    func,
    Float,
    DateTime,
)
from sqlalchemy.dialects.mysql import INTEGER
from hichao.theme.models.db import (
    Base,
    rdbsession_generator,
)
from hichao.cache.cache import deco_cache
from hichao.util.date_util import FIVE_MINUTES
from hichao.util.statsd_client import timeit
from hichao.base.models.base_component import BaseComponent
from sqlalchemy.dialects.mssql.base import TINYINT
timer = timeit('hichao_backend.m_theme_tag')


class ThemeTag(Base, BaseComponent):
    __tablename__ = 'news_theme_tag'
    id = Column(INTEGER,nullable = False,primary_key = True,autoincrement = True)
    sub_id = Column(INTEGER, nullable=False)
    tag_id = Column(INTEGER, nullable=False)
    status = Column(TINYINT, default=1)
    order_num = Column(TINYINT)

    def __init__(self, sub_id, tag_id, status):
        self.sub_id = sub_id
        self.tag_id = tag_id
        self.status = status

@timer
@deco_cache(prefix = 'tag_ids_by_theme_id', recycle = FIVE_MINUTES)
def get_tag_ids_by_theme_id(theme_id):
    DBSession = rdbsession_generator()
    tag_ids = DBSession.query(ThemeTag.tag_id).filter(ThemeTag.sub_id == int(theme_id)).all()
    if tag_ids: tag_ids = [id[0] for id in tag_ids]
    DBSession.close()
    return tag_ids
