# -*- coding: utf-8 -*-
import math
from time import time
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, Text, String, VARCHAR
from hichao.base.lib.redis import redis, redis_key, redis_slave
from hichao.base.celery.db import celery
from hichao.collect.models.db import Base, sync_dbsession_generator
from hichao.collect.models.fake import collect_count
from hichao.feed.models.feed import ACTIVITY_STATUS_DIGIT, feed_new, feed_rm
from hichao.points.models.points import point_change
import transaction

REDIS_SKU_COL_USER_BY_SKU_ID =  redis_key.SkuCollectUserBySku('%s') 
REDIS_SKU_COL_BY_USER_ID = redis_key.SkuCollectByUser('%s') 
REDIS_SKU_COL_COUNT = redis_key.SkuCollectCount() 

REDIS_STAR_COL_BY_USER_ID = redis_key.StarCollectByUser('%s')
REDIS_STAR_COL_USER_BY_STAR_ID = redis_key.StarCollectUserByStar('%s') 
REDIS_STAR_COL_COUNT = redis_key.StarCollectCount() 



REDIS_STAR_PUBLISH_DAYS = redis_key.StarPublishDays() 
REDIS_STAR_PUBLISH_HOURS = redis_key.StarPublishHours() 

REDIS_STAR_TOP_N = redis_key.StarTopN() 

COLLECT_KEY_BY_TYPE = dict()

COLLECT_KEY_BY_TYPE['sku'] = dict(
    user_id = REDIS_SKU_COL_BY_USER_ID,
    item_id = REDIS_SKU_COL_USER_BY_SKU_ID,
    count = REDIS_SKU_COL_COUNT,
    )

COLLECT_KEY_BY_TYPE['star'] = dict(
    user_id = REDIS_STAR_COL_BY_USER_ID,
    item_id= REDIS_STAR_COL_USER_BY_STAR_ID,
    count = REDIS_STAR_COL_COUNT,
    )



class Collect(object):

    def __init__(self, type):
        self.type = type 
        self.key = COLLECT_KEY_BY_TYPE[type]

    def new(self, user_id, item_list):

        _time = int(time())
        try:
            p = redis.pipeline(transaction=False)
            for id in item_list:
                p.zadd(self.key['user_id']%user_id, _time, id)
                p.zadd(self.key['item_id']%id, _time, user_id)
                p.hincrby(self.key['count'], id, 1)
                #已经不做mysql同步了, 注释之
                #if self.type == 'star':
                #    collect_star_new.delay(user_id, id, _time)
                #elif self.type == 'sku':
                #    collect_sku_new.delay(user_id, id, _time)
                if self.type == 'star':
                    point_change.delay(user_id, "star_collect", id,  _time)
                elif self.type == 'sku':
                    point_change.delay(user_id, "sku_collect", id,  _time)
            p.execute()
        except:
            return 0
        #for item_id in item_list:
        #    feed_new.delay(user_id, ACTIVITY_STATUS_DIGIT['%s_collect'%self.type] , item_id, _time)
        return 1

    def new_by_time(self, user_id, item_list):
        # item_list = [(id, ts), (id, ts)]

        try:
            p = redis.pipeline(transaction=False)
            for id, ts in item_list:
                p.zadd(self.key['user_id']%user_id, ts, id)
                p.zadd(self.key['item_id']%id, ts, user_id)
                p.hincrby(self.key['count'], id, 1)
                #已经不做mysql同步了, 注释之
                #if self.type == 'star':
                #    collect_star_new.delay(user_id, id, ts)
                #elif self.type == 'sku':
                #    collect_sku_new.delay(user_id, id, ts)
            p.execute()
        except:
            return 0
        return 1

    def rm(self, user_id, item_id):
        _time = int(time())
        if self.type == 'star':
            #collect_star_rm.delay(user_id, item_id)
            point_change.delay(user_id, "star_collect", item_id,  _time, method="rm")
        elif self.type == 'sku':
            #collect_sku_rm.delay(user_id, item_id)
            point_change.delay(user_id, "sku_collect", item_id,  _time, method="rm")
        r = redis.zrem(self.key['user_id']%user_id, item_id)
        feed_rm.delay(user_id, ACTIVITY_STATUS_DIGIT['%s_collect'%self.type] , item_id)
        return r

    def has_item(self, user_id, item_id):
        return redis_slave.zscore(self.key['user_id']%user_id, item_id)

    def get_item_list_by_user(self, user_id, offset=0, limit=18, reverse=0):
        key = self.key['user_id']%user_id
        if reverse ==0:
            _list = redis_slave.zrevrange(key, offset, offset+limit, withscores=True)
        else:
            _list = redis_slave.zrange(key, offset, offset+limit, withscores=True)
        return _list

    def get_user_list_by_item(self, item_id, offset=0, limit=18, reverse=0):
        key = self.key['item_id']%item_id
        if reverse == 0:
            _list = redis_slave.zrevrange(key, offset, offset+limit, withscores=True)
        else:
            _list = redis_slave.zrange(key, offset, offset+limit, withscores=True)
        return _list

    def item_count_by_user(self, user_id):
        return  redis_slave.zcard(self.key['user_id']%user_id)

    def user_count_by_item(self, item_id, ts=1):
        s =  redis_slave.hget(self.key['count'], item_id)
        return collect_count(item_id, s, ts) 

    #def user_count_by_item(self, item_id):
    #    return  redis.zcard(self.key['item_id']%item_id)

    def user_count_by_item_list(self, item_list):
        return redis_slave.hmget(self.key['count'], item_list)

    def get_all_with_count(self):
        return redis_slave.hgetall(self.key['count'])

