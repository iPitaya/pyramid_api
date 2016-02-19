# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        func,
        VARCHAR,
        TIMESTAMP,
        )
from hichao.event.models.db import (
        dbsession_generator,
        Base,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import WEEK

class NvShenUserNew(Base):
    __tablename__ = 'ns_user_new'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    user_id = Column(INTEGER)
    alipay = Column(VARCHAR(255))
    ts = Column(TIMESTAMP)

    def __init__(self, user_id, alipay):
        self.user_id = user_id
        self.alipay = alipay

@deco_cache(prefix = 'is_ns_user', recycle = WEEK)
def is_nv_shen_user(user_id, use_cache = True):
    DBSession = dbsession_generator()
    user = DBSession.query(NvShenUserNew).filter(NvShenUserNew.user_id == int(user_id)).first()
    if user: res = 1
    else: res = 0
    DBSession.close()
    return res

@deco_cache(prefix = 'alipay_related', recycle = WEEK)
def alipay_related(alipay, use_cache = True):
    DBSession = dbsession_generator()
    user = DBSession.query(NvShenUserNew).filter(NvShenUserNew.alipay == alipay).first()
    if user: res = 1
    else: res = 0
    DBSession.close()
    return res

@deco_cache(prefix = 'ns_user', recycle = WEEK)
def get_nv_shen_user(user_id, use_cache = True):
    DBSession = dbsession_generator()
    user = DBSession.query(NvShenUserNew).filter(NvShenUserNew.user_id == int(user_id)).first()
    DBSession.close()
    return user

def add_nv_shen_user(user_id, alipay):
    try:
        DBSession = dbsession_generator()
        user = NvShenUserNew(user_id, alipay)
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
        is_nv_shen_user(user_id, use_cache = False)
        alipay_related(alipay, use_cache = False)


