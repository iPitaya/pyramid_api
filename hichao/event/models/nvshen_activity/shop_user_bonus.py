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
from sqlalchemy.dialects.mysql import TINYINT
from hichao.event.models.db import (
        shop_dbsession_generator,
        ShopBase,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE
import time
import datetime
from hichao.util.statsd_client import timeit
timer = timeit('hichao_backend.m_event_shop_bonus')

class ShopUserBonus(ShopBase):
    __tablename__ = "ecs_user_bonus"
    id = Column(INTEGER,primary_key = True,autoincrement = True)
    bonus_id = Column(INTEGER)
    user_id = Column(INTEGER)    
    status = Column(TINYINT)
    create_date = Column(INTEGER)
    #used_time = Column(INTEGER)
    #pay_order_id = Column(INTEGER)
    
    def __init__(self,_bonus_id,_user_id,today_time,_status = 0):
        self.bonus_id = _bonus_id
        self.user_id = _user_id        
        self.create_date = today_time
        self.status = _status
        
@timer      
def add_bonus_to_user(bonus_id,user_id,today_time,dbsession):
    _today_time = int(time.mktime(today_time))
    user_bonus = ShopUserBonus(bonus_id,user_id,_today_time)
    dbsession.add(user_bonus)
    dbsession.flush()
    
if __name__== "__main__":
    today_time = datetime.datetime.now()
    print type(today_time)
    today_time =today_time.strftime("%Y-%m-%d %H:%M:%S")
    timeArray = time.strptime(today_time, "%Y-%m-%d %H:%M:%S")
    print timeArray
    try:
        dbsession = shop_dbsession_generator()
        add_bonus_to_user(34,100000,timeArray,dbsession)
        dbsession.commit()
        dbsession.close()
        print "done"
    except Exception,ex:
        print Exception,ex
        dbsession.rollback()
        dbsession.close()

