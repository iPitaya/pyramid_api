#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, Text, String, VARCHAR, FLOAT
from hichao.publish.models.db import dbsession_generator, Base
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_publish_olduser')

class OldUser(Base):
    __tablename__ = 'user'

    id = Column('user_id', Integer,primary_key=True,autoincrement=True)
    username = Column(VARCHAR(64))
    password = Column(VARCHAR(128))
    email = Column(VARCHAR(128))
    url = Column(VARCHAR(256))
    role = Column(Integer)
    user_type = Column(VARCHAR(64))
    open_id = Column(VARCHAR(64))
    token = Column(VARCHAR(64))
    gender = Column(Integer)
    location = Column(VARCHAR(64))
    identifier = Column(VARCHAR(64))
    apple_uid = Column(VARCHAR(32))
    last_date = Column(VARCHAR(20))
    register_date = Column(VARCHAR(20))
    avatar = Column(VARCHAR(256))

@timer
def get_user_id_by_name(name):
    DBSession = dbsession_generator()
    old_user_id = DBSession.query(OldUser).filter(OldUser.username==name).first().id
    DBSession.close()
    return old_user_id

@timer
def editor_user_dict():
    DBSession = dbsession_generator()
    user_list = DBSession.query(OldUser).filter(OldUser.user_type.in_(['star_fake', 'topic_fake'])).all()
    DBSession.close()
    user_dict =  dict([(i.username, i.id) for i in user_list])
    return user_dict

@timer
def fake_user_dict():
    DBSession = dbsession_generator()
    user_list = DBSession.query(OldUser).filter(OldUser.user_type.in_(['star_fake', 'topic_fake'])).all()
    DBSession.close()
    user_dict =  dict([(i.id, i) for i in user_list])
    return user_dict

#print get_user_id_by_name('Betty')
#editor_user_dict()

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

