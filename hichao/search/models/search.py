# -*- coding:utf-8 -*-
from icehole_client.search_manage_client import SearchManageClient
from hichao.util.image_url  import (
        build_category_and_brand_image_url,
        build_search_keywords_image_url,
        )
from hichao.collect.models.brand import (
        brand_collect_user_has_item,
        brand_count_by_user_id,
        brand_collect_count,
        )
from hichao.search.es import sg_tags
from hichao.util.object_builder import (
        build_item_component_by_sku_id,
        build_brand_action_by_brand_id,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import HOUR, DAY, MINUTE, FIVE_MINUTES
from hichao.util.statsd_client import timeit
from hichao.util.component_builder import build_component_search_sku_lite
import time
timer = timeit('hichao_backend.m_search_skus')

SUGGEST_TAG_COUNT = 10

@timer
def build_key_word( key_word, user_id, use_cache = True):
    concerns = {}
    concerns['background'] = build_search_keywords_image_url(key_word.get_background_image())
    concerns['picUrl'] = build_search_keywords_image_url(key_word.get_image())
    concerns['follow'] = str(key_word.get_focus_count())
    concerns['text'] = key_word.get_name()
    concerns['description'] = key_word.get_description()
    concerns['id'] = str(key_word.get_tag_id())
    brand_id = key_word.get_brand_id()
    if brand_id > 0:
        res = brand_collect_user_has_item(int(user_id), int(brand_id))
        brand_total = brand_collect_count(int(brand_id), 0)
        concerns['follow'] = str(brand_total)
    else:
        client = SearchManageClient()
        res = client.judge_user_follow_tag(int(user_id), int(key_word.get_tag_id()))
    if res: concerns['focused'] = '1'
    else: concerns['focused'] = '0'
    return concerns

@timer
@deco_cache(prefix = 'get_item_component_data', recycle = MINUTE)
def get_item_component_data(sku_id, lite_action, cps_type, support_webp, support_ec, support_xiajia, has_color = False, sku_item = {}, use_cache = True):
        sku_id = sku_item['sku_id']
        com = build_item_component_by_sku_id(sku_id,0,lite_action,cps_type,support_webp,support_ec,support_xiajia, has_color)
        if com:
            #com['component']['sales'] = str(sku_item['sales'])
            #com['component']['price'] = str(sku_item['current_price'])
            com['component']['trackValue'] = 'item_sku_' + str(sku_id)
            if com['component'].has_key('action'):
                com['component']['action']['trackValue'] = com['component']['trackValue']
            elif com['component'].has_key('actions'):
                com['component']['actions'][0]['trackValue'] = com['component']['trackValue']
        return com

@timer
@deco_cache(prefix = 'get_item_component_data_lite', recycle = FIVE_MINUTES)
def get_item_component_data_lite(sku_id, has_color=False, sku_item = {}, use_cache = True):
        com = build_component_search_sku_lite(sku_item)
        return com

@timer
def get_special_keywords(query,user_id,count = SUGGEST_TAG_COUNT):
    data = {}
    client = SearchManageClient()
    key_word = client.get_special_word(query.encode('utf-8'))
    if key_word:
        data['concerns'] = build_key_word(key_word, user_id)
        brand_id = key_word.get_brand_id()
        if brand_id > 0:
            action = {}
            action = build_brand_action_by_brand_id(brand_id)
            if action:
                data['concerns']['action'] = action
    else:
        tags = sg_tags(query, count)
        data['tags'] = []
        for tag in tags:
            obj = {}
            obj['text'] = tag['name']
            obj['color'] = tag['background']
            obj['picUrl'] = tag['img_url']
            data['tags'].append(obj)
    return data
