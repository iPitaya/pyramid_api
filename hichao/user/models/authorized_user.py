# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        )
from hichao.user.models.db import (
        rdbsession_generator,
        Base,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import FIVE_MINUTES
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_authorized_user')

class AuthorizedUser(Base):
    __tablename__ = 'authorization_user'
    id = Column(INTEGER, primary_key = True)
    user_id = Column(INTEGER)
    review = Column(INTEGER)

    def __init__(self, user_id, review):
        self.user_id = user_id
        self.review = review

@timer
@deco_cache(prefix = 'authorized_user_ids', recycle = FIVE_MINUTES)
def get_authorized_user_ids(use_cache = True):
    DBSession = rdbsession_generator()
    user_ids = DBSession.query(AuthorizedUser.user_id).filter(AuthorizedUser.review == 1).all()
    DBSession.close()
    return [user_id[0] for user_id in user_ids]

