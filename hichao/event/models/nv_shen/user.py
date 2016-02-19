# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        func,
        TIMESTAMP,
        )
from hichao.event.models.db import (
        dbsession_generator,
        Base,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import WEEK

class NvShenUser(Base):
    __tablename__ = 'ns_user'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    user_id = Column(INTEGER, unique = True, index = True)
    
    def __init__(self, user_id):
        self.user_id = user_id

@deco_cache(prefix = 'nv_shen_quan_user', recycle = WEEK)
def get_nv_shen_user(user_id, use_cache = True):
    DBSession = dbsession_generator()
    user = DBSession.query(NvShenUser).filter(NvShenUser.user_id == int(user_id)).first()
    if user: res = 1
    else: res = 0
    DBSession.close()
    return res

def add_nv_shen_user(user_id):
    try:
        DBSession = dbsession_generator()
        user = NvShenUser(user_id)
        DBSession.add(user)
        DBSession.flush()
        DBSession.commit()
        return 1
    except Exception, ex:
        print Exception, ex
        DBSession.rollback()
        return 0
    finally:
        DBSession.close()
        get_nv_shen_user(user_id, use_cache = False)

