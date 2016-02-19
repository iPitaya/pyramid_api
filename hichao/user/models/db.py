from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension


Base = declarative_base()

from sqlalchemy import create_engine
from hichao.user.config import (
        SQLALCHEMY_CONF_URL,
        UDID_SQLALCHEMY_CONF_URL,
        SQLALCHEMY_SLAVE_CONF_URL,
        DEVICE_SQLALCHEMY_CONF_URL,
        DEVICE_SQLALCHEMY_SLAVE_CONF_URL,
        )

engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = engine))
Base.metadata.bind = engine

rengine = create_engine(SQLALCHEMY_SLAVE_CONF_URL, pool_recycle = 60)
RDBSession = sessionmaker(bind = rengine)

udid_engine = create_engine(UDID_SQLALCHEMY_CONF_URL, pool_recycle = 60)
UDID_DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = udid_engine))

session_factory = sessionmaker(bind=engine)
USER_SESSION = scoped_session(session_factory)

device_engine = create_engine(DEVICE_SQLALCHEMY_CONF_URL, pool_size = 30, pool_recycle = 60)
DEVICE_SESSION = sessionmaker(bind = device_engine)

r_device_engine = create_engine(DEVICE_SQLALCHEMY_SLAVE_CONF_URL, pool_size = 30, pool_recycle = 60)
R_DEVICE_SESSION = sessionmaker(bind = r_device_engine)

def user_dbsession_generator():
    return USER_SESSION()

def CreateSession(db_uri):
    engine = create_engine(db_uri, pool_recycle = 60)
    d_session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
    d_session.configure(bind=engine)
    session = d_session()
    return session

def CreateEngine(db_uri):
    return create_engine(db_uri, pool_recycle = 60)

def dbsession_generator():
    return DBSession()

def rdbsession_generator():
    return RDBSession()

def new_dbsession_generator():
    engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
    DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = engine))
    DBSession.configure(bind=engine)
    return DBSession

def udid_dbsession_generator():
    return UDID_DBSession()

def new_session():
    engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
    session = scoped_session(sessionmaker(bind = engine))
    return session()

def device_dbsession_generator():
    return DEVICE_SESSION()

def r_device_dbsession_generator():
    return R_DEVICE_SESSION()

