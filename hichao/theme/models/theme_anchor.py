# -*- coding:utf-8 -*-

from hichao.util.statsd_client import timeit
from sqlalchemy import (
        func,
        Column,
        INTEGER,
        VARCHAR,
        DateTime,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.theme.models.db import (
        rdbsession_generator,
        Base,
        )
from hichao.base.models.base_component import BaseComponent
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE
from hichao.util.cms_action_builder import build_cms_action
import json

timer = timeit('hichao_backend.m_theme_anchor')

class ThemeAnchor(Base, BaseComponent):
    __tablename__ = 'news_anchor_map'
    id = Column(INTEGER, primary_key = True)
    review = Column('status', TINYINT)
    sub_id = Column(INTEGER)
    action_type = Column(INTEGER)
    action_value = Column(VARCHAR(150))
    add_datetime = Column(DateTime)
    x = Column(INTEGER)
    y = Column(INTEGER)
    width = Column(INTEGER)
    height = Column(INTEGER)

    def get_component_x(self, width):
        return '%.2f' %(float(self.x) / width * 100)+'%'

    def get_component_y(self, height):
        return '%.2f' %(float(self.y) / height * 100)+'%'

    def get_component_width(self, width):
        return '%.2f' %(float(self.width) / width * 100)+'%'

    def get_component_height(self, height):
        return '%.2f' %(float(self.height) / height * 100)+'%'

    def get_component_action_type_id(self):
        return str(self.action_type)

    def get_component_action_value(self):
        return str(self.action_value)

    def to_ui_action(self):
        return build_cms_action(self.get_component_action_type_id(), self.get_component_action_value())

    def to_ui_action_str(self):
        return json.dumps(self.to_ui_action())

    def to_ui_detail(self, width, height):
        com = {}
        com['x'] = self.get_component_x(width)
        com['y'] = self.get_component_y(height)
        com['width'] = self.get_component_width(width)
        com['height'] = self.get_component_height(height)
        com['action'] = self.to_ui_action_str()
        return com

@timer
@deco_cache(prefix = 'theme_anchors', recycle = MINUTE)
def get_anchors_by_theme_id(theme_id):
    DBSession = rdbsession_generator()
    anchors = DBSession.query(ThemeAnchor).filter(ThemeAnchor.sub_id == theme_id).filter(ThemeAnchor.review == 1).all()
    DBSession.close()
    return anchors

