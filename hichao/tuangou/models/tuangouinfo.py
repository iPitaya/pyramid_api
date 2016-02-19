# -*- coding:utf8 -*-
from hichao.util.statsd_client import statsd
from icehole_client.tuangou_client import (
        get_buying_info_list,
        get_buying_info,
        )
from hichao.base.config import(
        FALL_PER_PAGE_NUM,
        FAKE_ACTION,
        )
from hichao.util.date_util import (
        MINUTE,
        FIVE_MINUTES,
        TEN_MINUTES,
        HOUR,
        DAY,
        )
from hichao.cache.cache import (
        deco_cache,
        )
from hichao.tuangou.models.tuangousku import (
        build_tuangou_sku_by_id,
        build_tuangou_sku_by_id_lite,
        )
from hichao.tuangou.models.image_url import(
        build_tuan_image_url,
        )
from hichao.tuangou.models.attend_util import(
        build_attend_count,
        )
from hichao.base.models.base_component import BaseComponent
from hichao.util.statsd_client import timeit
import time
from hichao.sku.models.sku import get_sku_by_id

timer = timeit('hichao_backend.m_tuangou_tuangouinfo')

@timer
def get_buying_info_datablock_list(item_id, limit=FALL_PER_PAGE_NUM, offset=0, with_main=False, lite_action = 0, support_ec = 1):
    res = get_buying_info_list(item_id, limit, offset)
    data={}
    data['items']=[]
    tuangou = get_buying_info(item_id)
    start_time = str(tuangou.start_date)
    end_time = str(tuangou.end_date)
    server_time = str(int(time.time()))
    for item in res:
        if item.id==-1:
            continue
        new_sku =  get_sku_by_id(item.sku_id)
        item.discount_price = new_sku['curr_price']
        temp = None
        if lite_action == 1 and item.source == "ecshop":
            temp = build_tuangou_sku_by_id_lite(item.id, res = item)
            if temp:
                if temp['component']['tuanState'] == u'已结束' or temp['component']['tuanState'] == u'已售完':
                    temp['component']['action'] = {}
        else:
            temp = build_tuangou_sku_by_id(item.id, res = item)
        if temp:
            if item.source == 'ecshop' and not support_ec:
                temp['component']['action'] = FAKE_ACTION
            data['items'].append(temp)

    if len(res)==FALL_PER_PAGE_NUM:
        data['flag']=str(offset+FALL_PER_PAGE_NUM)

    if with_main == True:
        tuangou_info = build_tuangou_by_tuangou_id(item_id, slide=True)
        if tuangou_info:
            data['main'] = tuangou_info['component']['action']
        else:
            data['main'] = {}

    return data


@timer
def build_component_tuangou(item):
    data = {}
    com = {}
    action = {}
    com['slide'] = ''
    com['type'] = 'tuangou'
    com['componentType'] = 'tuanCell'
    com['id'] = str(item.id)
    com['title'] = item.title
    com['picUrl'] = build_tuan_image_url(item.detail_img_url)
    com['tuanState'] = ""    #待定,需要后面判断吗?
    com['peopleCount'] = ""   #需要野哥做支持,该参数需要放到build_visit_count里面,还是说需要提供一个url接口供前端访问
    com['discount'] = item.discount
    com['endTime'] = str(item.end_date)
    com['startTime'] = str(item.start_date)
    now = time.time()
    if now < item.start_date:
        action = {}
    else:
        action['id'] = str(item.id)
        action['actionType'] = 'tuan'
        action['title'] = item.title
        action['query'] = ""
        action['picUrl'] = build_tuan_image_url(item.scroll_img_url)
        action['description'] = item.description
        action['expires'] = ""
    com['action'] = action
    data['component'] = com
    return data

@timer
def build_action_tuangou(item_id, slide = False):
    data = build_tuangou_by_tuangou_id(item_id, slide = slide)
    if data==None:
        return None
    return data['component']['action']

@timer
@build_attend_count()
@deco_cache(prefix="component_tuangou", recycle = MINUTE)
def build_tuangou_by_tuangou_id(item_id, item=None, use_cache=True, slide=False):
    if not item:
        item = get_buying_info(item_id)
    if item==None or item.id==-1:
        return None
    res = build_component_tuangou(item)
    return res

class Tuangou(BaseComponent):
    def __init__(self, tuan_info):
        self.tuan = tuan_info

    def get_component_width(self):
        return '100'

    def get_component_height(self):
        return '150'

    def get_component_pic_url(self):
        return build_tuan_image_url(self.tuan.hangtag_img_url)

    def to_ui_action(self):
        return build_action_tuangou(self.tuan.id)

@timer
@deco_cache(prefix = 'tuangou', recycle = TEN_MINUTES)
def get_tuangou_by_id(id, use_cache = True):
    tuan = get_buying_info(id)
    if tuan: return Tuangou(tuan)
    return None

