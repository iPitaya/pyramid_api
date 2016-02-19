# -*- coding:utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
        scoped_session,
        sessionmaker,
        )
from zope.sqlalchemy import ZopeTransactionExtension
from hichao.mall.config import (
        PANICBUYING_SQLALCHEMY_CONF_URL,
        ECSHOP_PANICBUYING_CONF_URL,
        TEST_ECSHOP_PANICBUYING_CONF_URL,
        BETA_ECSHOP_PANICBUYING_CONF_URL,
        )
import sys
import os


Panic_Base = declarative_base()
Panic_engine = create_engine(PANICBUYING_SQLALCHEMY_CONF_URL, pool_recycle = 60)
Panic_Base.metadata.bind = Panic_engine
Panic_DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = Panic_engine))

ecshop_Base = declarative_base()
#echop 
ecshop_engine = create_engine(ECSHOP_PANICBUYING_CONF_URL, pool_recycle = 60)
ecshop_Base.metadata.bind = ecshop_engine
ecshop_DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = ecshop_engine))

#ecshop test
Test_ecshop_engine = create_engine(TEST_ECSHOP_PANICBUYING_CONF_URL, pool_recycle = 60)
#Panic_Base.metadata.bind = Panic_engine
Test_ecshop_DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = Test_ecshop_engine))

#ecshop beta
Beta_ecshop_engine = create_engine(BETA_ECSHOP_PANICBUYING_CONF_URL, pool_recycle = 60)
Beta_ecshop_DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = Beta_ecshop_engine))

if os.environ.get('thrift_stage') == 'yanjiao':
    ecshop_Base.metadata.bind = ecshop_engine
elif os.environ.get('thrift_stage') == 'pre_release':
    ecshop_Base.metadata.bind = Beta_ecshop_engine
else:
    ecshop_Base.metadata.bind = Test_ecshop_engine

def panic_buying_dbsession_generator():
    return Panic_DBSession()

def ecshop_dbsession_generator():
    if os.environ.get('thrift_stage') == 'yanjiao':
        return  ecshop_DBSession()
    elif os.environ.get('thrift_stage') == 'pre_release':
        return  Beta_ecshop_DBSession()
    else:
        return Test_ecshop_DBSession()

