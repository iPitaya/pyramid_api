# -*- coding:utf-8 -*-

from hichao.util.statsd_client import timeit
from sqlalchemy import (
        func,
        Column,
        INTEGER,
        VARCHAR,
        TEXT,
        DateTime,
        TIMESTAMP,
        DECIMAL,
    )
from sqlalchemy.dialects.mysql import (
        TINYINT,
    )
from hichao.flash_sale.models.db import (
        rdbsession_generator,
        Base,
    )

from hichao.base.models.base_component import BaseComponent
from hichao.flash_sale.models.count  import get_peopleCount_by_sku_id
from hichao.flash_sale.models.flash_sale import get_flashsale_status_by_flashsale_id
from hichao.base.config import FALL_PER_PAGE_NUM
from hichao.cache.cache import deco_cache
import datetime
from hichao.flash_sale.models.flash_sale import (
        FLASH_SALE_END,
        FLASH_SALE_END_STATE,
        FLASH_SALE_NOW,
        FLASH_SALE_NOW_SKU,
        FLASH_SALE_NOW_STATE,
        FLASH_SALE_NOSTART,
        FLASH_SALE_NOSTART_STATE,
        get_flashsale_id_now_state,
    )
from hichao.util.image_url import build_flash_sale_image_url
from hichao.mall.models.ecshop_goods  import get_ecshop_goods_number

FALL_PER_PAGE_NUM = 18

timer = timeit('hichao_backend.m_flash_sale_sku')

class FlashSaleSku(Base,BaseComponent):
    __tablename__ = 'flash_sale_sku'
    id = Column(INTEGER, primary_key = True)
    title = Column(VARCHAR(255))
    source_id = Column(VARCHAR(128))
    img_url = Column(VARCHAR(2048))
    discount = Column(VARCHAR(128))
    discount_price = Column(DECIMAL(20,2))
    original_price = Column(DECIMAL(20,2))
    publish_datetime = Column(DateTime)
    review = Column(TINYINT)
    pos = Column(INTEGER)
    sku_id = Column(INTEGER)
    flash_sale_id = Column(INTEGER)
    stock = Column(INTEGER)

    def to_ui_action(self):
        action = {} 
        action['actionType'] = 'detail'
        action['id'] = str(self.sku_id)
        action['source'] = 'ecshop'
        action['sourceId'] = str(self.source_id)
        action['type'] = 'sku'
        return action
        

@timer
@deco_cache(prefix = 'flash_sale_sku_list', recycle = 60)
def get_flash_sale_sku_list(flash_sale_id, offset = 0, limit = FALL_PER_PAGE_NUM, use_cache = True):
    ''' 从数据库中 获得某闪购的单品 list  '''
    DBSession = rdbsession_generator()
    flashsaleskus = DBSession.query(FlashSaleSku).filter(FlashSaleSku.flash_sale_id == int(flash_sale_id)).filter(FlashSaleSku.review == 1).order_by(FlashSaleSku.pos.desc(),FlashSaleSku.id.desc()).offset(offset).limit(limit)
    DBSession.close()
    return flashsaleskus

@timer
def build_component_flash_sale(item):
    ''' 生成闪购单品列表 的component  '''
    ui = {}
    if item:
        com = {}
        com['componentType'] = 'tuanItemCell'
        com['peopleCount'] = ''
        com['price'] = str(item.discount_price)
        com['priceOrig'] = str(item.original_price)
        com['picUrl'] = build_flash_sale_image_url(item.img_url)
        com['tuanState'] = ''
        com['id'] = str(item.sku_id)
        com['title'] = item.title
        if item.original_price == 0:
            com['priceOrig'] = str(item.discount_price)
        com['priceOrig'] = str(item.original_price)
        com['discount'] = "%.1f折"%(item.discount_price/item.original_price * 10)
        action = item.to_ui_action()
        com['action'] = action
        ui['component'] = com
    return ui

@timer
def build_component_flash_sale_panic(item):
    ''' 闪购单品替换限量抢购 的component  '''
    ui = {}
    if item:
        com = {}
        com['componentType'] = 'panicBuyingCell'
        com['price'] = str(item.discount_price)
        com['origin_price'] = str(item.original_price)
        com['img_url'] = build_flash_sale_image_url(item.img_url)
        com['id'] = str(item.sku_id)
        com['title'] = item.title
        com['sale'] =  '0'
        stock = get_ecshop_goods_number(item.source_id)
        # shengyu
        com['stock'] = str(stock)
        # xianliang
        com['all_stock'] = str(item.stock)
        if item.original_price == 0:
            com['origin_price'] = str(item.discount_price)
        com['origin_price'] = str(item.original_price)
        com['discount'] = "%.1f折"%(item.discount_price/item.original_price * 10)
        if com['discount'] == '10.0折':
            com['discount'] = '10折'
        action = item.to_ui_action()
        com['action'] = action
        ui['component'] = com
    return ui

@timer
def get_panic_by_flash_sale():
    flash_sale = get_flashsale_id_now_state()
    data_items = []
    if not flash_sale:
        return data_items
    items = get_flash_sale_sku_list(flash_sale['flash_sale_id'], 0, 1)
    for item in items:
        data_item = build_component_flash_sale_panic(item)
        if data_item:
            data_item['component']['limit_time'] = flash_sale['expires']
        data_items.append(data_item)
        break
    return data_items

@timer
def get_flash_sale_skus_by_flash_sale_id(flash_sale_id, offset, limit):
    ''' 通过每个闪购id 获得该时间段的闪购  '''
    items = get_flash_sale_sku_list(flash_sale_id, offset, limit)
    data = {}
    data['items'] = []
    for item in items:
        data_item = build_component_flash_sale(item)
        if data_item:
            if not item.publish_datetime:
                item.publish_datetime = datetime.datetime.now()
            data_item['component']['peopleCount'] = str(get_peopleCount_by_sku_id(item.sku_id,item.publish_datetime.microsecond))
            data_item['component']['state'] = get_flashsale_status_by_flashsale_id(item.flash_sale_id)
            if data_item['component']['state'] == FLASH_SALE_NOW_STATE:
                result = ''
                result = get_ecshop_goods_number(item.source_id)
                if result:
                    data_item['component']['tuanState'] = FLASH_SALE_NOW_SKU
                else:
                    data_item['component']['tuanState'] = FLASH_SALE_END
                    data_item['component']['state'] = FLASH_SALE_END_STATE
            if data_item['component']['state'] == FLASH_SALE_END_STATE:
                data_item['component']['action'] = {}
                data_item['component']['tuanState'] = FLASH_SALE_END
            if data_item['component']['state'] == FLASH_SALE_NOSTART_STATE:
                data_item['component']['tuanState'] = FLASH_SALE_NOSTART

            data['items'].append(data_item)
    return data

