#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from hichao.base.lib.redis import redis, redis_key, redis_slave

REDIS_USER_FOLLOWING = redis_key.UserFollowing("%s")
REDIS_USER_FOLLOWERS = redis_key.UserFollowers("%s")

class Follow(object):

    def __init__(self, user_id):
        self.current_user_id = user_id
        self.user_following_key = REDIS_USER_FOLLOWING
        self.user_followers_key = REDIS_USER_FOLLOWERS

    def follow(self, user_id):
        create_at = time.time()

        m = redis.zadd(self.user_following_key% self.current_user_id, create_at, user_id)
        n = redis.zadd(self.user_followers_key% user_id, create_at, self.current_user_id) 
        #with redis.pipeline(transaction=False) as p:
        #    p.zadd(self.user_following_key% self.current_user_id, create_at, user_id)
        #    p.zadd(self.user_followers_key% user_id, create_at, self.current_user_id) 
        #m, n = p.execute()
        if m and n:
            return  True
        return False

    def unfollow(self, user_id):
        #need test
        m = redis.zrem(self.user_following_key% self.current_user_id, user_id)
        n = redis.zrem(self.user_followers_key% user_id, self.current_user_id)
        #with redis.pipeline(transaction=False) as p:
        #    p.zrem(self.user_following_key% self.current_user_id, user_id)
        #    p.zrem(self.user_followers_key% user_id, self.current_user_id)
        #m, n = p.execute()
        if m and n:
            return  True
        return False

    def following(self, offset, limit):
        """ users that self.current_user_id following """
        return redis_slave.zrevrange(self.user_following_key% self.current_user_id, offset, offset+limit)

    def followers(self, offset, limit):
        """ users that self.current_user_id's  followers """
        return redis_slave.zrevrange(self.user_followers_key% self.current_user_id, offset, offset+limit) 

    def following_stats(self):
        return redis_slave.zcard(self.user_following_key% self.current_user_id)

    def followers_stats(self):
        return redis_slave.zcard(self.user_followers_key% self.current_user_id)

    def has_follow(self, user_id):
        return redis_slave.zscore(self.user_following_key% self.current_user_id, user_id)

if __name__ == "__main__":
    pass
