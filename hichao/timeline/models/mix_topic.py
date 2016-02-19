# -*- coding:utf-8 -*-

from hichao.util.statsd_client import timeit
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
from hichao.base.models.base_component import BaseComponent
from hichao.base.config import (
        FALL_PER_PAGE_NUM,
        )
from hichao.topic.models.topic import get_topic_by_id
from hichao.theme.models.theme import get_theme_by_id
from hichao.cache.cache import deco_cache
from hichao.util.date_util import (
        MINUTE,
        format_digital,
        ZHOU_DICT,
        )
from hichao.util.statsd_client import timeit
import datetime

timer = timeit('hichao_backend.m_timeline_mix_topic')
timer_mysql = timeit('hichao_backend.m_timeline_mix_topic.mysql')

class MixTopicUnit(Base, BaseComponent):
    __tablename__ = 'special_merge'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    type_id = Column(INTEGER, nullable = False, default = 0)
    type = Column(VARCHAR(255), nullable = False, default = '')
    publish_date = Column(TIMESTAMP, nullable = False)
    review = Column(INTEGER)

    def __init__(self, type_id = 0, type = 'topic', publish_date = ''):
        if not publish_date:
            publish_date = datetime.datetime.now()
        self.type_id = type_id
        self.type = type
        self.publish_date = publish_date

    def get_bind_item(self):
        if self.get_component_type() == 'topic':
            return get_topic_by_id(self.get_component_type_id())
        elif self.get_component_type() == 'theme':
            return get_theme_by_id(self.get_component_type_id())

    def get_component_type(self):
        return self.type

    def get_component_type_id(self):
        return str(self.type_id)

    def get_component_id(self):
        return str(self.id)

    def get_component_height(self):
        return '140'

    def get_component_width(self):
        return '320'

    def get_component_flag(self):
        return str(self.publish_date)

    def get_component_year(self):
        return format_digital(getattr(self.publish_date, 'year'))

    def get_component_month(self):
        return '{0}/{1}'.format(format_digital(getattr(self.publish_date, 'mon')), int(self.get_component_year()) % 100)

    def get_component_day(self):
        return format_digital(getattr(self.publish_date, 'day'))

    def get_component_pv(self):
        item = self.get_bind_item()
        return item.get_component_pv()

    def get_component_week_day(self):
        weekday = getattr(self.publish_date, 'weekday')()
        return ZHOU_DICT[weekday]

    def get_component_top_pic_url(self):
        item = self.get_bind_item()
        return item.get_component_top_pic_url()

    def get_component_pic_url(self):
        item = self.get_bind_item()
        return item.get_component_pic_url()

    def get_unixtime(self):
        return self.publish_date

@timer
@deco_cache(prefix = 'mix_topic_units', recycle = MINUTE)
@timer_mysql
def get_mix_topic_units(offset = '', per_page = FALL_PER_PAGE_NUM, use_cache = True):
    if not offset: offset = datetime.datetime.now()
    DBSession = rdbsession_generator()
    units = DBSession.query(MixTopicUnit).filter(MixTopicUnit.publish_date < offset).filter(MixTopicUnit.review == 1).order_by(MixTopicUnit.publish_date.desc()).limit(per_page).all()
    DBSession.close()
    return units

