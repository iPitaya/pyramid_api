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
from hichao.comment.config import (
        SQLALCHEMY_CONF_URL,
        READONLY_SQLALCHEMY_CONF_URL,
        )

Base = declarative_base()
engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
Base.metadata.bind = engine
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), bind = engine))

rengine = create_engine(READONLY_SQLALCHEMY_CONF_URL, pool_recycle = 60)
RDBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = rengine))

def dbsession_generator():
    return DBSession()

def rdbsession_generator():
    return RDBSession()

session_factory = sessionmaker(bind = engine)
SESSION = scoped_session(session_factory)

def subthread_img_dbsession_generator():
    return SESSION()

