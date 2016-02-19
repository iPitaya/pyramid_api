# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        func,
        TIMESTAMP,
        VARCHAR,
        DECIMAL,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.event.models.db import (
        dbsession_generator,
        Base,
        )

class NvShenOrder(Base):
    __tablename__ = 'ns_orders'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    order_id = Column('order_num', VARCHAR(128))
    source_ids = Column(VARCHAR(1024))
    real_price = Column(DECIMAL(10, 2, asdecimal = False))
    lottery_count = Column(TINYINT)
    review = Column(TINYINT)
    create_ts = Column(TIMESTAMP)
    update_ts = Column(TIMESTAMP)
    is_active = Column(TINYINT)

