# -*- coding: utf-8 -*-
from intstr import IntStr

redis_keyer = IntStr(
'!"#$&()+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ^_`abcdefghijklmnopqrstuvwxyz{|}~'
)

REDIS_KEY_ID = 'RedisKeyId'
REDIS_KEY = 'RedisKey'
REDIS_ID_KEY = 'RedisIdKey'

_EXIST = set()

class RedisKey(object):
    def __init__(self, redis):
        self.redis = redis

    def __getattr__(self, attr):
        def _(name=''):
            return self(attr, name)
        return _

    def __call__(self, attr, name=''):
        key = attr+name
        redis = self.redis

        if key in _EXIST:
            print 'REDIS KEY IS ALREADY DEFINED %s !!!'%key


        _EXIST.add(key)
        if redis:
            _key = redis.hget(REDIS_KEY, key)
            if _key is None:
                id = redis.incr(REDIS_KEY_ID)
                _key = redis_keyer.encode(id)
                if name and "%" in name:
                    _key = _key+"'"+name
                p = redis.pipeline(transaction=False)
                p.hset(REDIS_KEY, key, _key)
                p.hset(REDIS_ID_KEY, _key, key)
                p.execute()
            return _key



from redis import StrictRedis
from hichao.base.config import (
        REDIS_CONFIG,
        REDIS_SLAVE_CONFIG,
        DEVICE_REDIS_CONFIG,
        COLLECTION_REDIS_CONFIG,
        COLLECTION_REDIS_SLAVE_CONFIG,
        )

redis = StrictRedis(**COLLECTION_REDIS_CONFIG)
redis_key = RedisKey(redis)

redis_slave = StrictRedis(**COLLECTION_REDIS_SLAVE_CONFIG)
redis_slave_key = RedisKey(redis_slave)

#redis_device = StrictRedis(**DEVICE_REDIS_CONFIG)
#redis_device_key = RedisKey(redis_device)

redis_token = StrictRedis(**REDIS_CONFIG)
redis_token_key = RedisKey(redis_token)

redis_token_slave = StrictRedis(**REDIS_SLAVE_CONFIG)
redis_token_slave_key = RedisKey(redis_slave)

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

