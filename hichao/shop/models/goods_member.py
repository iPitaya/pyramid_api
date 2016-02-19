# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        func,
        )
from sqlalchemy.dialects.mysql import (
        TINYINT,
        SMALLINT,
        )
from hichao.shop.models.db import (
        dbsession_generator,
        Base,
        )
from hichao.util.image_url import build_member_sku_image_url
from hichao.util.statsd_client import timeit
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE, HOUR
import time

timer = timeit('hichao_backend.m_goods_member')
timer_mysql = timeit('hichao_backend.m_goods_member.mysql')

class GoodsMember(Base):
    __tablename__ = 'ecs_goods_member'
    id = Column(INTEGER, primary_key = True)
    goods_id = Column(INTEGER, nullable = False, default = 0)
    business_id = Column(INTEGER, nullable = False, default = 0)
    goods_name = Column(VARCHAR(120), nullable = False, default = '')
    img_data = Column(VARCHAR(255), nullable = False, default = '')
    is_v = Column(TINYINT, nullable = False, default = 0)
    v_sort = Column(SMALLINT, nullable = False, default = 0)
    is_v_time = Column(INTEGER, nullable = False, default = 0)
    publish_time = Column(INTEGER, nullable = False, default = 0)

    def get_component_goods_id(self):
        return str(self.goods_id)

    def get_component_title(self):
        return self.goods_name

    def get_component_business_id(self):
        return str(self.business_id)

    def get_component_pic_url(self):
        return build_member_sku_image_url(self.img_data)


@timer
@deco_cache(prefix = 'goods_member_last_publish_time', recycle = MINUTE)
@timer_mysql
def get_last_publish_times(use_cache = True):
    tm = time.time()
    DBSession = dbsession_generator()
    last_publish_times = DBSession.query(GoodsMember.publish_time).filter(GoodsMember.publish_time <= tm).group_by(GoodsMember.publish_time).order_by(GoodsMember.publish_time.desc()).limit(1)
    if last_publish_times:
        last_publish_times = [last_publish_time[0] for last_publish_time in last_publish_times]
    DBSession.close()
    return last_publish_times

@timer
@deco_cache(prefix = 'goods_member_last_goods', recycle = MINUTE)
@timer_mysql
def get_last_goods(use_cache = True):
    last_publish_times = get_last_publish_times()
    if not last_publish_times: return []
    DBSession = dbsession_generator()
    goods = DBSession.query(GoodsMember).filter(GoodsMember.publish_time.in_(last_publish_times)).filter(GoodsMember.is_v == 1).order_by(GoodsMember.publish_time.desc()).order_by(GoodsMember.v_sort).all()
    DBSession.close()
    return goods

@timer
@deco_cache(prefix = 'goods_member_all_goods', recycle = MINUTE)
@timer_mysql
def get_all_goods():
    tm_now = time.time()
    DBSession = dbsession_generator()
    #获得当前时间之前所有有效数据
    goods = DBSession.query(GoodsMember).filter(GoodsMember.publish_time <= tm_now).filter(GoodsMember.is_v == 1).order_by(GoodsMember.publish_time.desc()).order_by(GoodsMember.v_sort).all()
    DBSession.close()
    return goods

@timer
@deco_cache(prefix = 'goods_member_goods_count', recycle = HOUR)
@timer_mysql
def get_goods_count():
    tm_now = time.time()
    DBSession = dbsession_generator()
    goods_count = DBSession.query(func.count(GoodsMember.id)).filter(GoodsMember.publish_time <= tm_now).filter(GoodsMember.is_v == 1).first()
    if goods_count: goods_count = goods_count[0]
    else: goods_count = 0
    DBSession.close()
    return goods_count


