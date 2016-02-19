# -*- coding:utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from hichao.shop.config import (
        SQLALCHEMY_CONF_URL,
        ACTIVITY_SQLALCHEMY_CONF_URL,
        )

Base = declarative_base()
engine = create_engine(SQLALCHEMY_CONF_URL, pool_recycle = 60)
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

activity_engine = create_engine(ACTIVITY_SQLALCHEMY_CONF_URL, pool_recycle = 60)
ACT_DBSession = sessionmaker(bind = activity_engine)

def dbsession_generator():
    return DBSession()

def act_dbsession_generator():
    return ACT_DBSession()

