# -*- coding:utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
        scoped_session,
        sessionmaker,
        )
from zope.sqlalchemy import ZopeTransactionExtension
from hichao.keywords.config import (
        SQLALCHEMY_CONF_URL,
        UPDOWN_SQLALCHEMY_CONF_URL,
        UPDOWN_SQLALCHEMY_SLAVE_CONF_URL,
        )

Base = declarative_base()
engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
Base.metadata.bind = engine
DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = engine))

UP_Base = declarative_base()
UP_engine = create_engine(UPDOWN_SQLALCHEMY_CONF_URL, pool_recycle = 60)
UP_Base.metadata.bind = UP_engine
UP_DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = UP_engine))

R_UP_engine = create_engine(UPDOWN_SQLALCHEMY_SLAVE_CONF_URL, pool_recycle = 60)
R_UP_DBSession = sessionmaker(bind = R_UP_engine)

def dbsession_generator():
    return DBSession()

def up_down_dbsession_generator():
    return UP_DBSession()

def rup_down_dbsession_generator():
    return R_UP_DBSession()

