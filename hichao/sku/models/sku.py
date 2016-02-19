# -*- coding:utf-8 -*-

from hichao.util.statsd_client import timeit
from sqlalchemy import (
    Column,
    BIGINT,
    VARCHAR,
    DECIMAL,
    TEXT,
    INTEGER,
    TIMESTAMP,
)
from sqlalchemy.dialects.mysql import TINYINT
from hichao.sku.models.db import (
    slave_dbsession_generator,
    dbsession_generator,
    Base,
    mongo_sku_img_table,
)
from hichao.base.config.ui_action_type import SKU_DETAIL
from hichao.base.config.ui_component_type import SKU_CELL
from hichao.base.config import FAKE_ACTION, NATIONAL_FLAG_URL
from hichao.base.models.base_component import BaseComponent
from hichao.util.image_url import (
    build_sku_normal_image_url,
    build_sku_small_image_url,
    get_item_small_path,
    get_item_normal_path,
    build_sku_origin_image_url,
    build_nationalflag_image_url,
)
from hichao.util.formatter import format_price
from hichao.util.cps_util import (
    cps_title_styles_dict,
    get_cps_url,
    get_cps_source_name,
    get_cps_source_img,
    get_cps_key,
    CpsType,
)
from hichao.util.date_util import HOUR, DAY, FIVE_MINUTES, WEEK
from hichao.util.short_url import generate_short_url
from hichao.cache.cache import (
    deco_cache,
    deco_cache_m,
)
from hichao.collect.models.collect import Collect
#from hichao.sku.models.spider_sku import get_info_from_sku_source_source_id
from hichao.sku.models.brand import get_brand_by_id
from hichao.sku.config import SKU_PV_PREFIX, SKU_UV_PREFIX
from hichao.sku.models.sku_size import get_size_by_sku_id
from hichao.base.lib.redis import redis
from hichao.base.config import BUTIE_ICON
from hichao.util.obj2dict import obj2dict
from hichao.shop.models.activity_info import (
    has_valid_activitys,
    get_activity_by_id,
)
from icehole_client.sku_sku import SkuThriftClient
from icehole_client.files_client import get_filename as get_img_file
from icehole_client.shop_sku_client import ShopSkuInfoClient
from hc.redis.count import Counter, SetCounter
from icehole_client.files_client import get_image_filename
from ice_client import ClientFactory, HiExc
from hichao.util.image_url import (
    build_ec_event_icon_image_url,
    build_evaluation_image_url,
)
from hichao.base.config import SOLD_OUT
from hichao.util.sku_info import (
    get_sku_info_from_ecshop_by_source_ids,
    get_sku_country_info,
    get_sku_country_info_new,
    get_sku_activity_info_by_goods_id,
)
import transaction
import datetime
import time
import requests
import json
import socket
from random import randint
import uuid

IMAGE_FILENAME_SPACE = 'backend_images'
timer = timeit('hichao_backend.m_sku')


