# -*- coding:utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
        scoped_session,
        sessionmaker,
        )
from zope.sqlalchemy import ZopeTransactionExtension
from hichao.forum.config import (
        SQLALCHEMY_CONF_URL,
        SQLALCHEMY_THREADLOCAL_CONF_URL,
        SQLALCHEMY_SLAVE_CONF_URL,
        )
Base = declarative_base() 
engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60) 
DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = engine))

threadlocal_engine = create_engine(SQLALCHEMY_THREADLOCAL_CONF_URL, pool_recycle = 60) 
threadlocal_DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = threadlocal_engine))

rengine = create_engine(SQLALCHEMY_SLAVE_CONF_URL, pool_recycle = 60)
RDBSession = sessionmaker(bind = rengine)

def dbsession_generator():
    return DBSession()

def rdbsession_generator():
    return RDBSession()

def threadlocal_dbsession_generator():
    return threadlocal_DBSession()

session_factory = sessionmaker(bind = engine)
SESSION = scoped_session(session_factory)

def thread_img_dbsession_generator():
    return SESSION()

def new_session():
    engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
    session = scoped_session(sessionmaker(bind = engine))
    return session()

