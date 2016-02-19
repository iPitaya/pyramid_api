# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        TIMESTAMP,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.base.models.base_component import BaseComponent
from hichao.shop.models.db import (
        Base,
        act_dbsession_generator,
        )
from hichao.cache.cache import deco_cache
from hichao.util.statsd_client import timeit
from hichao.util.image_url import build_ec_event_icon_image_url
from hichao.util.date_util import (
        MINUTE,
        )
from icehole_client.files_client  import  get_image_filename
import datetime
import time

timer = timeit('hichao_backend.m_activity_info')
timer_mysql = timeit('hichao_backend.m_activity_info.mysql')

IMAGE_FILENAME_SPACE = 'tuangou'

class Activity(Base, BaseComponent):
    __tablename__ = 'pageant'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    img_falls = Column(VARCHAR(255), nullable = False, default = '')
    start_datetime = Column(TIMESTAMP, nullable = False)
    end_datetime = Column(TIMESTAMP, nullable = False)
    preheat_datetime = Column(TIMESTAMP, nullable = False)
    review = Column(TINYINT, nullable = False, default = 0)     # -1:被拒绝,0:未审核,1:等待报名,2:等待编辑,3:等待发布

    def get_component_event_icon(self):
        img = get_image_filename(IMAGE_FILENAME_SPACE, self.img_falls)
        if img:
            return build_ec_event_icon_image_url(img.filename)
        return self.img_falls

@timer
@deco_cache(prefix = 'activity_info', recycle = MINUTE)
@timer_mysql
def get_activity_by_id(act_id, use_cache = True):
    DBSession = act_dbsession_generator()
    now = datetime.datetime.now()
    activity = DBSession.query(Activity).filter(Activity.id == int(act_id)).filter(Activity.review == 3).filter(Activity.start_datetime <= now).filter(Activity.end_datetime > now).first()
    DBSession.close()
    return activity

@timer
@deco_cache(prefix = 'now_has_activity', recycle = MINUTE)
@timer_mysql
def has_valid_activitys(use_cache = True):
    DBSession = act_dbsession_generator()
    now = datetime.datetime.now()
    activity = DBSession.query(Activity).filter(Activity.review == 3).filter(Activity.start_datetime <= now).filter(Activity.end_datetime > now).first()
    DBSession.close()
    return 1 if activity else 0

