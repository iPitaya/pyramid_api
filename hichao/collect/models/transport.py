#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hichao.base.lib.redis import redis, redis_key
from hichao.collect.models.collect import COLLECT_KEY_BY_TYPE    #, collect_star_new
from hichao.collect.models.thread import thread_collect_user_list_by_thread_id

def collect_thread_to_star(thread_id, star_id):
    _list = thread_collect_user_list_by_thread_id(thread_id, offset=0, limit= -1)
    key = COLLECT_KEY_BY_TYPE['star']
    with redis.pipeline(transaction=False) as p:
        try:
            for i in _list: 
                p.zadd(key['user_id']%i[0], i[1], star_id)
                p.zadd(key['item_id']%star_id, i[1], i[0])
                p.hincrby(key['count'], star_id, 1)
                #collect_star_new.delay(i[0], star_id, i[1])
            p.execute()
        except Exception, ex:
            print Exception, ex
            return 0
        return 1

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

