# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        BIGINT,
        )
from hichao.winner_info.models.db import (
        Base,
        dbsession_generator,
        rdbsession_generator,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import FIVE_MINUTES

import transaction
import time

class WinnerList(Base):
    __tablename__ = 'winner_list'
    id = Column('id', INTEGER, primary_key = True, autoincrement = True)
    user_id = Column(BIGINT, nullable = False)
    activity_id = Column(INTEGER, nullable = False)
    activity_type = Column(VARCHAR(32), nullable = False)
    show_topic_id = Column(INTEGER, nullable = False)
    deadline = Column(BIGINT, nullable = False)
    comment = Column(VARCHAR(256), nullable = True)

    def __init__(self, user_id, activity_id, activity_type, show_topic_id, deadline, comment = ''):
        self.user_id = user_id
        self.activity_id = activity_id
        self.activity_type = activity_type
        self.show_topic_id = show_topic_id
        self.deadline = deadline
        self.comment = comment


@deco_cache(prefix = 'topic_winner_list', recycle = FIVE_MINUTES)
def get_winner_list(topic_id, use_cache = True):
    DBSession = dbsession_generator()
    winners = DBSession.query(WinnerList.user_id).filter(WinnerList.show_topic_id ==
            topic_id).filter(WinnerList.deadline >= time.time()).all()
    DBSession.close()
    winner_list = [str(winner[0]) for winner in winners]
    return winner_list

