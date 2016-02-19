# -*- coding:utf-8 -*-

from sqlalchemy import (
    Column,
    INTEGER,
    VARCHAR,
    TEXT,
    func,
)
from hichao.keywords.models.db import (
    rup_down_dbsession_generator,
    UP_Base,
)
from hichao.base.models.base_component import BaseComponent
from hichao.util.image_url import (
    build_search_star_list_image_url,
    build_category_and_brand_image_url,
)
from hichao.cache.cache import deco_cache
from hichao.util.date_util import FIVE_MINUTES
from hichao.util.statsd_client import timeit
from icehole_client.brand_client import BrandClient

timer = timeit('hichao_backend.m_keyword_hotwords')


class HotWords(UP_Base, BaseComponent):
    __tablename__ = 'updown'
    id = Column(INTEGER, primary_key=True)
    value = Column(TEXT, nullable=False)


class Querys(UP_Base, BaseComponent):
    __tablename__ = 'updown_all'
    id = Column(INTEGER, primary_key=True)
    tab = Column(VARCHAR(128), nullable=False)
    value = Column(TEXT, nullable=False)


@timer
def get_hot_words():
    DBSession = rup_down_dbsession_generator()
    hot_words = DBSession.query(HotWords).order_by(HotWords.id.desc()).first()
    DBSession.close()
    hot_words = eval(hot_words.value)
    for words in hot_words:
        for word in words['items']:
            rebuild_hot_word(word)
    return hot_words


@timer
def rebuild_hot_word(hot_word):
    hot_word['component']['picUrl'] = build_search_star_list_image_url(hot_word['component']['picUrl'])


@timer
@deco_cache(prefix='querys', recycle=FIVE_MINUTES)
def get_last_querys_id_by_type(_type, use_cache=True):
    DBSession = rup_down_dbsession_generator()
    last_id = DBSession.query(func.max(Querys.id)).filter(Querys.tab == _type).first()
    DBSession.close()
    return last_id and last_id[0] or 0


@timer
@deco_cache(prefix='last_querys_object', recycle=FIVE_MINUTES)
def get_last_querys_by_type(_type, use_cache=True):
    DBSession = rup_down_dbsession_generator()
    last_query = DBSession.query(Querys).filter(Querys.tab == _type).order_by(Querys.id.desc()).first()
    DBSession.close()
    return last_query


@timer
@deco_cache(prefix='querys_value', recycle=FIVE_MINUTES)
def get_querys_by_id(query_id, use_cache=True):
    DBSession = rup_down_dbsession_generator()
    querys = DBSession.query(Querys.value).filter(Querys.id == query_id).first()
    DBSession.close()
    return querys and querys[0] or ''


@timer
def rebuild_hot_querys(query_item):
    com = {}
    com['query'] = query_item['query']
    com['picUrl'] = build_search_star_list_image_url(query_item['src'])
    com['title'] = query_item['title']
    return com


@timer
def rebuild_item_categorys(query_item):
    items = {}
    title = query_item['title']
    items['title'] = title
    items['cateimg'] = build_search_star_list_image_url(query_item['cateimg'])
    items['items'] = []
    for item in query_item['items']:
        _item = {}
        com = {}
        action = {}
        com['componentType'] = 'search'
        com['word'] = item['title']
        com['picUrl'] = build_search_star_list_image_url(item['src'])
        action['title'] = item['title']
        action['query'] = title + ',' + item['query']
        action['actionType'] = 'searchWord'
        com['action'] = action
        _item['component'] = com
        items['items'].append(_item)
    return items


@timer
def rebuild_item_shop(query_item, comType, is_en=0, action_type=None):
    items = {}
    items['items'] = []
    if is_en == 0:
        title = query_item['title']
        items['title'] = title
        items['cateimg'] = build_category_and_brand_image_url(query_item['cateimg'])
        query_items = query_item['items']
    else:
        query_items = query_item
    for item in query_items:
        _item = {}
        com = {}
        action = {}
        com['componentType'] = comType
        com['word'] = item['title']
        com['picUrl'] = build_category_and_brand_image_url(item['src'])
        action['title'] = item['title']
        if is_en:
            com['id'] = item['id']
            com['en_title'] = item['en_title']
            action['en_title'] = item['en_title']
            if item['query']:
                action['query'] = item['query']
            else:
                action['query'] = item['title']
            action['id'] = item['id']
        else:
            action['query'] = item['title'] + ',' + item['query']
        if is_en:
            action['actionType'] = 'ecshopSearch'
        else:
            action['actionType'] = 'searchWord'

        if action_type:
            action['actionType'] = action_type

        com['action'] = action
        _item['component'] = com
        items['items'].append(_item)
    return items


