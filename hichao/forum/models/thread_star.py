# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        TIMESTAMP,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.forum.models.db import (
        Base,
        rdbsession_generator,
        )
import time
import transaction

class ThreadStar(Base):
    __tablename__ = "thread_star"
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    thread_id = Column(INTEGER, nullable = False)
    star_id = Column(INTEGER, nullable = False)
    review = Column(TINYINT, nullable = False, default = 0)
    ts = Column(TIMESTAMP, nullable = False)

    def __init__(self, thread_id, star_id, review):
        self.thread_id = thread_id
        self.star_id = star_id
        self.review = review

def get_thread_stars(ts, num):
    DBSession = rdbsession_generator()
    ids = DBSession.query(ThreadStar).filter(ThreadStar.review ==
            1).filter(ThreadStar.ts < ts).order_by(ThreadStar.ts.desc()).limit(num).all()
    DBSession.close()
    return ids

