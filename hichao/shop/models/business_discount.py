# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        DECIMAL,
        VARCHAR,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.shop.models.db import (
        dbsession_generator,
        Base,
        )

class BusinessDiscount(Base):
    __tablename__ = 'ecs_business_discount'
    id = Column(INTEGER, primary_key = True)
    business_id = Column(INTEGER, nullable = False, default = 0)
    rank = Column(TINYINT, nullable = False, default = 0)       # 会员等级 0注册会员 1：v1,2:v2, 3:v3, 4:v4
    discount = Column(DECIMAL(6, 2, asdecimal = False), nullable = False, default = 1)       # 折扣，存的小数，可以直接乘以原价得到折扣价。

    def get_discount(self):
        return self.discount

    def get_component_discount(self):
        return '{0}折'.format(self.discount * 10, '.2')

def get_discounts_by_business_id(business_id):
    DBSession = dbsession_generator()
    discounts = DBSession.query(BusinessDiscount.rank, BusinessDiscount.discount).filter(BusinessDiscount.business_id == int(business_id)).all()
    DBSession.close()
    return dict(discounts)

if __name__ == '__main__':
    print get_discounts_by_business_id(73)