@timer
def build_component_category_brand(query_item, comType, count, is_en=0, category=''):
    '''
    is_en为0 对hi版商城第一版支持不含en_title 1是商城首页分类个数不做限制其他有个数限制  2是商城新版首页精品大牌
    '''
    items = []
    for i, item in enumerate(query_item):
        _item = {}
        com = {}
        action = {}
        com['componentType'] = comType
        if comType == 'shopCategoryCell':
            com['word'] = item['title']
        com['picUrl'] = build_category_and_brand_image_url(item['src'])
        action['title'] = item['title']
        if is_en:
            action['id'] = item['id']
            action['en_title'] = item['en_title']
            com['id'] = item['id']
            com['en_title'] = item['en_title']
            com['title'] = item['title']
        if is_en == 1:
            if item['query']:
                action['query'] = item['query']
            else:
                action['query'] = item['title']
        else:
            if item['query']:
                action['query'] = item['query']
            else:
                action['query'] = item['title']
        if is_en == 2 or (is_en == 1 and comType == 'cell'):
            action['actionType'] = 'ecshopSearch'
        else:
            action['actionType'] = 'searchWord'
        com['action'] = action
        _item['component'] = com
        items.append(_item)
        if is_en == 1:
            continue
        if i >= count - 1:
            break
    return items


@timer
def build_component_brand(query_item, comType, actionType='ecshopSearch'):
    '''
    品牌数据 new
    '''
    items = []
    for item in query_item:
        _item = {}
        com = {}
        action = {}
        com['componentType'] = comType
        com['title'] = item['title']
        com['picUrl'] = build_category_and_brand_image_url(item['src'])
        action['title'] = item['title']
        action['id'] = item['id']
        action['en_title'] = item['en_title']
        com['id'] = item['id']
        com['en_title'] = item['en_title']
        com['title'] = item['title']
        if item['query']:
            action['query'] = item['query']
        else:
            action['query'] = item['title']
        action['actionType'] = actionType
        com['action'] = action
        _item['component'] = com
        items.append(_item)
    return items


@timer
def rebuild_item_count_shop(query_item, count, comType, is_en=0):
    items = {}
    title = query_item['title']
    items['title'] = title
    items['cateimg'] = build_category_and_brand_image_url(query_item['cateimg'])
    items['items'] = []
    if is_en:
        items['id'] = query_item['id']
    #is_en = 0
    # if comType == 'shopCategoryDetailCell':
    #    is_en = 1
    if is_en:
        brand_comType = 'cell'
        items['brands'] = build_component_category_brand(query_item['brands'], brand_comType, count, is_en, title)
    items['items'] = build_component_category_brand(query_item['items'], comType, count, is_en, title)

    return items


def rebuild_item_count_mall(query_item, count, comType, is_en=0):
    items = {}
    #title = query_item['title']
    #items['title'] = title
    #items['cateimg'] = build_search_star_list_image_url(query_item['cateimg'])
    items['items'] = []
    items['items'] = build_component_category_brand(query_item, comType, count, is_en=2)

    return items


def rebuild_item_catetory_one(querys, comType, actionType='selectcategory'):
    items = {}
    items['items'] = []
    # print querys
    for query_item in querys:
        com = {}
        action = {}
        _item = {}
        title = query_item['title']
        en_title = query_item['en_title']
        com['title'] = title
        com['picUrl'] = build_category_and_brand_image_url(query_item['cateimg'])
        com['en_title'] = en_title
        com['componentType'] = comType
        com['id'] = query_item['id']
        action['id'] = query_item['id']
        if query_item['query']:
            action['query'] = query_item['query']
        else:
            action['query'] = title
        action['title'] = title
        action['en_title'] = en_title
        action['actionType'] = actionType
        com['action'] = action
        _item['component'] = com
        items['items'].append(_item)
    return items


