#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from hichao.base.lib.redis import redis, redis_key
from hichao.collect.models.collect import REDIS_SKU_COL_BY_USER_ID, Collect
from hichao.collect.models.topic import topic_collect_list_by_user_id
from hichao.collect.models.thread import thread_collect_list_by_user_id


#将数据导入mysql



#num = 0
#for user_id in xrange(0, 900000):
#    star_list = topic_collect_list_by_user_id(user_id, 0, -1)
#    if star_list:
#        num += len(star_list)
#
#print num








if __name__ == "__main__":
    pass

