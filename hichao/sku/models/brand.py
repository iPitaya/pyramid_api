# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        VARCHAR,
        TIMESTAMP,
        )
from sqlalchemy.dialects.mysql import INTEGER
from hichao.sku.models.db import (
        Base,
        bdbsession_generator,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import DAY

class Brand(Base):
    __tablename__ = 'brand_new'
    id = Column(INTEGER(unsigned = True), primary_key = True, autoincrement = True)
    brandcn = Column(VARCHAR(255))
    branden = Column(VARCHAR(255))
    image_url = Column(VARCHAR(1024))
    ts = Column(TIMESTAMP)

    def __init__(self, brandcn, branden, image_url, ts):
        self.brandcn = brandcn
        self.branden = branden
        self.image_url = image_url
        self.ts = ts

@deco_cache(prefix = 'brand', recycle = DAY)
def get_brand_by_id(brand_id):
    DBSession = bdbsession_generator()
    brand = DBSession.query(Brand).filter(Brand.id == int(brand_id)).first()
    DBSession.close()
    return brand

if __name__ == '__main__':
    brand = get_brand_by_id(1)
    print brand.brandcn

