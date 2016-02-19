# -*- coding:utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import(
        scoped_session,
        sessionmaker,
        )
from zope.sqlalchemy import ZopeTransactionExtension
from hichao.star.config import (
        SQLALCHEMY_CONF_URL,
        SQLALCHEMY_SLAVE_CONF_URL,
        )

Base = declarative_base()
engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
Base.metadata.bind = engine
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = engine))

rengine = create_engine(SQLALCHEMY_SLAVE_CONF_URL, pool_recycle = 60)
RDBSession = sessionmaker(bind = engine)

def dbsession_generator():
    _DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = engine))
    return _DBSession()

def rdbsession_generator():
    return RDBSession()

