# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        BIGINT,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.star.models.db import (
        dbsession_generator,
        rdbsession_generator,
        Base,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MONTH, FIVE_MINUTES
from hichao.util.statsd_client import timeit
import transaction

timer = timeit('hichao_backend.m_star_starsku')
timer_mysql = timeit('hichao_backend.m_star_starsku.mysql')

class StarSku(Base):
    __tablename__ = 'star_sku'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    star_id = Column(INTEGER, nullable = False)
    sku_id = Column(BIGINT, nullable = False)
    tab_index = Column(TINYINT, nullable = False)
    tab_position = Column(TINYINT, nullable = False)
    part = Column(TINYINT)

    def __init__(self, star_id, sku_id, tab_index, tab_position, part):
        self.star_id = star_id
        self.sku_id = sku_id
        self.tab_index = tab_index
        self.tab_position = tab_position
        self.part = part

    def __getitem__(self, key):
        return getattr(self, key)

@timer
def add_star_sku(star_id, sku_id, tab_index, tab_position, part):
    star_sku = StarSku(star_id, sku_id, tab_index, tab_position, part)
    try:
        DBSession = dbsession_generator()
        DBSession.add(star_sku)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ':', ex
        return 0
    finally:
        DBSession.close()
    return 1

@timer
def delete_star_sku(star_id, sku_id):
    try:
        DBSession = dbsession_generator()
        DBSession.query(StarSku).filter(StarSku.star_id == star_id).filter(StarSku.sku_id == sku_id).delete()
    except Exception, ex:
        DBSession.rollback()
        print Exception, ':', ex
        return 0
    finally:
        DBSession.close()
    return 1

@timer
@deco_cache(prefix = 'star_tab', recycle = FIVE_MINUTES)
@timer_mysql
def get_tabs_index_by_star_id(star_id, use_cache = True):
    DBSession = rdbsession_generator()
    idxs = DBSession.query(StarSku.tab_index, StarSku.part).filter(StarSku.star_id == star_id).group_by(StarSku.tab_index, StarSku.part).order_by(
        StarSku.part).all()
    DBSession.close()
    return idxs

@timer
def get_skus_by_star_tab(star_id, tab_idx):
    '''
    此方法与get_tabs_index_by_star_id配合使用，传入的tab_index应该是一个(tab_index,part)元组。
    '''
    DBSession = rdbsession_generator()
    star_skus = DBSession.query(StarSku).filter(StarSku.star_id == star_id).filter(StarSku.tab_index == tab_idx[0]).filter(
        StarSku.part == tab_idx[1]).order_by(StarSku.tab_position).all()
    DBSession.close()
    return star_skus

@timer
@deco_cache(prefix = 'star_id_by_sku_id', recycle = FIVE_MINUTES)
@timer_mysql
def get_star_id_by_sku_id(sku_id, use_cache = True):
    DBSession = rdbsession_generator()
    star_id = DBSession.query(StarSku.star_id).filter(StarSku.sku_id == sku_id).first()
    DBSession.close()
    if star_id:
        star_id = star_id[0]
    else:
        star_id = -1
    return star_id

@timer
@deco_cache(prefix = 'star_ids_by_sku_id', recycle = FIVE_MINUTES)
@timer_mysql
def get_star_ids_by_sku_id(sku_id, use_cache = True):
    try:
        DBSession = rdbsession_generator()
        star_ids = DBSession.query(StarSku.star_id).filter(StarSku.sku_id == sku_id).order_by(StarSku.star_id.desc()).limit(10)
        star_ids = [id[0] for id in star_ids]
    except Exception, ex:
        print Exception, ex
    finally:
        DBSession.close()
    return star_ids

@timer
def delete_star_sku_by_star_id(star_id):
    print 'enter delete_star_sku_by_star_id'
    try:
        DBSession = dbsession_generator()
        star_id = DBSession.query(StarSku).filter(StarSku.star_id == star_id).delete()
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print 'delete_star_sku_by_star_id'
        print Exception, ex
        return 0
    finally:
        DBSession.close()
    return 1

if __name__ == '__main__':
    #if not Base.metadata.bind.has_table('star_sku'):
    #    Base.metadata.create_all()
    pass

