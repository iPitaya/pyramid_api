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

class RefusedUser(Base):
    __tablename__ = 'forbidden_user'
    id = Column(INTEGER, primary_key = True)
    user_id = Column(INTEGER)
    end_time = Column(DATETIME)

@timeit('hichao_backend.m_refused_user')
#@deco_cache(prefix = 'black_list_user', recycle = DAY)
def user_in_black_list(user_id):
    DBSession = rdbsession_generator()
    now = datetime.datetime.now()
    _id = DBSession.query(RefusedUser.id).filter(RefusedUser.user_id == int(user_id)).filter(RefusedUser.end_time >= now).first()
    DBSession.close()
    if _id: return 1
    else: return None

