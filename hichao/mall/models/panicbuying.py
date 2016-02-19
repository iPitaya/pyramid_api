# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        TEXT,
        func,
        DateTime,
        FLOAT,
    )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.mall.models.db  import(
        panic_buying_dbsession_generator,
        Panic_Base,
    )

from hichao.base.models.base_component import BaseComponent
from hichao.util.image_url import build_search_star_list_image_url
from hichao.util.statsd_client import timeit
import datetime
from hichao.sku.models.sku import get_sku_by_id
from hichao.util.image_url import build_panic_image_url_by_short_url
from hichao.mall.models.ecshop_goods import get_ecshop_goods_number
import time

timer = timeit('hichao_backend.m_mall_panic_buying')

class PanicBuying(Panic_Base,BaseComponent):
    __tablename__ = 'panic_buying'
    id = Column(INTEGER,primary_key = True)
    item_id = Column(INTEGER)
    title = Column(VARCHAR(255),nullable = False)
    img_url = Column(VARCHAR(255),nullable = False)
    price = Column(FLOAT,nullable = False)
    high_price = Column(FLOAT,nullable = False)
    origin_price = Column(FLOAT,nullable = False)
    sale = Column(INTEGER,nullable = False)
    stock = Column(INTEGER,nullable = False)
    create_ts = Column(DateTime,nullable = False)
    update_ts = Column(DateTime,nullable = False)
    review = Column(TINYINT,nullable = False)
    all_stock = Column(INTEGER,nullable = False)
    source_id = Column(VARCHAR(255),nullable = False)
    start_datetime = Column(DateTime,nullable = False)
    end_datetime = Column(DateTime,nullable = False)


@timer
def get_panic_buying_msg():
    DBSession = panic_buying_dbsession_generator()
    now_time = datetime.datetime.now()
    panic_buying = DBSession.query(PanicBuying).filter(PanicBuying.review == 1).filter(PanicBuying.end_datetime > now_time).order_by(PanicBuying.end_datetime).first()
    if not panic_buying:
        panic_buying = DBSession.query(PanicBuying).filter(PanicBuying.review == 1).order_by(PanicBuying.end_datetime.desc()).first()
    DBSession.close()
    return panic_buying

@timer
def build_component_panic_buying(panic_item):
    ui = {}
    if panic_item:
        com = {} 
        com['id'] = str(panic_item.item_id)
        com['panicId'] = str(panic_item.id)
        com['title'] = panic_item.title
        com['img_url'] = build_panic_image_url_by_short_url('shop', panic_item.img_url)
        com['price'] = str(panic_item.price)
        com['sale'] =  str(panic_item.sale)
        stock = get_ecshop_goods_number(panic_item.source_id)
        # shengyu
        com['stock'] = str(stock)
        # xianliang
        com['all_stock'] = str(panic_item.stock)
        if panic_item.origin_price == 0:
            panic_item.origin_price = panic_item.price
        com['origin_price'] = str(panic_item.origin_price)
        com['discount'] = "%.1f折"%(panic_item.price/panic_item.origin_price * 10)
        com['componentType'] = 'panicBuyingCell'
        start_datetime = panic_item.start_datetime
        end_datetime = panic_item.end_datetime
        now_datetime = datetime.datetime.now()
        com['limit_time'] = '0'
        if end_datetime:
            if end_datetime > now_datetime :
                result_time = end_datetime - now_datetime
                time_num = result_time.total_seconds()
                if time_num > 0:
                    com['limit_time'] = str(time_num).split('.')[0]
        action = {}
        action['sourceId'] = panic_item.source_id
        action['source'] = 'ecshop'
        action['id'] = str(panic_item.item_id)
        action['actionType'] = 'detail'
        action['type'] = 'sku'
        com['action'] = action
        ui['component'] = com
    return ui

@timer
def build_panic_buying():
    panic_item = get_panic_buying_msg()
    panic_list = []
    item = {}
    item = build_component_panic_buying(panic_item)
    panic_list.append(item)
    return panic_list


