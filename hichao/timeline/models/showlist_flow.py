# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        TIMESTAMP,
        )
from hichao.timeline.models.db import (
        rdbsession_generator,
        Base,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.base.models.base_component import BaseComponent
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE
from hichao.forum.models.thread import get_thread_by_id
from hichao.util.image_url import build_flow_image_url
from hichao.forum.models.pv  import thread_pv_count
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_timeline_showlist_flow')
timer_mysql = timeit('hichao_backend.m_timeline_showlist_flow.mysql')

class ShowlistFlow(Base, BaseComponent):
    __tablename__ = 'showlist_flow'
    id = Column(INTEGER(unsigned = True), primary_key = True, autoincrement = True)
    type = Column(VARCHAR(128))
    type_id = Column(INTEGER(unsigned = True))
    title = Column(VARCHAR(255))
    img_url = Column(VARCHAR(2048))
    width = Column(INTEGER)
    height = Column(INTEGER)
    review = Column(TINYINT)
    publish_date = Column(TIMESTAMP)
    ts = Column(TIMESTAMP)

    def __init__(self, type, type_id, title, img_url, width = 100, height = 150, review = 1):
        self.type = type
        self.type_id = type_id
        self.title = title
        self.img_url = img_url
        self.width = width
        self.height = height
        self.review = review

    def get_bind_item(self):
        if self.type == 'thread':
            return get_thread_by_id(self.type_id)
        return None

    def get_component_sku_num(self):
        item = self.get_bind_item()
        if item:
            return item.get_component_sku_num()
        return '0'

    def get_component_forum_id(self):
        return ''

    def get_component_id(self):
        return str(self.type_id)

    def get_component_type_id(self):
        return str(self.type_id)

    def get_component_width(self):
        return str(self.width)

    def get_component_height(self):
        return str(self.height)

    def get_component_pic_url(self):
        return build_flow_image_url(self.img_url)

    def get_component_common_pic_url(self):
        return self.get_component_pic_url()

    def get_component_type(self):
        return self.type

    def get_component_description(self):
        return self.title

    def get_component_title(self):
        return self.title

    def get_component_category_id(self):
        return ''

    def to_lite_ui_action(self):
        action = {}
        if self.type == 'thread':
            action['actionType'] = 'detail'
            action['type'] = 'thread'
            action['id'] = str(self.type_id)
        return action

    def get_component_pv(self):
        item = self.get_bind_item()
        if item:
            return item.get_component_pv()
        return '0'


@timer
@deco_cache(prefix = 'showlist_flow', recycle = MINUTE)
@timer_mysql
def get_flow_by_id(flow_id):
    DBSession = rdbsession_generator()
    item = DBSession.query(ShowlistFlow).filter(ShowlistFlow.id == int(flow_id)).first()
    DBSession.close()
    return item

