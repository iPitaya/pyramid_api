# -*- coding:utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
        scoped_session,
        sessionmaker,
        )
from zope.sqlalchemy import ZopeTransactionExtension
from hichao.upload.config import (
        SQLALCHEMY_CONF_URL,
        SQLALCHEMY_SLAVE_CONF_URL,
        )

Base = declarative_base()
engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = engine))
Base.metadata.bind = engine

rengine = create_engine(SQLALCHEMY_SLAVE_CONF_URL, pool_recycle = 60)
RDBSession = sessionmaker(bind = rengine)

def dbsession_generator():
    return DBSession()

def rdbsession_generator():
    return RDBSession()


if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

