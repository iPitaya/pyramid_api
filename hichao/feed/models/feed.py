#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from hichao.base.lib.redis import redis, redis_key, redis_slave
from hichao.base.celery.db import celery
from hichao.feed.models.follow import Follow
from hichao.feed import ACTIVITY_STATUS_DIGIT

REDIS_NEWS_FEED = redis_key.NewsFeedByUserId('%s')
REDIS_MINE_NEWS_FEED = redis_key.MineNewsFeedByUserId('%s')

def _feed_new(key, to_uid, from_uid, aid, item_id, ts):
    key = key % to_uid
    redis.zadd(key, ts, '%s:%s:%s' % (from_uid, aid, item_id))

@celery.task
def feed_new(from_uid, aid, item_id, ts):
    _feed_new(REDIS_MINE_NEWS_FEED, from_uid, from_uid, aid, item_id, ts)
    _feed_new(REDIS_NEWS_FEED, from_uid, from_uid, aid, item_id, ts)
    follow = Follow(from_uid)
    followers = follow.followers()

    # 需要优化
    for follower_id in followers:
        _feed_new(REDIS_NEWS_FEED, follower_id, from_uid, aid, item_id, ts)

def _feed_rm(key, to_uid, from_uid, aid, item_id):
    key = key % to_uid
    return redis.zrem(key, '%s:%s:%s' % (from_uid, aid, item_id))

@celery.task
def feed_rm(from_uid, aid, item_id):
    _feed_rm(REDIS_MINE_NEWS_FEED, from_uid, from_uid, aid, item_id)
    _feed_rm(REDIS_NEWS_FEED, from_uid, from_uid, aid, item_id)
    follow = Follow(from_uid)
    followers = follow.followers()

    # 需要优化
    for follower_id in followers:
        _feed_rm(REDIS_NEWS_FEED, follower_id, from_uid, aid, item_id)

class NewsFeed(object):

    def mine(self, user_id, offset=0, limit=20):
        # 按索引和按score排序, 索引可嫩
        key = REDIS_MINE_NEWS_FEED % user_id
        return redis_slave.zrevrange(key, offset, offset+limit, withscores=True)
        #return redis_slave.zrangebyscore(key, offset, offset - limit, withscores=True)

    def activity_list(self, user_id, offset=0, limit=20):
        key = REDIS_NEWS_FEED % user_id
        return redis_slave.zrevrange(key, offset, offset+limit, withscores=True)
        #return redis_slave.zrangebyscore(key, offset, offset - limit, withscores=True)
        

    def merge(self):
        # uid:1000:followers
        # uid:1000:following
        # 取following_uid_list,
        # 取出对应的new_type feed merge 到目标用户的news_feed
        pass

    def aggregate(self):
        # pull
        pass


if __name__ == "__main__":
    newsfeed = NewsFeed()
    print newsfeed.mine(30000)
    pass
