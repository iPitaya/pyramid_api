# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        TEXT,
        func,
        DateTime,
        FLOAT,
        BIGINT
    )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.mall.models.db  import(
        ecshop_dbsession_generator,
        ecshop_Base,
    )

from hichao.base.models.base_component import BaseComponent
from hichao.cache.cache import deco_cache
from hichao.util.date_util import TEN_MINUTES, DAY, MINUTE
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_ecshop_goods')

class EcshopGoodsSource(ecshop_Base,BaseComponent):
    __tablename__ = 'ecs_goods_source'
    id = Column(INTEGER,primary_key = True)
    goods_id = Column(INTEGER,nullable = False)

class EcshopGoods(ecshop_Base,BaseComponent):
    __tablename__ = 'ecs_goods'
    goods_id = Column(INTEGER,primary_key = True)
    goods_number = Column(BIGINT,nullable = False)
    is_delete = Column(INTEGER)
    is_on_sale = Column(INTEGER)

class EcshopBusinessInfo(ecshop_Base,BaseComponent):
    __tablename__ = 'ecs_business_info'
    business_id = Column(INTEGER,primary_key = True)
    brand_name = Column(VARCHAR(255),nullable = False)
    brand_type = Column(INTEGER)
    status = Column(TINYINT)
    brand_logo = Column(VARCHAR(255))

class EcshopCommonCategory(ecshop_Base,BaseComponent):
    __table_args__ = {'schema': 'common'}
    __tablename__ = 'categories_v2'
    cid = Column(INTEGER,primary_key = True)
    name = Column(VARCHAR(20))
    match_words = Column(VARCHAR(100))

@timer
@deco_cache(prefix = 'ecshop_goods_number', recycle = MINUTE)
def get_ecshop_goods_number(source_id):
    DBSession = ecshop_dbsession_generator()
    goods_number = DBSession.query(EcshopGoods,EcshopGoods.goods_number).join(EcshopGoodsSource,EcshopGoods.goods_id == EcshopGoodsSource.goods_id).filter(EcshopGoodsSource.id == int(source_id)).filter(EcshopGoods.is_delete == 0).filter(EcshopGoods.is_on_sale == 1).first()
    DBSession.close()
    if goods_number:
        return goods_number.goods_number
    else:
        return 0

@timer
@deco_cache( prefix = 'brand_name_business_id', recycle = TEN_MINUTES)
def get_brand_name_by_business_id(business_id):
    DBSession = ecshop_dbsession_generator()
    business_info = DBSession.query(EcshopBusinessInfo).filter(EcshopBusinessInfo.business_id == int(business_id)).filter(EcshopBusinessInfo.status == 1).first()
    DBSession.close()
    if business_info:
        return business_info.brand_name
    else:
        return ''

@timer
@deco_cache( prefix = 'brand_info_business_id', recycle = TEN_MINUTES)
def get_brand_info_by_business_id(business_id):
    DBSession = ecshop_dbsession_generator()
    business_info = DBSession.query(EcshopBusinessInfo).filter(EcshopBusinessInfo.business_id == int(business_id)).filter(EcshopBusinessInfo.status == 1).first()
    DBSession.close()
    return business_info

@deco_cache( prefix = 'cate_name_cid', recycle = TEN_MINUTES)
def get_cate_name_by_cid(cid):
    DBSession = ecshop_dbsession_generator()
    cate_info = DBSession.query(EcshopCommonCategory).filter(EcshopCommonCategory.cid == int(cid)).first()
    DBSession.close()
    result = ''
    if cate_info:
        result = cate_info.name
    return result

@deco_cache( prefix = 'match_words_cid', recycle = TEN_MINUTES)
def get_match_words_by_cid(cid):
    DBSession = ecshop_dbsession_generator()
    cate_info = DBSession.query(EcshopCommonCategory).filter(EcshopCommonCategory.cid == int(cid)).first()
    DBSession.close()
    result = ''
    if cate_info:
        result = cate_info.match_words
    return result
