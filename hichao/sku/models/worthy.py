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

timer = timeit('hichao_backend.m_sku_worthy')

class Worthy(Base, BaseComponent):
    __tablename__ = 'worth_sku'
    id = Column(INTEGER, primary_key=True, autoincrement = True)
    sku_id = Column(INTEGER)
    user_id = Column(INTEGER)
    editor_name = Column(VARCHAR(128))
    pos = Column(INTEGER)
    review = Column(TINYINT)
    ts = Column(TIMESTAMP)

    def __init__(self, sku_id, user_id, editor_name, pos, review, ts):
        self.sku_id = sku_id
        self.user_id = user_id
        self.editor_name = editor_name
        self.pos = pos
        self.review = review
        self.ts = ts

@timer
@deco_cache(prefix = 'worthy_sku_ids', recycle = TEN_MINUTES)
def get_worthy_sku_list(day, offset, limit):
    DBSession = rdbsession_generator()
    sku_ids = DBSession.query(Worthy.sku_id).filter(Worthy.ts >= day).filter(Worthy.ts < day + datetime.timedelta(1)).filter(Worthy.review == 1).order_by(Worthy.pos.desc()).offset(offset).limit(limit).all()
    sku_ids = [sku[0] for sku in sku_ids]
    DBSession.close()
    return sku_ids

