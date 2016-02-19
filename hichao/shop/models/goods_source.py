# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        )
from hichao.shop.models.db import (
        dbsession_generator,
        Base,
        )

class GoodsSource(Base):
    __tablename__ = 'ecs_goods_source'
    id = Column(INTEGER, primary_key = True)
    goods_id = Column(INTEGER, nullable = False, default = 0)

def get_source_id_by_goods_id(goods_id):
    DBSession = dbsession_generator()
    source_id = DBSession.query(GoodsSource.id).filter(GoodsSource.goods_id == goods_id).first()
    if source_id: source_id = source_id[0]
    DBSession.close()
    return source_id if source_id else ''

