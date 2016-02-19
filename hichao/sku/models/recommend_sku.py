# -*- coding:utf-8 -*-

from hichao.util.statsd_client import timeit
from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        TIMESTAMP,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.sku.models.db import (
        rdbsession_generator,
        Base,
        )
from hichao.base.models.base_component import BaseComponent
from hichao.cache.cache import deco_cache
from hichao.util.date_util import TEN_MINUTES
import datetime

timer = timeit('hichao_backend.m_region_sku_recommend')

class RegionSkusRecommend(Base, BaseComponent):
    __tablename__ = 'region_sku_recommend'
    id = Column(INTEGER, primary_key=True, autoincrement = True)
    sku_id = Column(INTEGER)
    editor_name = Column(VARCHAR(128))
    pos = Column(INTEGER)
    review = Column(TINYINT)
    ts = Column(TIMESTAMP)
    region = Column(INTEGER)

    def __init__(self, sku_id, editor_name, pos, review, ts, region):
        self.sku_id = sku_id
        self.editor_name = editor_name
        self.pos = pos
        self.review = review
        self.ts = ts
        self.region = region

@timer
@deco_cache(prefix = 'recommend_sku_ids', recycle = TEN_MINUTES)
def get_recommend_sku_list(region_id, offset, limit):
    day = datetime.date.today()
    DBSession = rdbsession_generator()
    sku_ids = DBSession.query(RegionSkusRecommend.sku_id).filter(RegionSkusRecommend.region == region_id).filter(RegionSkusRecommend.ts <= day).filter(
        RegionSkusRecommend.review == 1).order_by(RegionSkusRecommend.ts.desc()).order_by(RegionSkusRecommend.pos.desc()).offset(offset).limit(limit).all()
    sku_ids = [{'sku_id':sku[0]} for sku in sku_ids]
    DBSession.close()
    return sku_ids


