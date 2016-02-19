# -*- coding:utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hichao.tuangou.config import (
        SQLALCHEMY_CONF_URL,
        SQLALCHEMY_SLAVE_CONF_URL,
        SQLALCHEMY_BETA_CONF_URL
        )

Base = declarative_base()

slave_engine = create_engine(SQLALCHEMY_SLAVE_CONF_URL, pool_recycle = 60)
SLAVE_DBSession = sessionmaker(bind = slave_engine)

def slave_dbsession_generator():
    return SLAVE_DBSession()
