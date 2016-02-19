# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        func,
        TIMESTAMP,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.event.models.db import (
        dbsession_generator,
        Base,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import DAY, MINUTE, FIVE_MINUTES
import time
import datetime

class NvShenPrizeNew(Base):
    __tablename__ = 'ns_prize_new'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    price = Column(INTEGER)
    user_id = Column(INTEGER)
    review = Column(TINYINT)
    create_ts = Column(TIMESTAMP)
    update_ts = Column(TIMESTAMP)

    def __init__(self, price, user_id, review = 1):
        self.price = price
        self.user_id = user_id
        self.review = review

def get_prize_info(user_id, use_cache = True):
    today = datetime.datetime.now().date()
    ts_today = today.strftime('%Y-%m-%d')
    return _get_prize_info(user_id, ts_today, use_cache = use_cache)

@deco_cache(prefix = 'prize_info_today', recycle = DAY)
def _get_prize_info(user_id, ts, use_cache = True):
    DBSession = dbsession_generator()
    info = DBSession.query(NvShenPrizeNew).filter(NvShenPrizeNew.user_id == int(user_id)).filter(NvShenPrizeNew.create_ts >= ts).first()
    DBSession.close()
    return info

@deco_cache(prefix = 'ns_today_prize_users', recycle = MINUTE)
def get_today_users(use_cache = True):
    today = datetime.datetime.now().date()
    ts_today = today.strftime('%Y-%m-%d')
    DBSession = dbsession_generator()
    users = DBSession.query(NvShenPrizeNew.user_id).filter(NvShenPrizeNew.create_ts >= ts_today).order_by(NvShenPrizeNew.create_ts.desc()).all()
    if not users: users = []
    users = [id[0] for id in users]
    DBSession.close()
    return users


