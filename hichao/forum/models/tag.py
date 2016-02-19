# -*- coding:utf-8 -*-

from hichao.util.date_util import (
    HALF_HOUR,
    )
from hichao.util.statsd_client import timeit
from sqlalchemy import (
    INTEGER,
    VARCHAR,
    Column,
)
from sqlalchemy.dialects.mysql import (
    TINYINT,
)
from hichao.forum.models.db import (
    Base,
    rdbsession_generator,
)
from hichao.cache.cache import (
    deco_cache,
    deco_cache_m,
)
from hichao.forum.models.pv import (
    tag_thread_count,
    tag_comment_count,
)

timer = timeit('hichao_backend.m_forum_tag')


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    tag = Column(VARCHAR(64), nullable=False, default='')
    icon = Column(VARCHAR(512), nullable=False, default='')
    bg_url = Column(VARCHAR(512), nullable=False, default='')
    description = Column(VARCHAR(512), nullable=False, default='')
    review = Column(TINYINT, default=0)

    def get_component_forum_tag(self):
        com = {}
        com['id'] =self.id
        com['icon'] = self.icon
        com['bg_url'] = self.bg_url
        com['description'] = self.description
        com['title'] = self.tag
        com['threadCount'] = self.get_tag_thread_count()
        com['commentCount'] = self.get_tag_comment_count()
        return com

    def get_tag_comment_count(self):
        return tag_comment_count(self.id)

    def get_tag_thread_count(self):
        return tag_thread_count(self.id)

    def get_tag_action(self):
        action = {}
        action['id'] = str(self.id)
        action['type'] = 'forum'
        action['actionType'] = 'tag'
        action['tag'] = str(self.tag)
        return action

@timer
@deco_cache(prefix='forum_tag', recycle=HALF_HOUR)
def get_tag_by_id(tag_id, use_cache=True):
    DBSession = rdbsession_generator()
    tag = DBSession.query(Tag).filter(Tag.id == int(tag_id)).filter(Tag.review == 1).first()
    DBSession.close()
    return tag

@timer
@deco_cache_m(prefix='forum_tag', recycle=HALF_HOUR)
def get_tags_by_id(tag_ids, use_cache=True):
    tag_ids = [int(_id) for _id in tag_ids]
    DBSession = rdbsession_generator()
    tags = DBSession.query(Tag.id, Tag).filter(Tag.id.in_(tag_ids)).filter(Tag.review == 1).all()
    tags = dict(tags)
    DBSession.close()
    return tags

@timer
@deco_cache(prefix = 'forum_tag_id', recycle=HALF_HOUR)
def get_tag_id_by_tag(tag, use_cache=True):
    DBSession = rdbsession_generator()
    tag_id = DBSession.query(Tag.id).filter(Tag.tag == tag).first()
    if tag_id: tag_id = tag_id[0]
    else: tag_id = 0
    DBSession.close()
    return tag_id

