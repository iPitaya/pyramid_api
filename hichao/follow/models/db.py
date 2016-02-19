from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension
from hichao.follow.config import SQLALCHEMY_CONF_URL, SQLALCHEMY_SLAVE_CONF_URL

Base = declarative_base()

engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = engine))

def dbsession_generator():
    return DBSession()

rengine = create_engine(SQLALCHEMY_SLAVE_CONF_URL, pool_recycle = 60)
Base.metadata.bind = rengine
RDBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = rengine))

def rdbsession_generator():
    return RDBSession()

