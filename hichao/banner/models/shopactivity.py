
from sqlalchemy import (
        func,
        Column,
        INTEGER,
        VARCHAR,
        DECIMAL,
        BIGINT,
        DateTime,
        distinct,
        )
from hichao.banner.models.db import (
        rdbsession_generator,
        Base,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.base.models.base_component import BaseComponent
from hichao.topic.models.topic import (
        get_topic_by_id,
        get_last_topic_ids,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import FIVE_MINUTES
from hichao.util.statsd_client import timeit
import time
import datetime

timer = timeit('hichao_backend.m_shopactivity')

class BannerActivityBase(object):
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    item_id = Column(INTEGER, nullable = False)
    item_type = Column(VARCHAR(20), nullable = False)
    pos = Column(INTEGER, nullable = False)
    review = Column(TINYINT, nullable = False, default = 0)
    start_date = Column(DateTime, nullable = False)
    end_date = Column(DateTime, nullable = False)
    img_url = Column(VARCHAR(256), nullable = True, default = '')
    create_ts = Column(DateTime, nullable = False)

class BannerShopActivity(Base, BannerActivityBase):
    __tablename__ = 'shop_recom_activity'


class BannerShopCategory(Base, BannerActivityBase):
    __tablename__ = 'category_recom_activity'
    category = Column(VARCHAR(20),nullable = False)
    category_id = Column(INTEGER,nullable = False)

@timer
def get_shop_activity_ids():
    cls = BannerShopActivity
    DBSession = rdbsession_generator()
    now = datetime.datetime.now()
    bns = DBSession.query(distinct(cls.pos), cls.item_id, cls.item_type, cls.img_url, cls.id).filter(cls.review == 1).filter(cls.start_date <=now).filter(cls.end_date >= now).order_by(cls.pos.asc()).order_by(cls.id)
    DBSession.close()
    bns = [(int(bn[0]), int(bn[1]), str(bn[2]), str(bn[3]), str(bn[4])) for bn in bns]
    mx_num = 3
    if len(bns) > 1:
        if bns[-1][0] > 3:
            mx_num = bns[-1][0] 
    ids = [None] * mx_num
    #for i  in range(0,mx_num):
    #    ids[i] = None
    for bp in  bns:
        ids[bp[0]-1] = bp
    #for bp in ids:
    #    print bp
    
    return ids

@timer
def get_shop_category_ids(cate):
    cls = BannerShopCategory
    DBSession = rdbsession_generator()
    now = datetime.datetime.now()
    bns = DBSession.query(cls.pos, cls.item_id, cls.item_type, cls.img_url, cls.id).filter(cls.review == 1).filter(cls.category_id == cate).filter(cls.start_date <= now).filter(cls.end_date >= now).order_by(cls.pos.desc()).order_by(cls.id).limit(1)
    #bns = DBSession.query(cls.pos, cls.item_id, cls.item_type, cls.img_url, cls.id,cls.start_date).filter(cls.review == 1).filter(cls.category == cate).order_by(cls.pos.desc()).order_by(cls.id).limit(1)
    DBSession.close()
    bns = [(int(bn[0]), int(bn[1]), str(bn[2]), str(bn[3]), str(bn[4])) for bn in bns]
    return bns


if __name__ == "__main__":
    pass

