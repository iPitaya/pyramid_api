# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        )
from hichao.star.models.db import(
        dbsession_generator,
        rdbsession_generator,
        Base
        )
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_star_fakeuser')

class fakeUser(Base):
    __tablename__ = 'fake_user'
    id = Column(INTEGER, primary_key = True)
    fake_name = Column(VARCHAR(64), nullable = False)
    avatar_url = Column(VARCHAR(1024), nullable = False)

    def __init__(self, id, fake_name, avatar_url):
        self.id = id
        self.fake_name = fake_name
        self.avatar_url = avatar_url

@timer
def get_fake_user_by_id(fake_user_id):
    DBSession = rdbsession_generator()
    fake_user = DBSession.query(fakeUser).filter(fakeUser.id == fake_user_id).first()
    DBSession.close()
    return fake_user

@timer
def get_fake_user_by_name(fake_user_name):
    DBSession = rdbsession_generator()
    fake_user = DBSession.query(fakeUser).filter(fakeUser.fake_name.like(fake_user_name)).first()
    DBSession.close()
    return fake_user

@timer
def add_fake_user(id, fake_name, avatar_url):
    fake_user = fakeUser(id, fake_name, avatar_url)
    try:
        DBSession = dbsession_generator()
        DBSession.add(fake_user)
        DBSession.flush()
    except Exception, ex:
        DBSession.rollback()
        print Exception, ':', ex
        return 0
    finally:
        DBSession.close()
    return 1

@timer
def delete_fake_user(fake_user_id):
    try:
        DBSession = dbsession_generator()
        DBSession.query(fakeUser).filter(fakeUser.id == fake_user_id).delete()
    except Exception, ex:
        DBSession.rollback()
        print Exception, ':', ex
    finally:
        DBSession.close()
