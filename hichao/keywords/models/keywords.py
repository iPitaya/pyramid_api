# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        )
from hichao.keywords.models.db import (
        dbsession_generator,
        Base,
        )
from hichao.util.image_url import (
        build_keyword_image_url,
        )
from hichao.util import xpinyin
from hichao.base.models.base_component import BaseComponent
from hichao.cache.cache import deco_cache
from hichao.util.date_util import (
        DAY,
        )
from hichao.util.component_builder import build_component_search_words
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_keyword')

Pinyin = xpinyin.Pinyin()

class Keyword(Base, BaseComponent):
    __tablename__ = 'keyword'
    id = Column('keyword_id', INTEGER, primary_key = True, autoincrement = True)
    name = Column(VARCHAR(64))
    type = Column(INTEGER)                              # 1为star，3为热词
    url = Column(VARCHAR(256))
    star_count = Column(INTEGER)

    def __init__(self, name, type, url, star_count = 0):
        self.name = name
        self.type = type
        self.url = url
        self.star_count = star_count

    def to_ui_component(self):
        component = {}
        component['n'] = self.name

    def get_search_type(self):
        if self.type == 1:
            return 'searchStar'
        else:
            return 'searchWord'

    def get_first_word(self):
        return Pinyin.get_initials(self.name)

    def get_all_word(self):
        return Pinyin.get_pinyin(self.name)

    def get_first_initial(self):
        return self.get_first_word()[0]

    def get_component_pic_url(self):
        if not self.url: return ''
        return build_keyword_image_url(self.url)

    def get_component_name(self):
        return self.name

    def get_component_star_count(self):
        return str(self.star_count)

    def to_ui_action(self):
        lite_action = getattr(self, 'lite_action', 0)
        if lite_action: return self.to_lite_ui_action()
        action = {}
        action['actionType'] = self.get_search_type()
        action['query'] = self.name
        return action

    def to_lite_ui_action(self):
        action = {}
        action['actionType'] = 'query'
        action['type'] = 'star' if self.type == 1 else 'sku'
        action['query'] = self.name
        return action

    def get_search_info(self):
        info = {}
        info['type'] = self.get_search_type()
        info['n'] = self.get_component_name()
        info['fw'] = self.get_first_word()
        info['aw'] = self.get_all_word()
        info['c'] = self.get_component_star_count()
        info['pic'] = self.get_component_pic_url()
        return info

@timer
@deco_cache(prefix = 'keyword_list', recycle = DAY)
def get_keyword_list(_type, use_cache = True):
    '''
    如果传入的_type为'star'，则返回所有明星，如果不是'star'，则返回热词。
    '''
    tp = _type == 'star' and 1 or 3
    DBSession = dbsession_generator()
    keywords = DBSession.query(Keyword).filter(Keyword.type == tp).all()
    DBSession.close()
    return keywords

@timer
@deco_cache(prefix = 'hot_words', recycle = DAY)
def get_hot_words(_type, use_cache = True):
    '''
    _type: 要获取的热词类型，可以为‘star’或‘keywords’。
    '''
    keywords = get_keyword_list(_type)
    items = []
    for keyword in keywords:
        items.append(keyword.get_search_info())
    return items

@timer
def sort_keyword_list(word_list):
    dividers = []
    divider_list = {}
    for word in word_list:
        if word.get_component_star_count() == '0':
            continue
        fw = word.get_first_initial()[0]
        if fw < 'A' or fw > 'Z':
            fw = '#'
        if fw not in dividers:
            if fw == '#':
                dividers.insert(0, fw)
            else:
                dividers.append(fw)
            divider_list[fw] = []
        divider_list[fw].append(word)
        dividers.sort()
    return dividers, divider_list

@timer
@deco_cache(prefix = 'keyword_list_result', recycle = DAY)
def build_keyword_list(_type, lite_action, use_cache = True):
    stars = get_keyword_list(_type)
    dividers, divider_list = sort_keyword_list(stars)
    res_list = []
    for divider in dividers:
        item = {}
        item['title'] = divider
        item['divider'] = divider
        item['items'] = []
        words = divider_list[divider]
        words.sort(key = lambda w:w.get_component_name())
        for word in words:
            word.lite_action = lite_action
            item['items'].append(build_component_search_words(word))
        res_list.append(item)
    return res_list


