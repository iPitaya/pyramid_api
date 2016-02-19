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
from hichao.util.date_util import MINUTE, FIVE_MINUTES
import time
import datetime

class NvShenPrizeCount(Base):
    __tablename__ = 'ns_prize_count'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    lottery_count = Column(INTEGER, default = 2)
    is_win = Column(TINYINT)
    user_id = Column(INTEGER)
    review = Column(TINYINT)
    create_ts = Column(TIMESTAMP)
    update_ts = Column(TIMESTAMP)

    def __init__(self, user_id, lottery_count = 2, is_win = 0, review = 1):
        self.user_id = user_id
        self.lottery_count = lottery_count
        self.is_win = is_win
        self.review = review

@deco_cache(prefix = 'ns_today_prize_count', recycle = MINUTE)
def get_today_prize_count(use_cache = True):
    today = datetime.datetime.now().date()
    ts_today = today.strftime('%Y-%m-%d')
    DBSession = dbsession_generator()
    cnt = DBSession.query(func.count(NvShenPrizeCount.id)).filter(NvShenPrizeCount.create_ts >= ts_today).filter(NvShenPrizeCount.is_win == 1).first()
    if not cnt: cnt = 0
    else: cnt = cnt[0]
    DBSession.close()
    return cnt

@deco_cache(prefix = 'ns_all_prize_count', recycle = MINUTE)
def get_all_prize_count(use_cache = True):
    DBSession = dbsession_generator()
    cnt = DBSession.query(func.count(NvShenPrizeCount.id)).filter(NvShenPrizeCount.is_win == 1).first()
    if not cnt: cnt = 0
    else: cnt = cnt[0]
    DBSession.close()
    return cnt


