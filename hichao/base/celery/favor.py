# -*- coding: utf-8 -*-
import celery

from hichao.sku.models.sku import Sku
from hichao.sku.models.spider_sku import SpiderSku
from hichao.base.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWD

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

import transaction

WRITE_MYSQL_HOST = MYSQL_HOST
WRITE_MYSQL_PORT = MYSQL_PORT
WRITE_MYSQL_USER = MYSQL_USER
WRITE_MYSQL_PASSWD = MYSQL_PASSWD
SQLALCHEMY_CONF_URL_WODFAN = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (WRITE_MYSQL_USER, WRITE_MYSQL_PASSWD, WRITE_MYSQL_HOST, WRITE_MYSQL_PORT, 'wodfan')
engine = create_engine(SQLALCHEMY_CONF_URL_WODFAN, pool_recycle = 60)
RDBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = engine))

SKU_WRITE_MYSQL_HOST = MYSQL_HOST
SKU_WRITE_MYSQL_USER = MYSQL_USER
SKU_WRITE_MYSQL_PASSWD = MYSQL_PASSWD
SKU_WRITE_MYSQL_PORT = MYSQL_PORT
SKU_SQLALCHEMY_CONF_URL_WODFAN = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (SKU_WRITE_MYSQL_USER, SKU_WRITE_MYSQL_PASSWD, SKU_WRITE_MYSQL_HOST, SKU_WRITE_MYSQL_PORT, 'sku')
sku_engine = create_engine(SKU_SQLALCHEMY_CONF_URL_WODFAN, pool_recycle = 60)
SKU_RDBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = sku_engine))

rdb = RDBSession()
sku_rdb = SKU_RDBSession()

sku_count = 0
spider_sku_count = 0
thresh_hold = 10000
# params:
# type_id 单品id
@celery.task
def add_sku_favor_num_by_id(sku_id, n):
    global sku_count
    try:
        sku = sku_rdb.query(Sku).filter(Sku.sku_id == sku_id).first()
        if sku:
            sku_count += 1
            sku.favor = n
            sku_rdb.add(sku)
        
        if sku_count == thresh_hold:
            sku_count = 0
            transaction.commit()
    except:
        print "transaction has been aborted"
        transaction.abort()

# params:
# type_id 单品id
@celery.task
def add_spider_sku_favor_num_by_id(spider_sku_id, n):
    global spider_sku_count
    try:
        sku = RDBSession.query(SpiderSku).filter(SpiderSku.sku_id == spider_sku_id).first()
        if sku:
            #print spider_sku_id, ' ', n
            spider_sku_count += 1
            sku.favor = n
            rdb.add(sku)
            transaction.commit()
        if spider_sku_count == thresh_hold:
            spider_sku_count = 0
            transaction.commit()
    except:
        print "transaction has been aborted"
        transaction.abort()

if __name__ == '__main__':
    add_sku_favor_num_by_id(1656713, 1)
