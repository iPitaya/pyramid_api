# -*- coding:utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from hichao.sku.config import (
        SQLALCHEMY_CONF_URL,
        SQLALCHEMY_SLAVE_CONF_URL,
        READONLY_SQLALCHEMY_CONF_URL,
        BRAND_SQLALCHEMY_CONF_URL,
        MONGO_CONF_URL,
        MONGO_DBNAME,
        MONGO_SKU_IMG_TABLE,
        )
import pymongo

Base = declarative_base()

mongo_conn = pymongo.Connection(MONGO_CONF_URL) 
mongo_db = mongo_conn[MONGO_DBNAME]
mongo_sku_img_table = mongo_db[MONGO_SKU_IMG_TABLE]

rengine = create_engine(READONLY_SQLALCHEMY_CONF_URL, pool_recycle = 60)
#Base.metadata.bind = rengine
RDBSession = sessionmaker(bind = rengine)

def rdbsession_generator():
    return RDBSession()

engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = engine))

slave_engine = create_engine(SQLALCHEMY_SLAVE_CONF_URL, pool_recycle = 60)
SLAVE_DBSession = sessionmaker(bind = slave_engine)

def dbsession_generator():
    _DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = engine))
    return _DBSession()

def sku_img_size_dbsession_generator():
    return SLAVE_DBSession()

def slave_dbsession_generator():
    return SLAVE_DBSession()

brand_engine = create_engine(BRAND_SQLALCHEMY_CONF_URL, pool_recycle = 60)
BDBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = brand_engine))

def bdbsession_generator():
    return BDBSession()

