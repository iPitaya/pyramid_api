# -*- coding:utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import(
        scoped_session,
        sessionmaker,
        )
from hichao.topic.config import SQLALCHEMY_CONF_URL
from hichao.topic.config import SQLALCHEMY_SLAVE_CONF_URL
from hichao.event.config import SQLALCHEMY_CONF_SHOP_URL

Base = declarative_base()
engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

Base = declarative_base()
engine = create_engine(SQLALCHEMY_SLAVE_CONF_URL, pool_recycle = 60)
Base.metadata.bind = engine
DBSession_slave = sessionmaker(bind = engine)

def dbsession_generator():
    return DBSession_slave()

def dbsession_generator_write():
    return DBSession()

ShopBase = declarative_base()
shop_enging = create_engine(SQLALCHEMY_CONF_SHOP_URL,pool_recycle =60)
ShopBase.metadata.bind = shop_enging
shop_dbsession = sessionmaker(bind = shop_enging)

def shop_dbsession_generator():
    return shop_dbsession()