class Sku(Base, BaseComponent, dict):
    __tablename__ = 'sku'
    sku_id = Column(BIGINT, primary_key=True, index=True, unique=True)
    url = Column(VARCHAR(256), nullable=False)
    detail_url = Column(VARCHAR(256), nullable=False)
    curr_price = Column(DECIMAL(20, 2), nullable=False)
    title = Column(TEXT, nullable=False)
    sales = Column(INTEGER, nullable=False, default=0)
    source = Column(VARCHAR(256), nullable=False)
    link = Column(VARCHAR(1024), nullable=False)
    source_id = Column(VARCHAR(256), nullable=False)
    description = Column(TEXT, nullable=True)
    favor = Column(INTEGER, nullable=False, default=0)
    publish_date = Column(TIMESTAMP)
    is_recommend = Column(INTEGER)
    review = Column(INTEGER)
    came_from = Column('from', VARCHAR)
    tags = Column(VARCHAR)
    height = Column(INTEGER)
    width = Column(INTEGER)
    brand_id = Column(INTEGER)
    sku_type = Column(TINYINT)
    intro = Column(VARCHAR(255))
    origin_price = Column(DECIMAL(20, 2))
    b_color = Column(VARCHAR(128))

    def __init__(self):
        pass

    def get_component_id(self):
        return str(self['sku_id'])

    def get_component_pic_url(self):
        return self.get_normal_pic_url()

    def get_component_common_pic_url(self):
        return self.get_component_pic_url()

    def get_component_price(self):
        return format_price(self['curr_price'])

    def get_component_orig_price(self):
        return format_price(self['origin_price'])

    def get_component_active_price(self):
        return format_price(self['active_price'])

    def get_component_width(self):
        image_size = self.get_component_width_and_height()
        if str(image_size.width) != '0':
            return str(image_size.width)
        is_mongo_sku = 0
        try:
            int(self['sku_id'])
        except:
            is_mongo_sku = 1
        size = None
        if not is_mongo_sku:
            size = get_size_by_sku_id(self['sku_id'])
        if size:
            if str(size[0]) != '0':
                return str(size[0])
            else:
                return '100'
        else:
            return '100'

    def get_component_height(self):
        image_size = self.get_component_width_and_height()
        if str(image_size.height) != '0':
            return str(image_size.height)
        is_mongo_sku = 0
        try:
            int(self['sku_id'])
        except:
            is_mongo_sku = 1
        size = None
        if not is_mongo_sku:
            size = get_size_by_sku_id(self['sku_id'])
        if size:
            if str(size[1]) != '0':
                return str(size[1])
            else:
                return '100'
        else:
            return '100'

    def get_component_width_and_height(self):
        url = self['detail_url']
        if not url:
            url = self['url']
        image_size = get_image_filename(IMAGE_FILENAME_SPACE, url)
        return image_size

    def get_normal_pic_url(self):
        if self['url'].startswith('http'):
            return self['url']
        support_webp = self.get('support_webp', 0)
        return build_sku_normal_image_url(get_img_file(IMAGE_FILENAME_SPACE, get_item_normal_path(self['url'])), support_webp)

    def get_small_pic_url(self):
        if self['url'].startswith('http'):
            return self['url']
        support_webp = self.get('support_webp', 0)
        return build_sku_small_image_url(get_img_file(IMAGE_FILENAME_SPACE, self['url']), support_webp)

    def get_origin_pic_url(self):
        if self['url'].startswith('http'):
            return self['url']
        support_webp = self.get('support_webp', 0)
        url = self['detail_url']
        if not url:
            url = self['url']
        return build_sku_origin_image_url(get_img_file(IMAGE_FILENAME_SPACE, url), support_webp)

    def get_component_description(self):
        if self['title']:
            return self['title']
        else:
            return ''

    def get_component_short_description(self):
        desc = unicode(self['title'])
        if len(desc) > 25:
            return desc[0:25] + '...'
        else:
            return desc

    def get_collection_id(self):
        return self['sku_id']

    def get_collection_type(self):
        return 'sku'

    def get_channel_url(self):
        return get_cps_source_img(self['source'], self['link'])

    def get_channel_name(self):
        return get_cps_source_name(self['source'], self['link'])

    def get_taobaoke_url(self):
        if self.is_brand():
            return self['link']
        url = ''
        try:
            #cps_type = getattr(self, 'cps_type', CpsType.IPHONE)
            cps_type = self.get('cps_type', CpsType.IPHONE)
            url = get_cps_url(self['source'], self['source_id'], self.get_bind_info(), cps_type)
        except Exception, ex:
            print Exception, ex
            print 'get taobaoke failed, source_id is:', self['source_id']
        if not url:
            url = self['link']
        return url.replace('&unid=default', '')

    def get_component_channel(self):
        return self['source']

    def get_bind_info(self):
        return None
        # return get_info_from_sku_source_source_id(self['source'], self['source_id'])

    def get_source_id(self):
        return str(self['source_id'])

    def get_source(self):
        return str(self['source'])

    def is_sold_out(self):
        return self['review'] != 1 and True or False

    def get_unixtime(self):
        if isinstance(self['publish_date'], datetime.datetime):
            return int(time.mktime(self['publish_date'].timetuple()))
        else:
            return int(float(self['publish_date']))

    def is_brand(self):
        if self['sku_type'] == 1:
            return 1
        return 0

    def get_bind_brand(self):
        if self.is_brand():
            brand = get_brand_by_id(self['brand_id'])
            return brand
        return None

    def get_brand_img_url(self):
        brand = self.get_bind_brand()
        if brand:
            return brand.image_url
        return ''

    def get_component_intro(self):
        if self['intro']:
            return self['intro']
        else:
            return ''

    def get_component_orig_link(self):
        return self['link']

    def get_component_title_style(self):
        return cps_title_styles_dict[get_cps_key(self['source'], self['link'])]

    def get_component_title(self):
        if self['title']:
            return self['title']
        else:
            return ''

    def get_component_discount(self):
        if not self['origin_price']:
            self['origin_price'] = self['curr_price']
        if self['origin_price'] == self['curr_price']:
            return u'不打折'
        elif float(self['curr_price']) / float(self['origin_price']) > 9.99:
            return '不打折'
        discount = format(float(10.0 * self['curr_price']) / float(self['origin_price']), '.2')
        if float(discount) == 10.0:
            discount = format(10.0 * self['curr_price'] / self['origin_price'], '.3')
        return '{0}折'.format(discount)

    def get_component_pv(self):
        pv_key = SKU_PV_PREFIX.format(self['sku_id'])
        pv_counter = Counter(redis)
        cnt = pv_counter._byID(pv_key)
        if not cnt:
            cnt = 0
        return str(cnt)

    def get_component_uv(self):
        uv_key = SKU_UV_PREFIX.format(self['sku_id'])
        uv_counter = SetCounter(redis, uv_key)
        cnt = uv_counter.count
        if not cnt:
            cnt = 0
        return str(cnt)

    def has_allowance(self):
        return self.get('_has_allowance', 0)

    def has_event(self):
        return 1 if self.get('activity_id', 0) else 0

    def get_bind_event(self):
        if not self.has_event():
            return None
        return get_activity_by_id(self['activity_id'])

    def get_sku_state_msg(self):
        result = ""
        if self['source'] == 'ecshop':
            if self['review'] != 1:
                result = u"已售磬"
        return result

    def get_sku_state_info(self):
        ''' 获得国家信息 返回结果 {'country':'','flag':''}'''
        result = {'country': '', 'flag': ''}
        if self.get('business_id', 0):
            result = get_sku_country_info_new(self['business_id'])
        if not result:
            result = {'country': '', 'flag': ''}
        return result

    def get_ecshop_sku_info(self):
        source_id = self['source_id']
        items = get_sku_info_from_ecshop_by_source_ids(str(source_id))
        result = {}
        if items:
            result = items[0]
        return result

    def get_component_event_icon(self):
        icon = ''
        if self['source'] == 'ecshop':
            if self.has_event():
                activity = self.get_bind_event()
                if activity:
                    icon = activity.get_component_event_icon()
            else:
                icon = self.get_component_allowance_pic_url()
        return icon

    def get_component_allowance_pic_url(self):
        pic_url = ''
        if self.has_allowance():
            pic_url = BUTIE_ICON
        return pic_url

    def to_ui_action(self):
        if self['source'] == 'ecshop' and not self.get('support_ec', ''):
            return FAKE_ACTION
        if self.get('lite_action', ''):
            return self.to_lite_ui_action()
        action = {}
        action['actionType'] = SKU_DETAIL
        action['price'] = self.get_component_price()
        action['originLink'] = self.get_component_orig_link()
        action['link'] = self.get_taobaoke_url()
        action['id'] = self.get_component_id()
        action['unixtime'] = self.get_unixtime()
        action['normalPicUrl'] = self.get_origin_pic_url()
        action['channelPicUrl'] = self.get_channel_url()
        action['source'] = self.get_channel_name()
        action['source_id'] = self.get_source_id()
        action['channel'] = self.get_component_channel()
        action['titleStyle'] = self.get_component_title_style()
        if self.is_brand():
            action['brandPicUrl'] = self.get_brand_img_url()
            action['description'] = self.get_component_intro()
        else:
            action['description'] = self.get_component_title()
        action['shareAction'] = self.get_share_action()
        action['main_image'] = '0'
        return action

    def get_share_action(self):
        share = {}
        share['actionType'] = 'share'
        share_action = {}
        share_action['shareType'] = 'webpage'
        share_action['title'] = '分享个宝贝给你'
        share_action['typeId'] = self.get_component_id()
        share_action['type'] = 'sku'
        share_action['description'] = self.get_component_description()
        share_action['trackValue'] = '{0}_{1}'.format(share_action['type'], share_action['typeId'])
        share_action['picUrl'] = self.get_small_pic_url()
        share_action['detailUrl'] = self.get_taobaoke_url()
        # try:
        #    share_action['detailUrl'] = generate_short_url(self.get_taobaoke_url())
        # except Exception, ex:
        #    print Exception, ex
        #    print 'generate short url error. sku_id:', self['sku_id']
        #    share_action['detailUrl'] = self.get_taobaoke_url()
        share['share'] = share_action
        return share

    def to_lite_ui_action(self):
        if self['source'] == 'ecshop' and not self.get('support_ec', ''):
            return FAKE_ACTION
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'sku'
        action['id'] = self.get_component_id()
        action['source'] = self.get_source()
        action['sourceId'] = self.get_source_id()
        action['width'] = self.get_component_width()
        action['height'] = self.get_component_height()
        action['main_image'] = '0'
        return action

    def to_worthy_sku_action(self):
        if int(self['review']) < 0:
            return {}
        if self['source'] == 'ecshop' and not self.get('support_ec', ''):
            return FAKE_ACTION
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'worthySku'
        action['id'] = self.get_component_id()
        action['source'] = self.get_source()
        action['sourceId'] = self.get_source_id()
        action['width'] = self.get_component_width()
        action['height'] = self.get_component_height()
        return action


