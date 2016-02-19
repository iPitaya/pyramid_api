#-*- coding:utf8 -*-

import functools
from count import (
        tuangou_attend_count,
        tuangou_sku_attend_count,
        )
from time import time
from hichao.util.statsd_client import timeit
from hichao.collect.models.fake import collect_count

timer = timeit('hichao_backend.m_tuangou_attendutil')

COUNT_FUNC_DICT={}
COUNT_FUNC_DICT['tuangou']=tuangou_attend_count
COUNT_FUNC_DICT['tuangou_sku']=tuangou_sku_attend_count
COUNT_FAKE_NUM = 1037

@timer
def build_attend_count():
    def _(func):
        @functools.wraps(func)
        def __(*args, **kw):
            obj = func(*args, **kw)
            if not obj:
                return obj
            servertime = int(time())
            start_time = int(obj['component']['startTime'])
            end_time = int(obj['component']['endTime'])
            state, expires = judge_state(servertime, start_time, end_time)
            type = obj['component']['type']
            if type=='tuangou_sku':
                tag = int(obj['component']['tag'])
                state = '已售完' if tag in [3, 4, 5] else state
            else:
                if kw['slide']==True and obj['component']['action']:
                    obj['component']['picUrl'] = obj['component']['action']['picUrl']
            counter = COUNT_FUNC_DICT[type]
            count = counter(int(obj['component']['id']))
            if type == 'tuangou_sku':
                count = collect_count(int(obj['component']['id']), count, obj['component']['publish_date']) + COUNT_FAKE_NUM
                del obj['component']['publish_date']
            else:
                count = collect_count(int(obj['component']['id']), count, start_time - 86400 * 5) + COUNT_FAKE_NUM
            obj['component']['peopleCount']=str(count)
            obj['component']['tuanState']=state
            obj['component']['expires']=str(expires)
            if obj['component']['action']:
                obj['component']['action']['peopleCount']=str(count)
                obj['component']['action']['tuanState']=state
                obj['component']['action']['expires']=str(expires)
            del obj['component']['startTime']
            del obj['component']['endTime']
            del obj['component']['type']
            return obj
        return __
    return _

@timer
def build_attend_count_lite():
    def _(func):
        @functools.wraps(func)
        def __(*args, **kw):
            obj = func(*args, **kw)
            if not obj:
                return obj
            servertime = int(time())
            start_time = int(obj['component']['startTime'])
            end_time = int(obj['component']['endTime'])
            state, expires = judge_state(servertime, start_time, end_time)
            type = obj['component']['type']
            if type=='tuangou_sku':
                tag = int(obj['component']['tag'])
                state = '已售完' if tag in [3, 4, 5,7] else state
            else:
                if kw['slide']==True:
                    obj['component']['picUrl'] = obj['component']['action']['picUrl']
            counter = COUNT_FUNC_DICT[type]
            counter = COUNT_FUNC_DICT['tuangou']
            count = counter(int(obj['component']['tuanId']))
            if type == 'tuangou_sku':
                count = collect_count(int(obj['component']['id']), count, obj['component']['publish_date']) + COUNT_FAKE_NUM
                del obj['component']['publish_date']
            else:
                count = collect_count(int(obj['component']['id']), count, start_time - 86400 * 5) + COUNT_FAKE_NUM
            obj['component']['peopleCount']=str(count)
            obj['component']['tuanState']=state
            obj['component']['expires']=str(expires)
            del obj['component']['startTime']
            del obj['component']['endTime']
            del obj['component']['type']
            return obj
        return __
    return _


@timer
def judge_state(servertime, start_time , end_time):
    STARTING_STATE='即将开始'
    STARTED_STATE='正在抢购'
    ENDED_STATE='已结束'

    if servertime < start_time:
        return STARTING_STATE, start_time - servertime
    elif servertime > end_time:
        return ENDED_STATE, end_time - servertime
    return STARTED_STATE, end_time - servertime
