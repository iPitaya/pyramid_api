# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        )
from hichao.event.models.db import (
        shop_dbsession_generator,
        ShopBase,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE
from hichao.util.statsd_client import timeit
timer = timeit('hichao_backend.m_event_shop_bonus')

class ShopUsers(ShopBase):
    __tablename__ = "ecs_users"
    id = Column('user_id',INTEGER,primary_key = True,autoincrement = True)
    user_name = Column(INTEGER)    

        
@timer
@deco_cache(prefix = 'get_id_by_name', recycle = MINUTE)
def get_id_by_name(user_name):
    DBSession = shop_dbsession_generator()
    user_id = DBSession.query(ShopUsers.id).filter(ShopUsers.user_name == int(user_name)).first()
    DBSession.close()
    return user_id[0] if user_id else 0