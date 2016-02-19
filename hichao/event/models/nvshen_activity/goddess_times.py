# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        DATETIME,
        )
from hichao.event.models.db import (
        dbsession_generator,
        Base,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import HOUR
import time
import datetime
from hichao.util.statsd_client import timeit
timer = timeit('hichao_backend.m_event_goddess_timer')

class GoddessTimes(Base):
    __tablename__ = "event_goddess_times"
    id = Column(INTEGER,primary_key = True,autoincrement = True)
    dt = Column(DATETIME)
    times = Column(INTEGER)
    
    def __init__(self,_dt,_times):
        self.dt = _dt
        self.times = _times
        
@timer       
@deco_cache(prefix = 'get_times_by_datetime', recycle = HOUR)
def get_times_by_datatime(today, use_cache = True):
    today = today
    today_end = today + datetime.timedelta(days=1)
    DBSession = dbsession_generator()
    times = DBSession.query(GoddessTimes.times).filter(GoddessTimes.dt >= today).filter(GoddessTimes.dt < today_end).first()
    DBSession.close()
    return times[0] if times else 0

