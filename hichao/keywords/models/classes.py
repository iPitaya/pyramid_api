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

from sqlalchemy.dialects.mysql import TIMESTAMP
from hichao.base.models.base_component import BaseComponent
from icehole_client.promotion_client import PromotionClient
import time
from hichao.util.statsd_client import timeit
from hichao.cache.cache import deco_cache
from hichao.util.date_util import FIVE_MINUTES

timer = timeit('hichao_backend.m_classes')


class Classes(UP_Base, BaseComponent):
    __tablename__ = 'classes'
    id = Column(INTEGER, primary_key=True)
    f_id = Column(INTEGER)
    type = Column(VARCHAR(64))
    type_id = Column(INTEGER)
    review = Column(INTEGER)
    pos = Column(INTEGER)
    create_ts = Column(TIMESTAMP)
    last_update_ts = Column(TIMESTAMP)


class ClassesItem(UP_Base, BaseComponent):
    __tablename__ = 'classes_item'
    id = Column(INTEGER, primary_key=True)
    title = Column(VARCHAR(64))
    en_title = Column(VARCHAR(64))
    query = Column(VARCHAR(255))
    img_url = Column(VARCHAR(255))
    review = Column(INTEGER)
    query = Column(VARCHAR(255))
    type_id = Column(INTEGER)
    pos = Column(INTEGER)
    create_ts = Column(TIMESTAMP)
    last_update_ts = Column(TIMESTAMP)


class Category(UP_Base, BaseComponent):
    __tablename__ = 'category'
    id = Column(INTEGER, primary_key=True)
    title = Column(VARCHAR(64))
    en_title = Column(VARCHAR(64))
    query_title = Column(VARCHAR(255))
    img_url = Column(VARCHAR(255))
    review = Column(INTEGER)


@timer
def get_classes_type_id_by_type(type_name):
    DBSession = rup_down_dbsession_generator()
    querys = DBSession.query(Classes.type_id).filter(Classes.review == 1).filter(Classes.type == type_name).order_by(Classes.pos.desc()).all()
    DBSession.close()
    return querys


@timer
def get_classes_type_id_by_f_id(f_id):
    DBSession = rup_down_dbsession_generator()
    querys = DBSession.query(Classes.type_id).filter(Classes.review == 1).filter(Classes.f_id == f_id).order_by(Classes.pos.desc()).all()
    DBSession.close()
    return querys


@timer
def get_classes_by_f_id(f_id):
    DBSession = rup_down_dbsession_generator()
    querys = DBSession.query(Classes).filter(Classes.review == 1).filter(Classes.f_id == f_id).all()
    DBSession.close()
    return querys


@timer
def get_classes_by_type_id(type_id):
    DBSession = rup_down_dbsession_generator()
    querys = DBSession.query(Classes).filter(Classes.review == 1).filter(Classes.type_id == type_id).filter(Classes.type == 'brand_region').all()
    DBSession.close()
    return querys


@timer
def get_classes_item_by_id(id):
    DBSession = rup_down_dbsession_generator()
    query = DBSession.query(ClassesItem).filter(ClassesItem.review == 1).filter(ClassesItem.id == id).all()
    DBSession.close()
    return query


@timer
def get_classes_item_type_id_by_id(id):
    DBSession = rup_down_dbsession_generator()
    query = DBSession.query(ClassesItem.type_id).filter(ClassesItem.review == 1).filter(ClassesItem.id == id).first()
    DBSession.close()
    return query


@timer
def get_region_component_by_id(type_id):
    pc = PromotionClient()
    content = pc.get_content_by_id(type_id)
    return content


@timer
def get_region_components_by_ids(type_ids):
    pc = PromotionClient()
    contents = pc.get_contents_by_ids(type_ids)
    return contents


def get_class_id_by_type_and_type_id(type, type_id):
    DBSession = rup_down_dbsession_generator()
    id = DBSession.query(Classes.id).filter(Classes.review == 1).filter(Classes.type_id == type_id).filter(Classes.type == type).first()
    DBSession.close()
    return id[0] if id else ''


@timer
def build_regions_tag_component(obj, com_type='regionBrands', tagType='tagCell'):
    com = {}
    if obj:
        action = {}
        action['title'] = obj.title
        action['actionType'] = com_type
        action['id'] = str(obj.id)
        com['title'] = obj.title
        com['picUrl'] = ''
        com['componentType'] = tagType
        com['id'] = str(obj.id)
        com['action'] = action
    return com


@timer
def get_class_two_id(query_id, cate_name):
    content = get_classes_by_type_id(int(query_id))
    cate_id = 0
    if content:
        item = content[0]
        temps = get_classes_by_f_id(item.id)
        for temp in temps:
            classes_items = get_classes_item_by_id(temp.type_id)
            for classes_item in classes_items:
                if classes_item.title == cate_name:
                    cate_id = temp.id
                    break
    return cate_id


def build_component_region_category_item(obj):
    com = {}
    if obj:
        com['title'] = obj.title
        com['word'] = obj.title
        com['en_title'] = obj.en_title
        com['picUrl'] = obj.img_url
        action = {}
        action['title'] = obj.title
        action['query'] = obj.query_title
        action['regionName'] = obj.title
        action['actionType'] = 'searchRegion'
        action['id'] = str(obj.id)
        com['action'] = action
    return com


@timer
def get_category_by_id(category_id):
    DBSession = rup_down_dbsession_generator()
    querys = DBSession.query(Category).filter(Classes.review == 1).filter(Category.id == category_id).first()
    DBSession.close()
    return querys if querys else None


@timer
@deco_cache(prefix='category_by_title', recycle=FIVE_MINUTES)
def get_category_by_title(title):
    DBSession = rup_down_dbsession_generator()
    querys = DBSession.query(Category).filter(Category.title == title).first()
    DBSession.close()
    return querys if querys else None
