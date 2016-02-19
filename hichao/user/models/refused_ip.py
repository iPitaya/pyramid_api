# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        BIGINT,
        DATETIME,
        )
from hichao.user.models.db import (
        Base,
        rdbsession_generator,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import (
        HALF_MINUTE,
        DAY)
import time
import datetime
from hichao.util.statsd_client import timeit

class RefusedIP(Base):
    __tablename__ = 'forbidden_ip'
    id = Column(INTEGER, primary_key = True)
    ip = Column(INTEGER)
    end_time = Column(DATETIME)

@timeit('hichao_backend.m_refused_ip')
#@deco_cache(prefix = 'black_list_user', recycle = DAY)
def ip_in_black_list(ip):
    DBSession = rdbsession_generator()
    now = datetime.datetime.now()
    _id = DBSession.query(RefusedIP.id).filter(RefusedIP.ip == int(ip)).filter(RefusedIP.end_time >= now).first()
    DBSession.close()
    if _id: return 1
    else: return None

