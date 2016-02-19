# -*- coding:utf-8 -*-

from hichao.util.statsd_client import timeit
from sqlalchemy import (
        func,
        Column,
        INTEGER,
        VARCHAR,
        TEXT,
        DateTime,
        TIMESTAMP,
    )
from sqlalchemy.dialects.mysql import (
        TINYINT,
    )
from hichao.flash_sale.models.db import (
        rdbsession_generator,
        Base,
    )

from hichao.base.models.base_component import BaseComponent
import datetime
from hichao.cache.cache import deco_cache

timer = timeit('hichao_backend.m_flash_sale')

FLASH_SALE_END = '已结束'
FLASH_SALE_END_STATE = '0'
FLASH_SALE_NOW = '抢购中'
FLASH_SALE_NOW_SKU = '参加抢购'
FLASH_SALE_NOW_STATE = '1'
FLASH_SALE_NOSTART = '即将开始'
FLASH_SALE_NOSTART_STATE = '2'

class FlashSale(Base,BaseComponent):
    __tablename__ = 'flash_sale'
    id = Column(INTEGER, primary_key = True)
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    publish_datetime = Column(DateTime)
    user_name = Column(VARCHAR(32))
    review = Column(TINYINT)

    def get_flash_sale_tag(self):
        data = {}
        data['tag_value'] = self.start_datetime
        #datetime.strftime('%y-%m-%d %I:%M:%S %p')
        data['tag_time'] = self.start_datetime.strftime('%H:%M')
        return data

@timer
@deco_cache(prefix = 'flash_sale_tags', recycle = 60)
def get_flash_sale_tags_from_db( use_cache = True):
    ''' 从数据库 中获得今天的闪购标签 '''
    DBSession = rdbsession_generator()
    today_year = datetime.datetime.now().year
    today_month = datetime.datetime.now().month
    today_day = datetime.datetime.now().day
    today_start = datetime.datetime( today_year, today_month, today_day) 
    today_end = today_start + datetime.timedelta(days = 1)
    flashsale = DBSession.query(FlashSale).order_by(FlashSale.start_datetime.asc()).filter(FlashSale.review == 1).filter(FlashSale.start_datetime >= today_start).filter(FlashSale.start_datetime < today_end).all()
    DBSession.close()
    return flashsale

@timer
def build_flash_sale_tag(tag_obj):
    ''' 生成每个时间标签的数据  '''
    data = {}
    data['tag_time'] = tag_obj.start_datetime.strftime('%H:%M')
    data['flash_sale_id'] = str(tag_obj.id)
    if tag_obj.start_datetime < datetime.datetime.now():
        data['tag_value'] = FLASH_SALE_END
        data['state'] = FLASH_SALE_END_STATE
    elif tag_obj.start_datetime == datetime.datetime.now():
        data['tag_value'] = FLASH_SALE_NOW
        data['state'] = FLASH_SALE_NOW_STATE
    else:
        data['tag_value'] = FLASH_SALE_NOSTART
        data['state'] = FLASH_SALE_NOSTART_STATE
    return data

@timer
def build_flash_sale_tag_with_endtime(tag_obj):
    ''' 生成每个时间标签的数据  使用结束时间'''
    data = {}
    data['tag_time'] = tag_obj.start_datetime.strftime('%H:%M')
    data['flash_sale_id'] = str(tag_obj.id)
    if not tag_obj.end_datetime:
        return {}
    if tag_obj.end_datetime < datetime.datetime.now():
        data['tag_value'] = FLASH_SALE_END
        data['state'] = FLASH_SALE_END_STATE
        data['expires'] = '0'
    elif tag_obj.start_datetime > datetime.datetime.now():
        data['tag_value'] = FLASH_SALE_NOSTART
        data['state'] = FLASH_SALE_NOSTART_STATE
        data['expires'] = get_flash_sale_expires(tag_obj.start_datetime)
    else:
        data['tag_value'] = FLASH_SALE_NOW
        data['state'] = FLASH_SALE_NOW_STATE
        data['expires'] = get_flash_sale_expires(tag_obj.end_datetime)
    return data

