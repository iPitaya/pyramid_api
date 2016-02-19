#!/usr/bin/env python
# encoding: utf-8
from icehole_client.coflex_agent_client import CoflexAgentClient
from hichao.cache.cache import deco_cache
from hichao.util.date_util import HOUR, DAY, MINUTE
from hichao.util.statsd_client import timeit
timer = timeit('hichao_backend.m_search_skus')

SORT_DICT = {'promotion_price': 'current_price', 'sales': 'sales', 'on_sale_time': 'publish_date'}
REGION_DICT = ['欧美', '日韩', '国内', '设计师']


@timer
@deco_cache(prefix='search_skus', recycle=MINUTE)
def search_skus(query, gender=2, offset=0, limit=30,
                sort='all', asc_desc='desc',
                category='all', include_source=False, need_total=False):
    '''            
    if sort == 'all':
        sorts = '_score:desc,weight:desc,date:desc'
    else:
        sorts = '{0}:{1}'.format(sort,asc_desc)
    result = CoflexAgentClient().search_sku(query, gender, offset, limit, need_total, sorts, category, include_source)
    '''
    # current_price sales publish_date
    if sort == 'all':
        # sorts = '_score:desc'
        sorts = 'rank:asc,_score:desc'  # V6.4.0 按搜索要求修改
    else:
        sort = SORT_DICT[sort]
        if sort != 'current_price':
            asc_desc = 'desc'
        sorts = '{0}:{1}'.format(sort, asc_desc)
    result = CoflexAgentClient().search_item(query=query, gender=gender, offset=offset, limit=limit, need_total=need_total, sorts=sorts, category=category, include_source=include_source)
    return result


@timer
@deco_cache(prefix='search_zone', recycle=MINUTE)
def search_zone(query, gender=2, offset=0, limit=30,
                sort='all', asc_desc='desc',
                category='all', include_source=False, need_total=False):
    '''            
    if sort == 'all':
        sorts = '_score:desc,weight:desc,date:desc'
    else:
        sorts = '{0}:{1}'.format(sort,asc_desc)
    result = CoflexAgentClient().search_sku(query, gender, offset, limit, need_total, sorts, category, include_source)
    '''
    # current_price sales publish_date
    if sort == 'all':
        sorts = '_score:desc'
    else:
        sort = SORT_DICT[sort]
        if sort != 'current_price':
            asc_desc = 'desc'
        sorts = '{0}:{1}'.format(sort, asc_desc)
    result = CoflexAgentClient().search_zone(zone=query, offset=offset, limit=limit, sorts=sorts, category=category)
    return result
