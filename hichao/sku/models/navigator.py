# -*- coding: utf-8 -*-

from sqlalchemy import (
    Column,
    INTEGER,
    VARCHAR,
    TIMESTAMP,
)
from sqlalchemy.dialects.mysql import TINYINT
from hichao.util.date_util import FIVE_MINUTES
from hichao.util.statsd_client import timeit
from hichao.sku.models.db import (
    Base,
    rdbsession_generator,
)
from hichao.keywords.models.db import (
    rup_down_dbsession_generator,
    UP_Base,
)    
from hichao.keywords.models.classes import Classes, ClassesItem
from hichao.cache.cache import deco_cache
from hichao.mall.models.ecshop_goods import get_cate_name_by_cid,get_match_words_by_cid

timer = timeit('hichao_backend.m_region_recommend_tag')

class RegionRecommendTag(Base):
    __tablename__ = 'region_cat_recommend'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    name = Column(VARCHAR(255), nullable = False)
    cat_ids = Column(VARCHAR(255), nullable = False)
    region = Column(INTEGER, nullable = False)
    pos = Column(INTEGER, nullable = False)
    review = Column(TINYINT, nullable = False)

#获取首页、专区分类导航
@timer
@deco_cache(prefix = 'region_recommend_tag', recycle = FIVE_MINUTES)
def get_region_recommend_tag(region, limit = 10, use_cache = True):
    DBSession = rdbsession_generator()
    name_ids = DBSession.query(RegionRecommendTag.name, RegionRecommendTag.cat_ids).filter(RegionRecommendTag.region == region).filter(RegionRecommendTag.review == 1).order_by(RegionRecommendTag.pos.desc()).limit(limit).all()
    DBSession.close()
    tab_list = []
    for item in name_ids:
        com = {}
        com['nav_name'] = item[0][:4]
        com['nav_cat_ids'] = item[1] if str(item[1]) != "0" else ""
        cat_str = ''
        for cat_id in item[1].split(','):
            cate_name = get_match_words_by_cid(cat_id)
            if cat_str:
                cat_str = cat_str + '|' + cate_name
            else:
                cat_str = cate_name
        com['cate_names'] = cat_str
        tab_list.append(com)
    return tab_list

#获取专区顶部分类导航
@timer
@deco_cache(prefix = 'region_navigator', recycle = FIVE_MINUTES)
def get_region_navigator(item_type = 'region_nav', use_cache = True):
    DBSession = rup_down_dbsession_generator()
    ids = DBSession.query(Classes.type_id).filter(Classes.type == item_type).filter(Classes.review == 1).order_by(Classes.pos.desc()).all()
    ids = [id[0] for id in ids]
    ret = DBSession.query(ClassesItem.id, ClassesItem).filter(ClassesItem.id.in_(ids)).all()
    ret = dict(ret)
    DBSession.close()
    tab_list = []
    for _id in ids:
        item = ret.get(_id, None)
        if item:
            com = {}
            com['nav_name'] = item.title
            com['nav_id'] = str(item.type_id)
            tab_list.append(com)
    return  tab_list

if __name__ == '__main__':
    #ret = get_region_recommend_tag(1458)
    #print ret
    ret = get_region_navigator()
    print ret

