# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hichao.points.config import (
    SQLALCHEMY_CONF_URL,
    POINT_SQLALCHEMY_CONF_URL,
)

Base = declarative_base()
point_engine = create_engine(POINT_SQLALCHEMY_CONF_URL, pool_recycle=60)
#Base.metadata.bind = point_engine
RDBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension(), bind=point_engine))


def point_dbsession_generator():
    return RDBSession()

engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle=60)
DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension(), bind=engine))


def dbsession_generator():
    _DBSession = scoped_session(
        sessionmaker(extension=ZopeTransactionExtension(), bind=engine))
    return _DBSession()