#collect = Collect('star')
#print collect.new(-1, [300838,])
#print collect.item_count_by_user(-1)

#class CollectStar(Base):
#
#    __tablename__ = 'collect_star'
#
#    id = Column(Integer, primary_key = True)
#    user_id = Column(Integer)
#    star_id = Column(Integer)
#    time = Column(VARCHAR(20))
#
#
#class CollectSku(Base):
#
#    __tablename__ = 'collect_sku'
#
#    id = Column(Integer, primary_key = True)
#    user_id = Column(Integer)
#    sku_id = Column(Integer)
#    time = Column(VARCHAR(20))
#
#
#
#
#@celery.task
#def collect_star_new(user_id, star_id, time):
#    session = sync_dbsession_generator()
#    collect = CollectStar()
#    collect.user_id = user_id
#    collect.star_id = star_id
#    collect.time = time 
#    try:
#        session.add(collect)
#        transaction.commit()
#    except Exception, ex:
#        transaction.abort()
#        print Exception, ex
#    finally:
#        session.close()
#
#@celery.task
#def collect_star_rm(user_id, star_id):
#    session = sync_dbsession_generator()
#    try:
#        session.query(CollectStar).filter(CollectStar.user_id==user_id, CollectStar.star_id==star_id).delete()
#        transaction.commit()
#    except Exception, ex:
#        transaction.abort()
#        print Exception, ex
#    finally:
#        session.close()
#
#@celery.task
#def collect_sku_new(user_id, sku_id, time):
#    session = sync_dbsession_generator()
#    collect = CollectSku()
#    collect.user_id = user_id
#    collect.sku_id = sku_id
#    collect.time = time 
#    try:
#        session.add(collect)
#        transaction.commit()
#    except Exception, ex:
#        transaction.abort()
#        print Exception, ex
#    finally:
#        session.close()
#
#@celery.task
#def collect_sku_rm(user_id, sku_id):
#    session = sync_dbsession_generator()
#    try:
#        session.query(CollectSku).filter(CollectSku.user_id==user_id, CollectSku.sku_id==sku_id).delete()
#        transaction.commit()
#    except Exception, ex:
#        transaction.abort()
#        print Exception, ex
#    finally:
#        session.close()



if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')