@timer
def rebuild_shop_dress_categorys(querys, is_en=0, query=-1):
    values = []
    if is_en == 0:
        item_count = 8
        querys = querys[0]
        comType = 'shopCategoryCell'
        values.append(rebuild_item_count_shop(querys, item_count, comType))
    else:
        if query < 1:
            return values
        item_count = 9
        #querys = get_items_by_title_name(querys,query)
        querys = get_items_by_id(querys, query)
        comType = 'hotCategoryCell'
        #is_en = 1
        if querys:
            values.append(rebuild_item_count_shop(querys, item_count, comType, is_en))
    return values


@timer
def rebuild_shop_categorys_all(querys):

    values = []
    for query in querys:
        big_category = {}
        a_item = rebuild_item_shop(query['items'], 'shopCategoryCell_v640', is_en=1, action_type='searchWord')
        a_item['cateimg'] = build_category_and_brand_image_url(query['cateimg'])
        a_item['componentType'] = 'shopBigCategoryCell_v640'
        a_item['title'] = query['title']
        a_item['en_title'] = query['en_title']
        action = {'query': query['title'], 'title': query['title'], 'en_title': query['en_title'], "actionType": "searchWord"}
        a_item['action'] = action
        big_category['component'] = a_item

        values.append(big_category)
    return values


@timer
def rebuild_shop_dress_categorys_more(querys):
    values = []
    if len(querys) > 2:
        querys = querys[1:-1]
    else:
        return values
    comType = 'CategoryListCell'
    for query in querys:
        # if query['title'] != u'最热' and query['title'] != u'品牌':
        values.append(rebuild_item_shop(query, comType))
    return values


@timer
def rebuild_shop_dress_categorys_one(querys, comType='hotCategoryCell', actionType='selectcategory'):
    #comType = 'hotCategoryCell'
    values = []
    values.append(rebuild_item_catetory_one(querys, comType, actionType))
    return values


@timer
def rebuild_shop_dress_brand(querys, is_en=0):
    values = []
    if is_en:
        comType = 'cell'
        item_count = 7
        values.append(rebuild_item_count_mall(querys, item_count, comType, is_en))
    else:
        comType = 'shopBrandCell'
        item_count = 6
        values.append(rebuild_item_count_shop(querys, item_count, comType))
    return values


@timer
def rebuild_shop_dress_brand_more(querys, is_en=0):
    values = []
    comType = 'BrandListCell'
    values.append(rebuild_item_shop(querys, comType, is_en))
    return values


@timer
def rebuild_designer_brand_more(querys, is_en=0, num=0):
    values = []
    comType = 'designerCell'
    values.append(rebuild_item_shop(querys, comType, is_en))
    if num > 0 and values[0]:
        values[0]['items'] = values[0]['items'][0:num]
    return values


def get_items_by_title_name(querys, title_name):
    for query in querys:
        if query['title'] == title_name:
            return query
    return {}


def get_items_by_id(querys, id):
    for query in querys:
        if query['id'] == id:
            return query
    return {}


def build_component_category_selection(query_item, comType='hotCategoryCell', actionType='searchWord'):
    ''' 分类 精选 component  '''
    ui = {}
    if query_item:
        com = {}
        action = {}
        title = query_item['title']
        en_title = query_item['en_title']
        com['title'] = title
        com['word'] = title
        if comType == 'hotCategoryCell':
            url_str = query_item['src']
        else:
            url_str = BrandClient().get_brand_logo_by_brand_id(int(query_item['id']))
        if not url_str:
            url_str = query_item['src']
        com['picUrl'] = build_category_and_brand_image_url(url_str)
        com['en_title'] = en_title
        com['componentType'] = comType
        com['id'] = query_item['id']
        action['id'] = query_item['id']
        if query_item['query']:
            action['query'] = query_item['query']
        else:
            action['query'] = title
        action['title'] = title
        action['en_title'] = en_title
        action['actionType'] = actionType
        com['action'] = action
        ui['component'] = com
    return ui


def get_category_selection_items(querys):
    ''' 获得 分类精选所有的数据  '''
    data = {}
    data['items'] = []
    data['brands'] = []
    data['masters'] = []
    for key in querys.keys():
        if key == 'masters':
            comType = 'designerCell'
            actionType = 'ecshopSearch'
        elif key == 'brands':
            comType = 'cell'
            actionType = 'ecshopSearch'
        else:
            comType = 'hotCategoryCell'
            actionType = 'searchWord'
        for item in querys[key]:
            data[key].append(build_component_category_selection(item, comType, actionType))
    return data
