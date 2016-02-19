# -*- coding:utf-8 -*-
"""
Edited by lenson 2013.08.21.
 Inorde to support 'category' in the topic list.
 changes:
 1. import realted count function named "topic_user_count";
 2. add mapping in the dictionary variable named "counters";
"""

from hichao.collect.models.star import star_collect_count
from hichao.collect.models.sku import sku_collect_count
from hichao.collect.models.topic import topic_user_count
from hichao.collect.models.thread import thread_user_count
from hichao.collect.models.theme import theme_collect_count

from hichao.base.config.ui_action_type import (
        STAR_DETAIL,
        SKU_DETAIL,
        TOPIC_DETAIL,
        THREAD_DETAIL,
        DETAIL,
        DETAIL_STAR,
        DETAIL_SKU,
        DETAIL_THREAD,
        DETAIL_THEME,
        )
from hichao.base.config.ui_component_type import (
        FALL_STAR_CELL,
        SKU_CELL,
        TOPIC_CELL,
        THREAD_CELL,
        SEARCH_TOPIC_CELL,
        )
import functools

star_collect_counter = star_collect_count
sku_collect_counter = sku_collect_count
topic_collect_counter = topic_user_count
thread_collect_counter = thread_user_count
theme_collect_counter = theme_collect_count

counters = {
        STAR_DETAIL:star_collect_counter,
        SKU_DETAIL:sku_collect_counter,
        FALL_STAR_CELL:star_collect_counter,
        SKU_CELL:sku_collect_counter,
        TOPIC_CELL:topic_collect_counter,
        TOPIC_DETAIL:topic_collect_counter,
        SEARCH_TOPIC_CELL:topic_collect_counter,
        THREAD_DETAIL:thread_collect_counter,
        THREAD_CELL:thread_collect_counter,
        DETAIL_THEME:theme_collect_counter,
        DETAIL_STAR:star_collect_counter,
        DETAIL_SKU:sku_collect_counter,
        DETAIL_THREAD:thread_collect_counter,
        DETAIL:None,
        }

def build_collection_count(more_actions = False):
    def _(func):
        @functools.wraps(func)
        def __(*args, **kw):
            _obj = func(*args, **kw)
            if not _obj: return _obj
            count = 0
            if more_actions:
                for action in _obj['component']['actions']:
                    if not action: continue
                    if action['actionType'] not in counters.keys():continue
                    _type = action['actionType']
                    if action['actionType'] == DETAIL:
                        _type = action['type']
                        if _type not in counters.keys(): continue
                    if action.has_key('unixtime'):
                        count = counters[_type](action['id'], action['unixtime'])
                    if not count or int(count) < 0: count = 0
                    action['collectionCount'] = str(count)
                    if action.has_key('unixtime'): del(action['unixtime'])
                    _obj['component']['collectionCount'] = str(count)
            else:
                action = _obj['component']['action']
                if action['actionType'] in counters.keys():
                    _type = action['type'] if action['actionType'] == DETAIL else action['actionType']
                    count = 0
                    if _obj['component'].has_key('unixtime'):
                        unixtime = action['unixtime'] if action.has_key('unixtime') else _obj['component']['unixtime']
                        count = counters[_type](action['id'], unixtime)
                    if action.has_key('unixtime'): del(action['unixtime'])
                    if not count or int(count) < 0: count = 0
                    _obj['component']['action']['collectionCount'] = str(count)
                    _obj['component']['collectionCount'] = str(count)
            if _obj['component'].has_key('unixtime'): del(_obj['component']['unixtime'])
            return _obj
        return __
    return _


def build_collection_count_detail(more_actions = False):
    def _(func):
        @functools.wraps(func)
        def __(*args, **kw):
            _obj = func(*args, **kw)
            if not _obj:
                return _obj
            _type = 'topic'
            count = 0
            if _obj.has_key('unixtime'):
                count = counters[_type](_obj['id'],_obj['unixtime'])
            if not count or int(count) < 0: count = 0
            _obj['collectionCount'] = str(count)
            if _obj.has_key('unixtime'): del(_obj['unixtime'])
            return _obj
        return __
    return _


