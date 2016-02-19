# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        or_,
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
        MINUTE,
        )
from hichao.util.component_builder import (
        build_component_search_words,
        build_component_newsStar_list,
        )
from hichao.news.models.db import dbsession_generator
from hichao.keywords.models.keywords import sort_keyword_list
from hichao.util.statsd_client import timeit
from hichao.topic.models.topic import get_starspace_news_ids
import time
from hichao.base.config import FALL_PER_PAGE_NUM
from hichao.util.object_builder import (
        build_news_list_item_by_id,
        build_star_by_star_id,
        )
from hichao.search.es import search
from icehole_client.coflex_agent_client  import CoflexAgentClient 

timer = timeit('hichao_backend.m_news_star')

Pinyin = xpinyin.Pinyin()

class NewsStar(Base, BaseComponent):
    __tablename__ = 'special_words'
    id = Column('id', INTEGER, primary_key = True, autoincrement = True)
    name = Column('show_word',VARCHAR(1024))
    english_name = Column('synonymous',VARCHAR(1024))
    url = Column('avatar',VARCHAR(256))
    img_url = Column( VARCHAR(1024))
    review = Column(INTEGER)
    gender = Column(VARCHAR(16))
    job = Column(VARCHAR(255))
    constellation = Column(VARCHAR(16))
    news_count = Column(INTEGER)
    image_count = Column(INTEGER)

    def get_component_star_count(self):
        num = self.image_count
        return str(num)

    def get_component_news_count(self):
        num = self.news_count
        return str(num)

    def get_component_name(self):
        return self.name

    def get_component_english_name(self):
        return self.english_name

    def get_component_pic_url(self):
        return self.img_url

    def get_first_word(self):
        return Pinyin.get_initials(self.name)

    def get_first_initial(self):
        return self.get_first_word()[0]

    def to_ui_action(self):
        action = {}
        action['actionType'] = 'starSpace'
        action['id'] = str(self.id)
        return action 

    def get_news_star_info(self):
        info = {}
        info['id'] = str(self.id)
        info['gender'] = self.gender
        info['job'] = self.job
        info['constellation'] = self.constellation
        info['name'] = self.name
        info['avatar'] = self.img_url
        return info

@timer
@deco_cache(prefix = 'news_star_list', recycle = MINUTE)
def get_news_star_list():
    DBSession = dbsession_generator()
    star_items = DBSession.query(NewsStar).filter(or_(NewsStar.news_count > 0, NewsStar.image_count > 0)).all()
    DBSession.close()
    return star_items

@timer
@deco_cache(prefix = 'news_star_info_by_id', recycle = MINUTE)
def get_news_star_info_by_id(id):
    DBSession = dbsession_generator()
    star_item = DBSession.query(NewsStar).filter(NewsStar.id == int(id)).first()
    DBSession.close()
    return star_item

@timer
@deco_cache(prefix = 'newsStar_list', recycle = MINUTE)
def build_newsStar_list( use_cache = True):
    stars = get_news_star_list()
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
            item['items'].append(build_component_newsStar_list(word))
        res_list.append(item)
    return res_list

def get_starspace_news_list(star_user_id,flag):
    data = {}
    if not flag:
        flag = time.time()
        star_info = get_news_star_info_by_id(star_user_id)
        if star_info:
            data['head'] = star_info.get_news_star_info()
    news_ids = get_starspace_news_ids(flag, FALL_PER_PAGE_NUM, star_user_id)
    data['items'] = []
    for news_id in news_ids:
        com = build_news_list_item_by_id(news_id)
        flag = com['component']['flag']
        del(com['component']['flag'])
        if com:
            data['items'].append(com)
    if len(news_ids) >= FALL_PER_PAGE_NUM:
        data['flag'] = flag 
    return data

def get_starspace_star_list(star_user_id, flag, tp):
    data = {}
    items = []
    star_info = get_news_star_info_by_id(star_user_id)
    if not star_info:
        return data
    if not flag:
        flag = int(flag) if flag else 0
        if star_info:
            data['head'] = star_info.get_news_star_info()
    q = star_info.get_component_name()
    #item_ids = search(q, int(flag), FALL_PER_PAGE_NUM, tp)
    client = CoflexAgentClient()
    item_data = client.search_star_photo(q, 0, int(flag), FALL_PER_PAGE_NUM)
    item_ids = []
    if item_data:
        item_ids = item_data['star_photos']
    com = {}
    for item in item_ids:
        com = build_star_by_star_id(item, 1, 1, 1, use_cache = False)
        if com:
            items.append(com)
    data['items'] = items
    if len(item_ids) == FALL_PER_PAGE_NUM:
        data['flag'] = str(int(flag) + FALL_PER_PAGE_NUM)
    return data
