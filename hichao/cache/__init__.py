# -*- coding:utf-8 -*-

import redis
from hichao.base.config import (
        REDIS_CACHE_CONFIG_LIST,
        USE_LOCAL_CACHE,
        LOCAL_CACHE_PORT,
        )

#redis = StrictRedis(**CACHE_CONFIG)
REDIS_CLIENTS = []
for CACHE_CONFIG in REDIS_CACHE_CONFIG_LIST:
    #pool = redis.ConnectionPool(**CACHE_CONFIG)
    #cache_client = redis.StrictRedis(connection_pool=pool)
    cache_client = redis.StrictRedis(**CACHE_CONFIG)
    REDIS_CLIENTS.append(cache_client)

def generate_redis_random():
    index = 0
    count = len(REDIS_CLIENTS)
    while True:
        yield REDIS_CLIENTS[index]
        index = index + 1
        if index == count:
            index = 0

REDIS_RANDOM_NUM = generate_redis_random().next

def get_cache_client():
    redis_client =  REDIS_RANDOM_NUM()
    return redis_client


