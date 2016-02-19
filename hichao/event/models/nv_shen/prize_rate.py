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
        dbsession_generator,
        Base,
        )

class NvShenPrizeRate(Base):
    __tablename__ = 'ns_prize_rate'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    days = Column(DATETIME)
    prize_count = Column(INTEGER)
    prize_win_count = Column(INTEGER)
    prize_count_default = Column(INTEGER)

