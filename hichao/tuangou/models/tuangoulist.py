# -*- coding:utf8 -*-

from icehole_client.tuangou_client import (
        get_buying_list,
        get_latest_starting_buying_id_list,
        get_buying_id_list,
        get_buying_num,
        get_buying_list_with_ids,
        get_latest_buying_publish_ts,
        )
from hichao.base.config import(
        FALL_PER_PAGE_NUM,
        )
from hichao.util.date_util import (
        MINUTE,
        FIVE_MINUTES,
        HOUR,
        DAY,
        )
from hichao.tuangou.models.tuangouinfo import (
        build_tuangou_by_tuangou_id,
        )
from hichao.cache.cache import deco_cache
from hichao.util.statsd_client import timeit
import time

latest_starting_count = 1

# 下边几个状态应该在中间件里写一个枚举。。先这样写吧。。
ALL = 0             # 全部
STARTING = 1        # 即将开始
STARTED = 2         # 正在抢购
CLOSED = 3          # 已经结束

timer = timeit('hichao_backend.m_tuangou_tuangoulist')

@timer
def get_buying_datablock_list(order_code=0, limit=FALL_PER_PAGE_NUM, offset=0):
    if order_code != ALL:
        ids = get_buying_id_list(order_code, limit, offset)
    else:
        #混合排序
        ids = get_buying_id_list_with_sorted_by_all(limit, offset)
    data = {}
    data['items'] = []
    for id in ids:
        temp = build_tuangou_by_tuangou_id(id, slide=False)
        if temp:
            if order_code == STARTING:
                if temp['component']['tuanState'] == u'正在抢购':
                    continue
            data['items'].append(temp)

    if len(ids) == FALL_PER_PAGE_NUM:
        data['flag'] = str(offset + FALL_PER_PAGE_NUM)
    data['lts'] = str(get_last_tuangou_publish_date())
    has_starting = 1 if get_buying_id_list(STARTING, limit = 1, offset = 0) else 0
    data['has_starting'] = str(has_starting)
    if order_code != 0:
        data['has_starting'] = "0"
    return data

@timer
def get_starting_buying_datablock_list(limit=FALL_PER_PAGE_NUM, offset=0):
    data = get_buying_datablock_list(STARTING, limit, offset)
    return data

@timer
def get_started_buying_datablock_list(limit=FALL_PER_PAGE_NUM, offset=0):
    data = get_buying_datablock_list(STARTED, limit, offset)
    return data

@timer
def get_ended_buying_datablock_list(limit=FALL_PER_PAGE_NUM, offset=0):
    data = get_buying_datablock_list(CLOSED, limit, offset)
    return data

@timer
def get_buying_id_list_with_sorted_by_all(limit, offset):
    ids = []
    if offset==0:
        started_ids = get_buying_id_list(STARTED, limit, 0) 
    else:
        started_ids = get_buying_id_list(STARTED, limit, offset) 
    ids.extend(started_ids)
    len_started = len(ids)
    if len_started == limit:
        return ids
    started_total_num = get_buying_num(STARTED) 
    now_ids_len = started_total_num
    if now_ids_len < offset:
        offset = offset - started_total_num
        end_ids = get_buying_id_list(CLOSED, limit, offset)
    else:
        limit = limit - len_started
        end_ids = get_buying_id_list(CLOSED, limit, 0)
    ids.extend(end_ids)
    return ids

@timer
@deco_cache(prefix = 'tuangou_last_ts', recycle = FIVE_MINUTES)
def get_last_tuangou_publish_date():
    return get_latest_buying_publish_ts()

