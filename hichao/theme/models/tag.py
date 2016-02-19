# -*- coding:utf-8 -*-
from sqlalchemy import (
        Column,
        VARCHAR,
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
from bson.json_util import default
timer = timeit('hichao_backend.m_theme_tags')

class Tag(Base,BaseComponent):
    __tablename__ = 'news_tags'
    id = Column(INTEGER,primary_key = True, autoincrement = True)
    name = Column('title', VARCHAR(128),nullable = False)
    description = Column(VARCHAR(255))
    editor = Column(VARCHAR(50),nullable = False)
    status = Column(TINYINT,nullable = False ,default = 1)
    add_datetime = Column(DateTime,nullable = False)
    recommend = Column(TINYINT,default = 0)
    order_num = Column(INTEGER,default = 0)

    def get_component_id(self):
        return str(self.id)
    
    def get_component_tag(self):
        if self.name:
            return str(self.name)
        else:
            return ''
    
    def get_component_description(self):
        if self.description:
            return str(self.description)
        else:
            return ''

    def to_ui_action(self):
        action = {}
        action['actionType'] = 'tag'
        action['tag'] = self.get_component_tag()
        action['id'] = self.get_component_id()
        action['type'] = 'theme'
        return action
   
@timer
@deco_cache(prefix='get_all_tag_ids', recycle=FIVE_MINUTES)
def get_all_tag_ids():
    DBSession = rdbsession_generator()
    tag_ids = DBSession.query(Tag.id).filter(Tag.status == 1).filter(Tag.recommend == 1).order_by(Tag.order_num.asc()).all()
    DBSession.close()
    tag_ids = [tag[0] for tag in tag_ids]
    return tag_ids

@timer
@deco_cache(prefix='tag_by_id', recycle=FIVE_MINUTES)
def get_tag_by_id(tag_id):
    DBSession = rdbsession_generator()
    tag = DBSession.query(Tag).filter(Tag.id == int(tag_id)).filter(Tag.status == 1).first()
    DBSession.close()
    return tag


if __name__ =="__main__":
    tags = get_all_tag_ids()
    print tags