def add_sku(sku_id, url, curr_price, title, sales, source, link, source_id, height, width, is_recommend, review,
            description, came_from, tags, detail_url='', brand_id=0, sku_type=0, intro='', b_color='', origin_price=0):
    sku = Sku()
    sku.sku_id = sku_id
    sku.url = url
    sku.curr_price = curr_price
    sku.title = title
    sku.sales = sales
    sku.source = source
    sku.link = link
    sku.source_id = source_id
    sku.height = height
    sku.width = width
    sku.is_recommend = is_recommend
    sku.review = review
    sku.description = description
    sku.came_from = came_from
    sku.tags = tags
    sku.detail_url = detail_url
    sku.brand_id = brand_id
    sku.sku_type = sku_type
    sku.intro = intro
    sku.b_color = b_color
    sku.origin_price = origin_price
    sku.publish_date = datetime.datetime.now()

    try:
        DBSession = dbsession_generator()
        DBSession.add(sku)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ':', ex
        return 0
    finally:
        DBSession.close()
    return 1


def update_sku(sku):
    try:
        DBSession = dbsession_generator()
        #DBSession.query(Sku).filter(Sku.sku_id == sku.sku_id).update({Sku.url:sku.url, Sku.price:sku.price, Sku.price:sku.price})
        DBSession.add(sku)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print 'update_sku error'
        print Exception, ':', ex
        return 0
    finally:
        DBSession.close()
    return 1


