# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        BIGINT,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.shop.models.db import (
        dbsession_generator,
        Base,
        )
from hichao.util.formatter import format_price
import time

class Goods(Base):
    __tablename__ = 'ecs_goods'

    goods_id = Column(INTEGER, primary_key = True)
    shop_price = Column(VARCHAR(32), nullable = False, default = '')
    goods_number = Column(BIGINT, nullable = False)
    is_delete = Column(TINYINT, nullable = False)
    min_purchase_num = Column(INTEGER, nullable = False)

    def get_price(self):
        price = self.shop_price
        if self.has_range_price():
            price = self.shop_price.split('-', 1)[0].strip()
            price = float(price) if price else 0
        return float(price)

    def has_range_price(self):
        return True if '-' in self.shop_price else False

    def get_component_price(self):
        price = format(self.get_price(),'.2f')
        final_price = format_price(price)
        if self.has_range_price():
            final_price = '{0}起'.format(final_price)
        return final_price

    def get_component_discount_price(self, discount):
        discount_price = format(self.get_price() * float(discount), '.2f')
        final_discount_price = format_price(discount_price)
        if self.has_range_price():
            final_discount_price = '{0}起'.format(final_discount_price, '.2f')
        return str(final_discount_price)

    def get_goods_state_msg(self):
        result = ''
        if self.is_delete == 1:
            result = '已售罄'
            return result
        if (self.min_purchase_num > 0 and self.goods_number<self.min_purchase_num) or (self.goods_number <= 0):
            result = '已售罄'
            return result
        return result

def get_goods_by_goods_id(goods_id):
    DBSession = dbsession_generator()
    goods = DBSession.query(Goods).filter(Goods.goods_id == goods_id).first()
    DBSession.close()
    return goods

