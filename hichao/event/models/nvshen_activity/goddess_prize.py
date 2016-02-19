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
from hichao.util.date_util import MINUTE, HOUR, FIVE_MINUTES
from hichao.event.models.nvshen_activity.goddess_winner import (
        get_number_by_prize_id,
        get_all_prize_id_by_user_id,
        )
import time
import datetime
from hichao.util.statsd_client import timeit
timer = timeit('hichao_backend.m_event_goddess_prize')

class GoddessPrize(Base):
    __tablename__ = "event_goddess_prize"
    id = Column(INTEGER,primary_key = True,autoincrement = True)    
    name = Column(VARCHAR(100))
    num = Column(INTEGER)
    rate = Column(Float)
    image = Column(VARCHAR(256))
    start_datetime = Column(DATETIME)
    end_datetime = Column(DATETIME)
    review = Column(TINYINT)
    prize_type = Column(TINYINT)
    virtual_money_id = Column(INTEGER)
   

    def __init__(self,name,num,rate,image,start_time,end_time,prize_type,money_id):
        self.name = name
        self.num = num
        self.rate = rate
        self.image = image
        self.start_datetime = start_time
        self.end_datetime = end_time
        self.review = 1
        self.prize_type = prize_type
        self.virtual_money_id = money_id

    def get_prize_id(self):
        return str(self.id)
    
    def get_prize_image(self):
        return str(self.image)
    
    def get_prize_name(self):
        return str(self.name)
    
    def to_ui_action(self):
        pass
    
    def get_virtual_money_id(self):
        return str(self.virtual_money_id)
    
@timer
@deco_cache(prefix = 'get_prize_ids', recycle = FIVE_MINUTES)
def get_all_prize_ids(today_time, use_cache = True):
    DBSession = dbsession_generator()
    prize_ids = DBSession.query(GoddessPrize.id).filter(
            today_time >= GoddessPrize.start_datetime).filter(
            today_time <= GoddessPrize.end_datetime).filter(
            GoddessPrize.review ==1).order_by(GoddessPrize.id.asc()).all()
    DBSession.close()
    prize_ids = [id[0] for id in prize_ids]
    return prize_ids

@timer
@deco_cache(prefix = 'get_prize_by_id', recycle = HOUR)
def get_prize_by_id(prize_id, use_cache = True):
    DBSession = dbsession_generator()
    prize = DBSession.query(GoddessPrize).filter(
        GoddessPrize.id ==int(prize_id)).filter(
        GoddessPrize.review == 1).first()
    DBSession.close()
    return prize

@timer
@deco_cache(prefix = 'get_prize_by_rate', recycle = FIVE_MINUTES)
def get_prize_by_rate(prize_type, rate, today_time, use_cache = True):
    DBSession = dbsession_generator()
    prize = DBSession.query(GoddessPrize).filter(
        today_time >= GoddessPrize.start_datetime).filter(
        today_time <= GoddessPrize.end_datetime).filter(
        GoddessPrize.rate == rate).filter(
        GoddessPrize.prize_type == prize_type).filter(GoddessPrize.review == 1).first()
    DBSession.close()
    return prize

@timer
def has_prize_left(prize_id,today_time):
    today = today_time.date()
    num = get_number_by_prize_id(prize_id, today, use_cache = True)
    prize = get_prize_by_id(prize_id, use_cache = True)
    if prize:
        if num < prize.num:
            return 1
    else:
        return 0

@timer
def get_prize_type_by_id(prize_id):
    DBSession = dbsession_generator()
    prize_type = DBSession.query(GoddessPrize.prize_type).filter(
        GoddessPrize.id ==int(prize_id)).filter(
        GoddessPrize.review == 1).first()
    DBSession.close()
    return prize_type[0] if prize_type else 0

@timer
def had_not_won_big_prize(user_id):
    prize_ids = get_all_prize_id_by_user_id(user_id)
    for prize_id in prize_ids:
        prize_type = get_prize_type_by_id(prize_id)
        if prize_type == 1:        
            return 0
    return 1
