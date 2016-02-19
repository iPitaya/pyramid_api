# -*- coding:utf-8 -*-

from hichao.util.statsd_client import timeit
from sqlalchemy import (
    Column,
    INTEGER,
    VARCHAR,
    BIGINT,
    func,
    DateTime,
)
from hichao.timeline.models.db import (
    rdbsession_generator,
    Base,
)
from hichao.base.models.base_component import BaseComponent
from hichao.base.config import (
    FALL_PER_PAGE_NUM,
    MYSQL_MAX_INT,
)
from hichao.util.date_util import (
    get_date_attr,
    format_digital,
    ZHOU_DICT,
    WEEK_DICT,
)
from hichao.util.formatter import format_hour_minutes
from hichao.star.models.star import get_star_by_star_id
from hichao.sku.models.sku import get_sku_by_id
from hichao.drop.models.drop import get_drop_by_id
from hichao.tuangou.models.tuangouinfo import get_tuangou_by_id
from hichao.forum.models.thread import get_thread_by_id
from hichao.timeline.models.showlist_flow import get_flow_by_id
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE
import datetime

timer = timeit('hichao_backend.m_timeline')
timer_mysql = timeit('hichao_backend.m_timeline.mysql')


class TIME_LINE:
    STAR = 1
    SKU = 2
    STAR_V35 = 3
    WORTH_SKU = 4
    SHOP = 5
    SKU_V60 = 6


class TimeLineUnit(BaseComponent):
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    type_id = Column(INTEGER)
    type = Column(VARCHAR(64), nullable=False)
    power = Column(INTEGER, nullable=False)
    publish_date = Column(BIGINT, nullable=True)

    def __init__(self, id, type_id, type, power, publish_date):
        self.id = id
        self.type = type
        self.type_id = type_id
        self.power = power
        self.publish_date = publish_date

    def get_component_id(self):
        return str(self.id)

    def get_bind_drop(self):
        return None

    def get_component_height(self):
        obj = self.get_bind_drop()
        if obj:
            return obj.get_component_height()
        else:
            return '150'

    def get_component_width(self):
        obj = self.get_bind_drop()
        if obj:
            return obj.get_component_width()
        else:
            return '100'

    def get_component_publish_date(self):
        return self.publish_date

    def get_component_year(self):
        return format_digital(get_date_attr(self.publish_date, 'tm_year'))

    def get_component_year_short(self):
        return format_digital(int(self.get_component_year()) % 100)

    def get_component_month(self):
        return '{0}/{1}'.format(format_digital(get_date_attr(self.publish_date, 'tm_mon')), int(self.get_component_year()) % 100)

    def get_component_month_only(self):
        return format_digital(get_date_attr(self.publish_date, 'tm_mon'))

    def get_component_day(self):
        return format_digital(get_date_attr(self.publish_date, 'tm_mday'))

    def get_component_week_day(self):
        weekday = get_date_attr(self.publish_date, 'tm_wday')
        return ZHOU_DICT[weekday]

    def get_component_show_time(self):
        return format_hour_minutes(get_date_attr(self.publish_date, 'tm_hour'), get_date_attr(self.publish_date, 'tm_min'))

    def get_component_pic_url(self):
        obj = self.get_bind_drop()
        if obj:
            return self.get_bind_drop().get_component_pic_url()
        else:
            return ''

    def get_component_drop_pic_url(self):
        obj = self.get_bind_drop()
        if obj:
            method = getattr(obj, 'get_component_drop_pic_url', obj.get_component_pic_url)
            return method()
        else:
            return ''

    def get_drop_type(self):
        drop = self.get_bind_drop()
        if drop:
            x = getattr(drop, 'get_component_type', '')
            if x:
                return x()
            else:
                return x
        else:
            return ''

    def get_component_type(self):
        return self.type

    def get_component_type_id(self):
        return self.type_id

    def get_component_xingqi(self):
        weekday = get_date_attr(self.publish_date, 'tm_wday')
        return WEEK_DICT[weekday]

    def to_ui_action(self):
        obj = self.get_bind_drop()
        if obj:
            return self.get_bind_drop().to_ui_action()
        else:
            return {}


class StarTimeLine(Base, TimeLineUnit):
    __tablename__ = 'test7'

    def get_bind_drop(self):
        obj = None
        if self.type == 'star':
            obj = get_star_by_star_id(self.type_id)
        elif self.type == 'drop' or self.type == 'timedrop':
            obj = get_drop_by_id(self.type_id)
        return obj


class SkuTimeLine(Base, TimeLineUnit):
    __tablename__ = 'sku_list'

    def get_bind_drop(self):
        obj = None
        if self.type == 'sku' or self.type == 'timesku':
            obj = get_sku_by_id(self.type_id)
        return obj


class SkuTimeLineV60(Base, TimeLineUnit):
    __tablename__ = 'sku_list_v6_0'

    category_id = Column(INTEGER, nullable=False)

    def get_bind_drop(self):
        obj = None
        if self.type == 'sku' or self.type == 'timesku':
            obj = get_sku_by_id(self.type_id)
        return obj


class ShopTimeLine(Base, TimeLineUnit):
    __tablename__ = 'mall_sku'

    def get_bind_drop(self):
        obj = None
        if self.type == 'sku' or self.type == 'timesku':
            obj = get_sku_by_id(self.type_id)
        return obj


