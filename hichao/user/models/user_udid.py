#-*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        )
from hichao.user.models.db import (
        Base,
        udid_dbsession_generator,
        )
from hichao.util.statsd_client import timeit

class UserUdid(Base):
    __tablename__ = 'user_udid'
    id = Column('user_udid_id', INTEGER, primary_key = True, autoincrement = True)
    user_id = Column(INTEGER)
    openUDID = Column(VARCHAR(128))
    mac = Column(VARCHAR(128))

@timeit('hichao_backend.m_user_udid')
def user_is_exist(user_id, mac):
    DBSession = udid_dbsession_generator()
    user = DBSession.query(UserUdid).filter(UserUdid.user_id == user_id).filter(UserUdid.mac == mac).first()
    DBSession.close()
    if user:
        return 1
    else:
        return 0

