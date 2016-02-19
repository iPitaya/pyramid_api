# -*- coding:utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
        scoped_session,
        sessionmaker,
        )
from zope.sqlalchemy import ZopeTransactionExtension
import MySQLdb
from hichao.base.config import MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT

#MYSQL_USER='release'
#MYSQL_PASSWD='release'
#MYSQL_HOST='192.168.1.68'
#MYSQL_PORT=3307

SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s' % (MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'msgcenter')

Base = declarative_base()
engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
Base.metadata.bind = engine
DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = engine))

def dbsession_generator():
    return DBSession()