class StarTimeLineV35(Base, TimeLineUnit):
    __tablename__ = 'showlist_v3_5'

    def get_bind_drop(self):
        obj = None
        if self.type == 'star':
            obj = get_star_by_star_id(self.type_id)
        elif self.type == 'drop' or self.type == 'timedrop':
            obj = get_drop_by_id(self.type_id)
        elif self.type == 'timetuan':
            obj = get_tuangou_by_id(self.type_id)
        elif self.type == 'thread':
            obj = get_thread_by_id(self.type_id)
        elif self.type == 'flow':
            obj = get_flow_by_id(self.type_id)
        return obj

    def to_ui_action(self):
        obj = self.get_bind_drop()
        if obj:
            if self.type == 'thread':
                return obj.to_lite_ui_action()
            return obj.to_ui_action()
        else:
            return {}


class WorthSkuTimeLine(Base, TimeLineUnit):
    __tablename__ = 'worth_sku'

    def get_bind_drop(self):
        obj = None
        if self.type == 'sku' or self.type == 'timesku':
            obj = get_sku_by_id(self.type_id)
        return obj


class DailyHotSaleTimeLine(Base):
    __table_args__ = {"schema": "wodfan"}
    __tablename__ = 'hot_sku_recommend'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    sku_id = Column(INTEGER)
    power = Column('pos', INTEGER, nullable=False)
    sale_time = Column(DateTime, nullable=True)
    ts = Column(DateTime, nullable=True)
    review = Column(INTEGER, nullable=False)
    sale_number = Column(INTEGER, nullable=False)
    shop_prize = Column('shop_price', VARCHAR(32), nullable=False)


@timer
@deco_cache(prefix='time_line', recycle=MINUTE)
@timer_mysql
def get_time_line_units_by_power(power=MYSQL_MAX_INT, per_page=FALL_PER_PAGE_NUM, _type=TIME_LINE.STAR):
    cls = get_cls_by_type(_type)
    DBSession = rdbsession_generator()
    time_line_units = DBSession.query(cls).filter(cls.power < power).order_by(cls.power.desc()).limit(per_page).all()
    DBSession.close()
    return time_line_units


@timer
@deco_cache(prefix='time_line_by_cates', recycle=MINUTE)
@timer_mysql
def get_time_line_units_by_cate_ids(category_ids, power=MYSQL_MAX_INT, per_page=FALL_PER_PAGE_NUM, _type=TIME_LINE.STAR):
    cls = get_cls_by_type(_type)
    DBSession = rdbsession_generator()
    time_line_units = DBSession.query(cls).filter(cls.power < power, cls.category_id.in_(category_ids)).order_by(cls.publish_date.desc()).limit(per_page).all()
    DBSession.close()
    return time_line_units


def get_cls_by_type(_type):
    if _type == TIME_LINE.STAR:
        return StarTimeLine
    elif _type == TIME_LINE.STAR_V35:
        return StarTimeLineV35
    elif _type == TIME_LINE.SKU:
        return SkuTimeLine
    elif _type == TIME_LINE.SHOP:
        return ShopTimeLine
    elif _type == TIME_LINE.SKU_V60:
        return SkuTimeLineV60
    else:
        return WorthSkuTimeLine


@timer
@deco_cache(prefix='timeline_unit', recycle=MINUTE)
@timer_mysql
def get_timeline_unit_by_type_id(type, id, use_cache=True):
    cls = get_cls_by_type(type)
    DBSession = rdbsession_generator()
    timeline_unit = DBSession.query(cls).filter(cls.id == int(id)).first()
    DBSession.close()
    return timeline_unit


@timer
@deco_cache(prefix='timeline_unit_drop_type', recycle=MINUTE)
@timer_mysql
def get_droptype_by_timeline_type_id(type, id):
    unit = get_timeline_unit_by_type_id(type, id)
    return unit.get_drop_type() if unit else 'unknow'


@timer
@deco_cache(prefix='daily_hotsale_unit', recycle=MINUTE)
def get_daily_hotsale_unit_by_type_id(tag_type, power, per_page=FALL_PER_PAGE_NUM, asc=1):
    offset = int(power)
    cls = DailyHotSaleTimeLine
    today_year = datetime.datetime.now().year
    today_month = datetime.datetime.now().month
    today_day = datetime.datetime.now().day
    today_start = datetime.datetime(today_year, today_month, today_day)
    today_end = today_start + datetime.timedelta(days=1)
    DBSession = rdbsession_generator()
    tiaojian = getattr(cls, 'power').desc()
    if tag_type == 'all':
        tiaojian = getattr(cls, 'power').desc()
    if tag_type == 'new':
        tiaojian = getattr(cls, 'sale_time').desc()
    if tag_type == 'sale':
        asc = 0  # 兼容ios bug
        if str(asc) == '1':
            tiaojian = getattr(cls, 'sale_number').asc()
        else:
            tiaojian = getattr(cls, 'sale_number').desc()
    if tag_type == 'price':
        if str(asc) == '1':
            tiaojian = (getattr(cls, 'shop_prize') * 1).asc()
        else:
            tiaojian = (getattr(cls, 'shop_prize') * 1).desc()
    time_line_units = DBSession.query(cls).filter(cls.ts >= today_start).filter(cls.ts < today_end).filter(cls.review == 1).order_by(tiaojian).offset(offset).limit(per_page).all()
    DBSession.close()
    return time_line_units
