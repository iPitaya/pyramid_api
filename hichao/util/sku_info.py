# -*- coding:utf-8 -*-
import requests
import json
import socket
from hichao.base.config import (
        ECSHOP_SKU_INFO,
        NATIONAL_FLAG_URL,
        SKU_ACTIVITY_URL,
        BUSINESS_ID_TO_COUNTRY_ID_URL,
        COUNTRY_NAME_IMG,
        )
from hichao.util.date_util import (
        HOUR,
        DAY,
        MINUTE,
        FIVE_MINUTES,
        WEEK,
        )
from hichao.cache.cache import deco_cache
from hichao.util.statsd_client import timeit
from hichao.util.image_url import build_nationalflag_image_url

#IP_DOMAIN = socket.gethostbyname(socket.gethostname())
IP_DOMAIN = "127.0.0.1"
QUERY_REFERER = 'api'
timer = timeit('hichao_backend.m_sku_info')

@timer
@deco_cache(prefix = 'sku_info_from_ecshop', recycle = MINUTE)
def get_sku_info_from_ecshop_by_source_ids(source_ids, use_cache = True):
    url = ECSHOP_SKU_INFO
    query_all = {}
    query = {}
    query['source_ids'] = str(source_ids)
    query['ip'] = IP_DOMAIN
    query['referer'] = QUERY_REFERER
    query_all['data'] = json.dumps(query)
    try:
        rt = requests.post(url,data=query_all,headers = {})
        result = json.loads(rt.text)
        result = result['data']
    except Exception, e:
        print e, 'get_sku_info_from_ecshop_by_source_ids'
        result = []
    return result

@timer
@deco_cache(prefix = 'sku_country_info', recycle = WEEK)
def get_sku_country_info(business_id, use_cache = True):
    ''' 获得国家信息 返回结果 {'country':'','flag':''}'''
    url = NATIONAL_FLAG_URL
    query_all = {}
    query = {}
    query['business_id'] = business_id
    query['ip'] = IP_DOMAIN
    query['referer'] = QUERY_REFERER
    query_all['data'] = json.dumps(query)
    try:
        rt = requests.post(url,data=query_all,headers = {})
        result = json.loads(rt.text)
        result = result['data']
        if result:
            result['flag'] = build_nationalflag_image_url(result['flag'])
        else:
            result = {'country':'','flag':''}
    except Exception, e:
        print e
        result = {'country':'','flag':''}
    return result

@timer
@deco_cache(prefix = 'sku_country_info_new', recycle = WEEK)
def get_sku_country_info_new(business_id, use_cache = True):
    ''' 获得国家信息 返回结果 {'country':'','flag':''}'''
    business_id = str(business_id)
    url = BUSINESS_ID_TO_COUNTRY_ID_URL
    query_all = {}
    query = {}
    query['business_ids'] = business_id
    query['ip'] = IP_DOMAIN
    query['referer'] = QUERY_REFERER
    query_all['data'] = json.dumps(query)
    result = {'country':'','flag':''}
    try:
        rt = requests.post(url,data=query_all,headers = {})
        result_data = json.loads(rt.text)
        result_data = result_data['data']
        if result_data:
            for item in result_data:
                if item['business_id'] == business_id:
                    country_id = item['id']
                    if COUNTRY_NAME_IMG.has_key(country_id):
                        result['flag'] = COUNTRY_NAME_IMG[country_id]['img_url']
                        result['country'] = COUNTRY_NAME_IMG[country_id]['title']
                        break
        else:
            result = {}
    except Exception, e:
        print e
        result = {}
    return result

@timer
@deco_cache(prefix = 'sku_activity_info', recycle = FIVE_MINUTES)
def get_sku_activity_info_by_goods_id(goods_id, use_cache = True):
    url = SKU_ACTIVITY_URL
    data = {}
    query = {}
    query['goods_id'] = str(goods_id)
    query['ip'] = IP_DOMAIN
    query['referer'] = QUERY_REFERER
    data['data'] = json.dumps(query)
    res = {}
    try:
        res = requests.post(url, data = data, headers = {})
        res = json.loads(res.text)
        if res: res = res['data']
    except Exception, ex:
        print ex
        pass
    return res

