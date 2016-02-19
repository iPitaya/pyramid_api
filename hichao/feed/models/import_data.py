#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hichao.base.lib.redis import redis, redis_key
from hichao.feed.models.feed import feed_new, ACTIVITY_STATUS_DIGIT
from hichao.collect.models.collect import Collect, REDIS_STAR_COL_BY_USER_ID, REDIS_SKU_COL_BY_USER_ID
from hichao.collect.models.topic import REDIS_TOPIC_COL_BY_USER_ID, topic_collect_list_by_user_id
from hichao.collect.models.thread import REDIS_THREAD_COL_BY_USER_ID, thread_collect_list_by_user_id


def import_past_feed():
    # 按user_id 去导入数据
    # 大约668000个用户
    collect_star = Collect('star')
    collect_sku = Collect('sku')
    for user_id in xrange(0, 700000):
        # star
        star_id_list = collect_star.get_item_list_by_user(user_id, offset=0, limit=-1)
        for star_id, ts in star_id_list:
            feed_new( user_id, ACTIVITY_STATUS_DIGIT['star_collect'], star_id, ts)

        # sku
        sku_id_list = collect_sku.get_item_list_by_user(user_id, 0, - 1)
        for sku_id, ts in sku_id_list:
            feed_new( user_id, ACTIVITY_STATUS_DIGIT['sku_collect'], sku_id, ts)

        # topic
        topic_id_list = topic_collect_list_by_user_id(user_id, 0, - 1)
        for topic_id, ts in topic_id_list:
            feed_new( user_id, ACTIVITY_STATUS_DIGIT['topic_collect'], topic_id, ts)

        # thread
        thread_id_list = thread_collect_list_by_user_id(user_id, 0, - 1)
        for thread_id, ts in thread_id_list:
            feed_new( user_id, ACTIVITY_STATUS_DIGIT['thread_collect'], topic_id, ts)


if __name__ == "__main__":
    import_past_feed()
    pass