def delete_sku(sku_id):
    try:
        DBSession = dbsession_generator()
        DBSession.query(Sku).filter(Sku.sku_id == sku_id).delete()
    except Exception, ex:
        DBSession.rollback()
        print Exception, ':', ex
        return 0
    finally:
        DBSession.close()
    return 1


@timer
def _get_sku_by_id(sku_id):
    DBSession = slave_dbsession_generator()
    sku = DBSession.query(Sku).filter(Sku.sku_id == sku_id).first()
    DBSession.close()
    return sku


@timer
def get_sku_from_icehole(sku_id):  # 现在瀑布流的价格,专题单品单出一个函数
    thrift_client = SkuThriftClient()
    # 调用的thrift
    _sku = thrift_client.get_sku_dict([str(sku_id), ])
    try:
        if _sku:
            if _sku[0]['source'] == 'ecshop':
                global_id = str(uuid.uuid1())
                goods_price_client = ClientFactory.create('goods_price')
                # 调用的ice
                _sku[0]['activity_id'] = 0
                _sku_price_with_activity_raw = goods_price_client.getGoodsPriceWithPreheat(global_id, str(_sku[0]['goods_id']))
                _sku_price_with_activity = json.loads(_sku_price_with_activity_raw)
                if str(_sku_price_with_activity['code']) == '0' and _sku_price_with_activity['data']['goods']:
                    sku_price_data = _sku_price_with_activity['data']['goods'][0]
                    _sku[0]['sales'] = sku_price_data['sale_num']
                    _sku[0]['origin_price'] = format_price(sku_price_data['origin_price'])
                    _sku[0]['curr_price'] = format_price(sku_price_data['active_price'])
                    # active_price活动没有开始,就是shop_price,活动开始就是取得实际的活动价格
                    if sku_price_data['active_id'] != 0:
                        _sku[0]['activity_id'] = sku_price_data['active_id']
                    if sku_price_data['img_falls']:
                        _sku[0]['eventIcon'] = build_evaluation_image_url(sku_price_data['img_falls'], 'backend_images')
    except Exception, ex:
        print Exception, ex
    finally:
        return _sku


