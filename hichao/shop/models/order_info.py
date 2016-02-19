# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        DECIMAL,
        INTEGER,
        func,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.shop.models.db import(
        dbsession_generator,
        Base,
        )
from hichao.util.date_util import (
        WEEK,
        SEASONS,
        )
from hichao.base.models.base_component import BaseComponent
import time

class OrderInfo(Base):
    __tablename__ = 'ecs_order_info'
    order_id = Column(INTEGER, primary_key = True)
    order_amount_paid = Column(DECIMAL(10, 2, asdecimal = False), nullable = False, default = 0)
    order_status = Column(TINYINT, nullable = False, default = 0)
    ec_user_id = Column('user_id', INTEGER, nullable = False, default = 0)
    confirm_time = Column(INTEGER, nullable = False, default = 0)

def get_user_amount_paid(ec_user_id):
    DBSession = dbsession_generator()
    paid = DBSession.query(func.sum(OrderInfo.order_amount_paid)).filter(OrderInfo.ec_user_id == int(ec_user_id)).filter(OrderInfo.order_status == 4).first()
    if paid: paid = paid[0]
    DBSession.close()
    return paid if paid else 0

def get_user_amount_paid_by_season(ec_user_id, start_ts, end_ts):
    DBSession = dbsession_generator()
    paid = DBSession.query(func.sum(OrderInfo.order_amount_paid)).filter(OrderInfo.ec_user_id == int(ec_user_id)).filter(OrderInfo.order_status == 4).filter(OrderInfo.confirm_time + WEEK >= start_ts).filter(OrderInfo.confirm_time + WEEK < end_ts).first()
    if paid: paid = paid[0]
    DBSession.close()
    return paid if paid else 0

def get_last_season_paid_by_ecuser_id(ec_user_id):
    now = time.localtime()
    curr_month = now.tm_mon
    season_start_month = 1
    season_start_year = now.tm_year
    next_season_start_year = now.tm_year
    for season in SEASONS:
        if curr_month in season:
            season_start_month = season[0]
    next_season_start_month = (season_start_month + 3) % 12
    if season_start_month + 3 > 12:
        next_season_start_year = next_season_start_year + 1
    start_ts = time.mktime(time.strptime('{0}-{1}-1'.format(season_start_year, season_start_month), '%Y-%m-%d'))
    end_ts = time.mktime(time.strptime('{0}-{1}-1'.format(next_season_start_year, next_season_start_month), '%Y-%m-%d'))
    return get_user_amount_paid_by_season(ec_user_id, start_ts, end_ts)

