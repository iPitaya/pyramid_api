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
        engine,
        Base,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE, FIVE_SECONDS
from hichao.util.statsd_client import timeit
import time
import datetime
timer = timeit('hichao_backend.m_event_goddess_winner')

class GoddessWinner(Base):
    __tablename__ = "event_goddess_winner"
    id = Column(INTEGER,primary_key = True,autoincrement = True)
    prize_id = Column(INTEGER)
    user_id = Column(INTEGER)
    ts = Column(TIMESTAMP)
    address = Column(VARCHAR(255))
    remarks = Column(VARCHAR(255), default = '')
    status = Column(TINYINT)
    tel = Column(VARCHAR(30))
    name = Column(VARCHAR(20))
    postcode = Column(INTEGER)
    
    def __init__(self,_prize_id,_user_id,_ts,_status,remarks = '',_address='',_tel = '0',_name = '',_postcode = 0):
        self.prize_id = _prize_id
        self.user_id = _user_id
        self.ts = _ts
        self.status = _status
        self.remarks = remarks
        self.address =_address        
        self.tel = _tel
        self.name = _name
        self.postcode = _postcode
        
    def get_winner_use_id(self):
        return str(self.user_id)
    
    def get_winner_prize_id(self):
        return str(self.prize_id)
@timer
def get_all_winner_ids():
    DBSession = dbsession_generator()
    winner_ids = DBSession.query(GoddessWinner.id).order_by(GoddessWinner.ts.desc()).limit(30).all()
    DBSession.close()
    winner_ids = [id[0] for id in winner_ids]
    return winner_ids

@timer
def get_winner_by_use_id(user_id):
    DBSession = dbsession_generator()
    winners = DBSession.query(GoddessWinner).filter(GoddessWinner.user_id == user_id).order_by(GoddessWinner.id.desc()).all()
    DBSession.close()
    return winners

@timer   
@deco_cache(prefix = 'get_winner_by_id', recycle = MINUTE)
def get_winner_by_id(winner_id):
    DBSession = dbsession_generator()
    winner = DBSession.query(GoddessWinner).filter(GoddessWinner.id == int(winner_id)).first()
    DBSession.close()
    return winner

@timer
@deco_cache(prefix = 'get_number_by_prize_id', recycle = FIVE_SECONDS)
def get_number_by_prize_id(prize_id,today,use_cache=True):
    today = today
    today_end = today + datetime.timedelta(days=1)
    DBSession = dbsession_generator()
    number = DBSession.query(func.count(GoddessWinner.prize_id)).filter(
        GoddessWinner.prize_id == prize_id).filter(
        GoddessWinner.ts >= today).filter(
        GoddessWinner.ts < today_end).first()
    if not number: number = 0
    else:number = number[0]
    DBSession.close()
    return number

@timer
def get_all_prize_id_by_user_id(user_id):
    DBSession = dbsession_generator()
    prize_ids = DBSession.query(GoddessWinner.prize_id).filter(
        GoddessWinner.user_id == int(user_id)).all()
    if prize_ids:
        id_list = [prize_id[0] for prize_id in prize_ids]
    else:
        id_list = []
    DBSession.close()
    return id_list

@timer
def add_winner(winner,dbsession):
    dbsession.add(winner)
    dbsession.flush()
    return True

@timer
def get_all_winner_count():
    DBSession = dbsession_generator()
    sum_winners = DBSession.query(func.count(GoddessWinner.id)).filter(GoddessWinner.remarks == 'goddess_clothes').first()
    DBSession.close()
    return sum_winners[0] if sum_winners else 0

@timer
def get_all_winners():
    DBSession = dbsession_generator()
    winners = DBSession.query(GoddessWinner).filter(GoddessWinner.remarks == 'goddess_clothes').order_by(GoddessWinner.ts.desc()).limit(30).all()
    DBSession.close()
    return winners

@timer
def get_today_winners_by_taday_time(today_time):
    today = today_time.date()
    today_end = today + datetime.timedelta(days=1)
    DBSession = dbsession_generator()
    today_winners = DBSession.query(func.count(GoddessWinner.id)).filter(GoddessWinner.ts >= today).filter(GoddessWinner.ts < today_end).filter(GoddessWinner.remarks == 'goddess_clothes').first()
    DBSession.close()
    return today_winners[0] if today_winners else 0
