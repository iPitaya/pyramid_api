# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        func,
        DATETIME,
        TIMESTAMP,
        VARCHAR,
        DECIMAL,
        )
from sqlalchemy.types import Float
from sqlalchemy.dialects.mysql import TINYINT
from hichao.event.models.db import (
        dbsession_generator,
        Base,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE, TEN_SECONDS
from hichao.event.models.nvshen_activity.goddess_times import get_times_by_datatime
import time
import datetime
from hichao.util.statsd_client import timeit
timer = timeit('hichao_backend.m_event_goddess_record')


class GoddessRecord(Base):
    __tablename__ = 'event_goddess_record'
    id = Column(INTEGER,primary_key = True,autoincrement = True)
    user_id = Column(INTEGER)
    dt = Column(DATETIME)
    times = Column(INTEGER)
    shared = Column(TINYINT)

    def __init__(self,user_id,today_time,times,shared):
        self.user_id = user_id
        self.dt = today_time
        self.times = times
        self.shared = shared

def have_chance_for_prize(user_id,today_time,dbsession):
    todaytime = today_time.date()
    times = get_times_by_datatime(todaytime, use_cache = True)
    if times:
        userrecord = get_record_by_user_id(user_id,todaytime, use_cache = True)
        if not userrecord:
            res = add_record(user_id,today_time,dbsession)
            get_record_by_user_id(user_id,todaytime, use_cache = False)
            return 1 if res else 2
        else:
            if userrecord.times < times:
                res = update_record(userrecord,today_time,dbsession)
                get_record_by_user_id(user_id,todaytime, use_cache = False)     
                return 1 if res else 2
            else:
                return 0
    else:
        return 0
    
@timer
@deco_cache(prefix = 'get_left_times_by_user_id', recycle = MINUTE)
def get_left_times_by_user_id(user_id,today,use_cache=True):
    today = today
    today_end = today + datetime.timedelta(days=1)
    times = get_times_by_datatime(today, use_cache = True)  
    DBSession = dbsession_generator()
    record = DBSession.query(GoddessRecord).filter(
        GoddessRecord.user_id == int(user_id)).filter(
        GoddessRecord.dt >= today).filter(
        GoddessRecord.dt < today_end).first()
    DBSession.close()
    left_times = 0
    if times:
        if record:
            left_times = times - record.times
        else:
            left_times = times
    return left_times if left_times>0 else 0

@timer
@deco_cache(prefix = 'get_record_by_user_id', recycle = MINUTE)
def get_record_by_user_id(user_id,today, use_cache=True):
    today = today
    today_end = today + datetime.timedelta(days=1)
    DBSession = dbsession_generator()
    userrecord = DBSession.query(GoddessRecord).filter(
            GoddessRecord.user_id == int(user_id)).filter(
            GoddessRecord.dt > today).filter(
            GoddessRecord.dt < today_end).first()
    DBSession.close()
    return userrecord

@timer
def get_number_record():
    DBSession = dbsession_generator()
    number = DBSession.query(func.count(GoddessRecord.id)).first()
    DBSession.close()  
    return number[0] if number else 0

@timer
def add_record(user_id,today_time,DBSession,times = 1):
    shared = 0
    one_record = GoddessRecord(user_id,today_time,times,shared)
    DBSession.add(one_record)
    DBSession.flush()
    return one_record

@timer     
def update_record(userrecord,today_time,DBSession):
    userrecord.times += 1 
    userrecord.dt = today_time
    DBSession.add(userrecord)
    DBSession.flush()
    return True    

@timer
def reduce_times(userrecord,today_time,DBSession):
    userrecord.times -= 1 
    userrecord.dt = today_time
    DBSession.add(userrecord)
    DBSession.flush()
    return True 
