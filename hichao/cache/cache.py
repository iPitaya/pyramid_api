# -*- coding:utf-8 -*-

from hichao.cache import (
    get_cache_client,
)
from hichao.base.config import (
    USE_LOCAL_CACHE,
    LOCAL_CACHE_RECYCLE,
    LOCAL_CACHE_NAME,
    CACHE_PREFIX,
)
import functools
import cPickle
import time
import zlib

if USE_LOCAL_CACHE:
    import uwsgi

FAKE_VALUE = '##FAKE_VALUE##'
COMPRESS_LEVEL = 6

def delete_cache_by_args_key(*args, **kw):
    try:
        cache_client = get_cache_client()
        key = '{0}:{1}'.format(CACHE_PREFIX, '_'.join([str(i).replace(' ', '_') for i in args]))
        cache_client.delete(key)
    except Exception, e:
        print e

    
def delete_cache_by_key(key):
    try:
        cache_client = get_cache_client()
        key = CACHE_PREFIX + ':' + key
        cache_client.delete(key)
    except Exception, e:
        print e


def deco_cache(prefix, recycle=60):
    def func_packer(func):
        @functools.wraps(func)
        def checker(*args, **kw):
            cache_client = get_cache_client()
            key = '{0}:{1}_{2}'.format(CACHE_PREFIX, prefix, '_'.join([str(i).replace(' ', '_') for i in args]))
            value = None
            local_cached = 0
            use_cache = kw.get('use_cache', True)
            if use_cache:
                if USE_LOCAL_CACHE:
                    try:
                        value = uwsgi.cache_get(key)
                    except:
                        value = None
                    if value:
                        local_cached = 1
                if not local_cached:
                    try:
                        value = cache_client.get(key)
                        if USE_LOCAL_CACHE and value:
                            uwsgi.cache_set(key, value, LOCAL_CACHE_RECYCLE, LOCAL_CACHE_NAME)
                    except:
                        value = None
            if value:
                value = zlib.decompress(value)
                value = cPickle.loads(value)
                if value == FAKE_VALUE:
                    return None
            else:
                value = func(*args, **kw)
                try:
                    if value != None:
                        compressed_str = zlib.compress(cPickle.dumps(value), COMPRESS_LEVEL)
                        if recycle == 0:
                            cache_client.set(key, compressed_str)
                        else:
                            cache_client.setex(key, recycle, compressed_str)
                        if USE_LOCAL_CACHE:
                            uwsgi.cache_set(key, compressed_str, LOCAL_CACHE_RECYCLE, LOCAL_CACHE_NAME)
                    else:
                        compressed_str = zlib.compress(cPickle.dumps(FAKE_VALUE), COMPRESS_LEVEL)
                        cache_client.setex(key, 20, compressed_str)
                        if USE_LOCAL_CACHE:
                            uwsgi.cache_set(key, compressed_str, LOCAL_CACHE_RECYCLE, LOCAL_CACHE_NAME)
                except:
                    pass
            return value
        return checker
    return func_packer


def deco_cache_static_prefix(prefix, recycle=60):
    def func_packer(func):
        @functools.wraps(func)
        def checker(*args, **kw):
            cache_client = get_cache_client()
            key = prefix
            value = None
            local_cached = 0
            use_cache = kw.get('use_cache', True)
            if use_cache:
                if USE_LOCAL_CACHE:
                    try:
                        value = uwsgi.cache_get(key)
                    except:
                        value = None
                    if value:
                        local_cached = 1
                if not local_cached:
                    try:
                        value = cache_client.get(key)
                        if USE_LOCAL_CACHE and value:
                            uwsgi.cache_set(key, value, LOCAL_CACHE_RECYCLE, LOCAL_CACHE_NAME)
                    except:
                        value = None
            if value:
                value = zlib.decompress(value)
                value = cPickle.loads(value)
                if value == FAKE_VALUE:
                    return None
            else:
                value = func(*args, **kw)
                try:
                    if value != None:
                        compressed_str = zlib.compress(cPickle.dumps(value), COMPRESS_LEVEL)
                        if recycle == 0:
                            cache_client.set(key, compressed_str)
                        else:
                            cache_client.setex(key, recycle, compressed_str)
                        if USE_LOCAL_CACHE:
                            uwsgi.cache_set(key, compressed_str, LOCAL_CACHE_RECYCLE, LOCAL_CACHE_NAME)
                    else:
                        compressed_str = zlib.compress(cPickle.dumps(FAKE_VALUE), COMPRESS_LEVEL)
                        cache_client.setex(key, 20, compressed_str)
                        if USE_LOCAL_CACHE:
                            uwsgi.cache_set(key, compressed_str, LOCAL_CACHE_RECYCLE, LOCAL_CACHE_NAME)
                except:
                    pass
            return value
        return checker
    return func_packer


def deco_cache_m(prefix, recycle=60):
    """
    批量获取缓存,只支持单层列表，如[1,2,3,4,5],未使用本地缓存
    :param prefix:缓存前缀
    :param recycle:要缓存的时长,以秒为单位
    :return:要获取的列表数据,没获取到的返回None
    """
    def func_packer(func):
        @functools.wraps(func)
        def _(li, **kw):
            if not li:
                return []
            keys = ['{0}_{1}_{2}'.format(CACHE_PREFIX, prefix, str(item)) for item in li]
            cache_client = get_cache_client()
            uncached_item = []
            res_items = {}
            use_cache = kw.get('use_cache', True)
            if use_cache:
                values = cache_client.mget(keys)
                res_items = dict(zip(li, values))
                for item in li:
                    value = res_items[item]
                    if not value:
                        uncached_item.append(item)
                    else:
                        value = zlib.decompress(value)
                        value = cPickle.loads(value)
                        if value == FAKE_VALUE:
                            value = None
                        res_items[item] = value
            else:
                uncached_item = li
            if uncached_item:
                recache_item = func(uncached_item, **kw)
                res = {}
                for k in recache_item.keys():
                    res[str(k)] = recache_item[k]
                for item in uncached_item:
                    v = res.get(str(item), None)
                    res_items[item] = v
                    key = '{0}_{1}_{2}'.format(CACHE_PREFIX, prefix, item)
                    if v is not None:
                        compressed_str = zlib.compress(cPickle.dumps(v), COMPRESS_LEVEL)
                        if recycle == 0:
                            cache_client.set(key, compressed_str)
                        else:
                            cache_client.setex(key, recycle, compressed_str)
                    else:
                        compressed_str = zlib.compress(cPickle.dumps(FAKE_VALUE), COMPRESS_LEVEL)
                        cache_client.setex(key, 20, compressed_str)
            return [res_items[item] for item in li]

        return _

    return func_packer

