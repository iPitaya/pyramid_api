from sqlalchemy import (
    Column,
    Integer,
    Text,
    create_engine,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension
from hichao.collect.config import SQLALCHEMY_CONF_URL, SYNC_SQLALCHEMY_CONF_URL

Base = declarative_base()

engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
#Base.metadata.bind = engine
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = engine))

def dbsession_generator():
    return DBSession()

sync_engine = create_engine(SYNC_SQLALCHEMY_CONF_URL, pool_recycle = 60)
Base.metadata.bind = sync_engine
SYNC_DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = sync_engine))

def sync_dbsession_generator():
    return SYNC_DBSession()

