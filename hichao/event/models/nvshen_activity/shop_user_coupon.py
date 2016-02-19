# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.event.models.db import (
        #shop_dbsession_generator,
        ShopBase,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE
import time
from hichao.util.statsd_client import timeit
timer = timeit('hichao_backend.m_event_shop_soupon')

class ShopUserCoupon(ShopBase):
    __tablename__ = "ecs_user_coupon"
    id = Column(INTEGER,primary_key = True,autoincrement = True)
    act_id = Column(INTEGER)
    user_id = Column(INTEGER)    
    status = Column(TINYINT)
    create_date = Column(INTEGER)
    #used_time = Column(INTEGER)
    #pay_order_id = Column(INTEGER)
    
    def __init__(self,_act_id,_user_id,today_time,_status = 0):
        self.act_id = _act_id
        self.user_id = _user_id        
        self.create_date = today_time
        self.status = _status

@timer
def add_coupon_to_user(act_id,user_id,today_time,dbsession):
    _today_time = int(time.mktime(today_time))
    user_coupon = ShopUserCoupon(act_id,user_id,_today_time)
    dbsession.add(user_coupon)
    dbsession.flush()

