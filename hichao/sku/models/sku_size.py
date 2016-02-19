# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        )
from hichao.sku.models.db import (
        sku_img_size_dbsession_generator,
        Base,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import FIVE_MINUTES
from hichao.base.models.base_component import BaseComponent
from hichao.util.statsd_client import timeit

class SkuSize(Base, BaseComponent):
    __tablename__ = 'sku_full_image_size'
    id = Column(INTEGER, primary_key = True)
    sku_id = Column(INTEGER, nullable = False)
    width = Column(INTEGER)
    height = Column(INTEGER)

    def __init__(self, sku_id, width, height):
        self.sku_id = sku_id
        self.width = width
        self.height = height

@timeit('hichao_backend.m_sku_skusize')
@deco_cache(prefix = 'sku_size', recycle = FIVE_MINUTES)
def get_size_by_sku_id(sku_id, use_cache = True):
    DBSession = sku_img_size_dbsession_generator()
    size = DBSession.query(SkuSize.width, SkuSize.height).filter(SkuSize.sku_id == sku_id).first()
    DBSession.close()
    return size