@timer
def get_topic_sku_from_icehole(sku_id):  # 现在瀑布流的价格,专题单品单出一个函数
    thrift_client = SkuThriftClient()
    # 调用的thrift
    _sku = thrift_client.get_sku_dict([str(sku_id), ])
    try:
        if _sku:
            if _sku[0]['source'] == 'ecshop':
                global_id = str(uuid.uuid1())
                goods_price_client = ClientFactory.create('goods_price')
                # 调用的ice
                _sku[0]['activity_id'] = 0
                goods_info_detail_raw = goods_price_client.getGoodsInfoDetail(global_id, str(_sku[0]['goods_id']))
                goods_info_detail = json.loads(goods_info_detail_raw)
                if str(goods_info_detail['code']) == '0':
                    goods_info_detail_data = goods_info_detail['data']
                    _sku[0]['origin_price'] = format_price(goods_info_detail_data['goods'][0]['origin_price'])
                    _sku[0]['curr_price'] = format_price(goods_info_detail_data['goods'][0]['shop_price'])
                    if goods_info_detail_data['rules']:  # 有活动
                        _sku[0]['activity_id'] = goods_info_detail_data['rules'][0]['active_id']
                        start_time = goods_info_detail_data['rules'][0]['start_time']
                        end_time = goods_info_detail_data['rules'][0]['end_time']
                        preheat_time = goods_info_detail_data['rules'][0]['preheat_time']
                        curr_time = time.time()
                        if (curr_time >= preheat_time) and (curr_time < end_time):  # 开始预热且活动没有结束
                            p_price_list = []
                            for product in goods_info_detail_data['goods'][0]['products']:
                                p_price_list.append(float(format_price(product['p_price'])))
                            min_price = p_price_list[0]
                            for p_price in p_price_list:
                                if p_price < min_price:
                                    min_price = p_price
                            _sku[0]['active_price'] = str(min_price)
                        purchase_num = goods_info_detail_data['goods'][0]['products'][0]['purchase_num']
                        sale_num = goods_info_detail_data['goods'][0]['products'][0]['sale_num']
                        if purchase_num and sale_num >= purchase_num:
                            _sku[0]['is_sale_over'] = 1
                        else:
                            _sku[0]['is_sale_over'] = 0
                        if curr_time > end_time:
                            _sku[0]['is_end'] = 1
                        else:
                            _sku[0]['is_end'] = 0
    except Exception, ex:
        print Exception, ex
    finally:
        return _sku


@timer
def get_allowance_from_icehole(source_id):
    client = ShopSkuInfoClient()
    allowance_sku = None
    try:
        allowance_sku = client.get_allowance_sku_by_source_id(source_id)
    except:
        return None
    return allowance_sku


@timer
def get_ecskus_by_source_id(source_ids):
    DBSession = slave_dbsession_generator()
    skus = DBSession.query(Sku).filter(Sku.source == 'ecshop').filter(Sku.source_id.in_(source_ids)).all()
    skus = [sku2dict(sku) for sku in skus]
    DBSession.close()
    return skus


@timer
#@deco_cache(prefix = 'sku', recycle = HOUR)
def get_sku_by_id(sku_id, use_cache=True):
    _sku = get_sku_from_icehole(sku_id)
    sku = None
    if _sku:
        sku = Sku()
        sku.update(_sku[0])
    if sku and sku['source'] == 'ecshop':
        allowance_sku = {}
        if str(sku['source_id']).isdigit():
            source_id = int(sku['source_id'])
            allowance_sku = get_allowance_from_icehole(source_id)
            if allowance_sku and allowance_sku.source_id:
                sku['_has_allowance'] = 1
                allowance_sku = obj2dict(allowance_sku)
            else:
                allowance_sku = {}
        sku.update(allowance_sku)
    return sku


