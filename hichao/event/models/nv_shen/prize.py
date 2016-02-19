# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        func,
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
from hichao.util.date_util import MINUTE
import time
import datetime

class NvShenPrize(Base):
    __tablename__ = 'ns_prize'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    order_id = Column('order_num', VARCHAR(128))
    real_price = Column(DECIMAL(20, 2, asdecimal = False))
    user_id = Column(INTEGER)
    review = Column(TINYINT, default = 1)
    alipay = Column(VARCHAR(64))
    create_ts = Column(TIMESTAMP)
    update_ts = Column(TIMESTAMP)

    def __init__(self, user_id, order_id, real_price):
        self.user_id = user_id
        self.order_id = order_id
        self.real_price = real_price
        self.review = 1

@deco_cache(prefix = 'nv_shen_quan_prize_count', recycle = MINUTE)
def get_today_prize_count():
    today = datetime.datetime.now()
    ts_today = today.strftime('%Y-%m-%d')
    ts_today_end = (today + datetime.timedelta(1)).strftime('%Y-%m-%d')
    DBSession = dbsession_generator()
    cnt = DBSession.query(func.count(NvShenPrize.id)).filter(NvShenPrize.create_ts >= ts_today).filter(NvShenPrize.create_ts < ts_today_end).first()
    if not cnt: cnt = 0
    else: cnt = cnt[0]
    DBSession.close()
    return cnt

@deco_cache(prefix = 'nv_shen_quan_prize_orders', recycle = MINUTE)
def get_prize_orders():
    today = datetime.datetime.now()
    ts_today = today.strftime('%Y-%m-%d')
    ts_today_end = (today + datetime.timedelta(1)).strftime('%Y-%m-%d')
    DBSession = dbsession_generator()
    orders = DBSession.query(NvShenPrize).filter(NvShenPrize.create_ts >= ts_today).filter(NvShenPrize.create_ts < ts_today_end).order_by(NvShenPrize.create_ts.desc()).limit(20).all()
    if not orders: orders = []
    DBSession.close()
    return orders

