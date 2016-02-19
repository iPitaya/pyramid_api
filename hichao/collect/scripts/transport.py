# -*- coding: utf-8 -*-
import time
from hichao.collect.models.db import Base, DBSession
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, Text, String, VARCHAR, FLOAT, func
from hichao.base.lib.redis import redis, redis_key
from hichao.collect.models.collect import Collect, COLLECT_KEY_BY_TYPE

class Star_collection(Base):
    __tablename__ = 'star_collection'
    id = Column('star_collection_id', Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, nullable = False)
    star_id = Column(Integer, nullable = False)
    device_id = Column(VARCHAR(32))
    publish_date = Column(Integer)

    def __init__(self, user_id, star_id, device_id = '', publish_date = int(time.time())):
        self.user_id = user_id
        self.star_id = star_id
        self.device_id = device_id
        self.publish_date = str(time.time())

class Sku_collection(Base):
    __tablename__ = 'sku_collection'
    id = Column('sku_collection_id', Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, nullable = False)
    sku_id = Column(Integer, nullable = False)
    device_id = Column(VARCHAR(32))
    publish_date = Column(Integer)

    def __init__(self, user_id, sku_id, device_id = '', publish_date = int(time.time())):
        self.user_id = user_id
        self.sku_id = sku_id
        self.device_id = device_id
        self.publish_date = str(time.time())

class User_star(Base):
    __tablename__ = 'user_star'
    
    id = Column('user_star_id', Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer)
    star_id = Column(Integer)
    apple_uid = Column(VARCHAR(32))
    publish_date = Column(VARCHAR(20))

    def __init__(self, user_id, apple_uid=apple_uid, star_id=None):
        self.user_id = user_id
        self.star_id = star_id
        self.apple_uid = apple_uid
        self.publish_date = str(time.time())

class User_sku(Base):
    __tablename__ = 'user_sku'

    id = Column('user_sku_id', Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer)
    sku_id = Column(Integer)
    source = Column(VARCHAR(64))
    source_id = Column(VARCHAR(64))
    apple_uid = Column(VARCHAR(32))
    publish_date = Column(VARCHAR(20))

    def __init__(self, user_id, sku_id, source='', source_id='', apple_uid=''):
        self.user_id = user_id
        self.sku_id = sku_id
        self.source = source
        self.source_id = source_id
        self.apple_uid = apple_uid
        self.publish_date = str(time.time())


def star_collect_count(cursor):
    _count = DBSession.query(func.count(Star_collection.id)).filter(Star_collection.id > cursor).first()
    if _count:
        return _count[0]
    return 0

def sku_collect_count(cursor):
    _count = DBSession.query(func.count(Sku_collection.id)).filter(Sku_collection.id > cursor).first()
    if _count:
        return _count[0]
    return 0

def star_collect_anonymous_count(cursor):
    _count = DBSession.query(func.count(User_star.id)).filter(User_star.user_id == -1).filter(User_star.id > cursor).first()
    if _count:
        return _count[0]
    return 0

def sku_collect_anonymous_count(cursor):
    _count = DBSession.query(func.count(User_sku.id)).filter(User_sku.user_id == -1).filter(User_sku.id > cursor).first()
    if _count:
        return _count[0]
    return 0

def star_collect_list(limit=10000, cursor=0):
    _list = DBSession.query(Star_collection).filter(Star_collection.id > cursor).limit(limit).all()
    return _list

def sku_collect_list(limit=10000, cursor=0):
    _list = DBSession.query(Sku_collection).filter(Sku_collection.id > cursor).limit(limit).all()
    return _list

def star_collect_anonymous_list(limit=10000, cursor=0):
    _list = DBSession.query(User_star).filter(User_star.user_id == -1).filter(User_star.id > cursor).limit(limit).all()
    return _list

def sku_collect_anonymous_list(limit=10000, cursor=0):
    _list = DBSession.query(User_sku).filter(User_sku.user_id == -1).filter(User_sku.id > cursor).limit(limit).all()
    return _list


countDict = {
    "star": star_collect_count,
    "sku": sku_collect_count,
    "star_anonymous": star_collect_anonymous_count,
    "sku_anonymous": sku_collect_anonymous_count,
}

listDict = {
    "star": star_collect_list,
    "sku": sku_collect_list,
    "star_anonymous": star_collect_anonymous_list,
    "sku_anonymous": sku_collect_anonymous_list,
}

def collect_new(type, cursor_key, item_list):
    print 'collect_new .......'
    key = COLLECT_KEY_BY_TYPE[type]
    try:
        p = redis.pipeline(transaction=False)
        print 'connect redis'
        for i in item_list:
            type_id = getattr(i, '%s_id'%type)
            user_id = i.user_id
            publish_date = i.publish_date

            print  'user_id:%s'%user_id, '%s_id:%s'%(type,type_id)
            p.zadd(key['user_id']%user_id, publish_date, type_id)
            p.zadd(key['item_id']%type_id, publish_date, user_id)
            p.hincrby(key['count'], type_id, 1)
            p.set(cursor_key, i.id)
        p.execute()
    except Exception, ex:
        print ex
        return 0
    return 1


def translate_collect(type, type_key, cursor_key):
    print 'start %s'%type
    collect = Collect(type)
    LIMIT=10000
    offset = 0 
    cursor = redis.get(cursor_key) 
    print cursor
    if not cursor:
        cursor = 0
    count = countDict[type_key](cursor)
    while True:
        cursor = redis.get(cursor_key) 
        if not cursor:
             cursor = 0
        print cursor, cursor_key, './*'*20
        collect_new(type, cursor_key, listDict[type_key](LIMIT, cursor))
        if  offset >= count:
            break
        offset = offset + LIMIT

def main():
    translate_collect('star', 'star', 'collectionStarCursor')
    translate_collect('star', 'star_anonymous', 'collectionStarAnonymousCursor')
    translate_collect('sku', 'sku', 'collectionSkuCursor')
    translate_collect('sku', 'sku_anonymous','collectionSkuAnonymousCursor')

if __name__ == "__main__":
    main()
