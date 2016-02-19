# -*- coding:utf-8 -*-

from hichao.cache import get_cache_client

import functools
import cPickle
import time

cache_client = get_cache_client()

def get_send_mobile_num(mobile):
    value = cache_client.get(mobile)
    if value:
        value = cPickle.loads(value)
    return value

def set_send_mobile_num_and_time(mobile, recycle = 2*60):
    value = cache_client.get(mobile)
    result = ''
    if not value:
        result = cache_client.setex(mobile, recycle, cPickle.dumps(4))
    return result