# 因为专题中价格的展示逻辑和瀑布流不一样,所以单独出一个函数
@timer
def get_topic_sku_by_id(sku_id, use_cache=True):
    _sku = get_topic_sku_from_icehole(sku_id)
    sku = None
    if _sku:
        sku = Sku()
        sku.update(_sku[0])
    if sku and sku['source'] == 'ecshop':
        allowance_sku = {}
        if str(sku['source_id']).isdigit():
            source_id = int(sku['source_id'])
            allowance_sku = get_allowance_from_icehole(source_id)
            if allowance_sku and allowance_sku.source_id:
                sku['_has_allowance'] = 1
                allowance_sku = obj2dict(allowance_sku)
            else:
                allowance_sku = {}
        sku.update(allowance_sku)
    return sku

#@deco_cache(prefix = 'wodfan_sku', recycle = HOUR)


def get_old_sku_by_id(sku_id, use_cache=True):
    return get_sku_by_id(sku_id, use_cache=use_cache)


@deco_cache(prefix='sku_id_by_source_sourceid', recycle=DAY)
def get_sku_id_by_source_sourceid(source, source_id, use_cache=True):
    DBSession = slave_dbsession_generator()
    sku_id = DBSession.query(Sku.sku_id).filter(Sku.source_id == source_id).filter(Sku.source == source).first()
    DBSession.close()
    if not sku_id:
        sku_id = None
    else:
        sku_id = sku_id[0]
    return sku_id


@timer
def get_recommend_sku_ids(offset=0, limit=50, start_time='', end_time=''):
    DBSession = slave_dbsession_generator()
    ids = DBSession.query(Sku.sku_id, Sku.publish_date, Sku.came_from).filter(Sku.publish_date.between(start_time, end_time)).filter(Sku.is_recommend == 1).filter(Sku.review == 1).order_by(Sku.publish_date.desc()).offset(offset).limit(limit)
    DBSession.close()
    return ids


@timer
def get_sku_action_by_sku_id(sku_id):
    sku = get_old_sku_by_id(sku_id)
    if not sku:
        return {}
    action = sku.to_ui_action()
    count = Collect('sku').user_count_by_item(sku_id)
    if not count:
        count = 0
    action['collectionCount'] = str(count)
    return action


@timer
def get_sku_imgs(source, source_id):
    return mongo_sku_img_table.find_one({'source': source, 'source_id': source_id})


@timer
#@deco_cache(prefix = 'sku_ids_by_source_sourceids', recycle = FIVE_MINUTES)
def get_sku_ids_by_source_sourceids(source, source_ids, use_cache=True):
    DBSession = slave_dbsession_generator()
    source_sku_ids = DBSession.query(Sku.source_id, Sku.sku_id, Sku.publish_date).filter(Sku.source_id.in_(source_ids)).filter(Sku.source == source).all()
    DBSession.close()
    return source_sku_ids


@timer
@deco_cache(prefix='sku_cache_by_sourceid', recycle=WEEK)
def get_sku_cache_by_sourceid(source_id, use_cache=True):
    DBSession = slave_dbsession_generator()
    item = DBSession.query(Sku.source_id, Sku.sku_id, Sku.publish_date).filter(Sku.source_id == str(source_id)).first()
    DBSession.close()
    return item


def get_sku_event_icon(source_id, goods_id):
    has_allowance = 0
    source_id = int(source_id)
    allowance_sku = get_allowance_from_icehole(source_id)
    if allowance_sku and allowance_sku.source_id:
        has_allowance = 1
    activity_id = 0
    if has_valid_activitys():                   # 先判断是否有活动，如果没有就没必要再调商城接口。活动规则修改 商家后台可以添加时间
        if goods_id:
            act_sku = get_sku_activity_info_by_goods_id(goods_id)
            if act_sku and act_sku.has_key('active_id'):                    # 这里不使用商城单品活动数据，活动是否有效在sku.get_bind_event方法里做判断。
                activity_id = act_sku['active_id']
    icon = ''
    if activity_id:
        start = time.time()
        activity = get_activity_by_id(activity_id)
        if activity:
            icon = activity.get_component_event_icon()
    else:
        if has_allowance:
            icon = BUTIE_ICON
    return icon


@timer
def get_sku_from_icehole_by_source_id(source_id):
    client = SkuThriftClient()
    return client.get_sku_by_source_source_id(source_id=str(source_id), source='ecshop')


def sku2dict(sku):
    for k, v in sku.__dict__.iteritems():
        sku[k] = v
    return sku