@timer
def get_flash_sale_expires(tag_time):
    ''' 获得距离开团的时间 或 结束时间'''
    now_time = datetime.datetime.now()
    time_num = '0'
    if tag_time > now_time :
        result_time = tag_time - now_time
        time_num = result_time.total_seconds()
        if time_num > 0:
            time_num = str(int(time_num))
        else:
            time_num = '0'
    return time_num


@timer
def get_flash_sale_tags_info():
    ''' 获得 闪购时间标签 list  '''
    items = get_flash_sale_tags_from_db()
    tag_value = FLASH_SALE_END
    data = []
    for item in items:
        tag = build_flash_sale_tag(item)
        if tag['tag_value'] == FLASH_SALE_NOW:
            tag_value = FLASH_SALE_NOW
        elif tag_value == FLASH_SALE_END and tag['tag_value'] == FLASH_SALE_NOSTART:
            if len(data) >= 1:
                data[-1]['tag_value'] = FLASH_SALE_NOW
                data[-1]['state'] = FLASH_SALE_NOW_STATE
            tag_value = FLASH_SALE_NOW
                
        tag['expires'] = get_flash_sale_expires(item.end_datetime)
        data.append(tag)
    for temp in data:
        if temp['tag_value'] == FLASH_SALE_END:
            temp['expires'] = '0'
	
    if data:
        if data[-1]['tag_value'] == FLASH_SALE_END:
            data[-1]['tag_value'] = FLASH_SALE_NOW
            data[-1]['state'] = FLASH_SALE_NOW_STATE
        tag = build_flash_sale_tag_with_endtime(items[-1])
        if tag:
            tag['expires'] = get_flash_sale_expires(item.end_datetime)
            data[-1]=tag

    return data

@timer
def get_flash_sale_tags_info_with_endtime():
    ''' 获得 闪购时间标签 list  使用结束时间'''
    items = get_flash_sale_tags_from_db()
    tag_value = FLASH_SALE_END
    data = []
    for item in items:
        '''
        #全部使用开始时间和结束时间
        tag = build_flash_sale_tag_with_endtime(item)
        if not tag:
            continue
        if (tag_value == FLASH_SALE_NOW and tag['tag_value'] == FLASH_SALE_NOW) or (tag_value == FLASH_SALE_END and tag['tag_value'] == FLASH_SALE_NOSTART):
            tag_value = tag['tag_value']
            if len(data) >= 1:
                data[-1]['tag_value'] = FLASH_SALE_NOW
                data[-1]['state'] = FLASH_SALE_NOW_STATE
                tag['expires'] = '0'
        if tag['tag_value'] == FLASH_SALE_NOW:
            tag_value = FLASH_SALE_NOW
        '''
        #最后一条使用开始时间和结束时间 其他使用结束时间
        if item != items[-1]:
            tag = build_flash_sale_tag(item)
        else:
            tag = build_flash_sale_tag_with_endtime(item)
            if tag:
                tag['expires'] = get_flash_sale_expires(item.end_datetime)
        data.append(tag)
    return data

@timer
def get_flashsale_status_by_flashsale_id(flashsale_id):
    data = get_flash_sale_tags_info()
    for item in data:
        if item['flash_sale_id'] == str(flashsale_id):
            return item['state']
    return '0'
        
@timer
def get_flashsale_id_now_state():
    data = get_flash_sale_tags_info()
    for item in data:
        if item['state'] == str(FLASH_SALE_NOW_STATE):
            return item
    if len(data) >= 1:
        if data[0]['state'] == FLASH_SALE_NOSTART_STATE:
            return data[0]
        else:
            return data[-1]
    else:
        return ''

