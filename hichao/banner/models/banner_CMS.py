# -*- coding:utf-8 -*-
from icehole_client.promotion_client import PromotionClient
import time
import json
import socket
import datetime
import requests
from hichao.util.image_url import (
    build_CMS_image_url_by_short_url,
    build_CMS_image_url_by_width,
)
from hichao.tuangou.models.tuangouinfo import build_tuangou_by_tuangou_id
from hichao.util.object_builder import (
    build_lite_thread_by_id,
    build_staruser_by_user_id,
    build_topic_list_item_by_id,
)
from hichao.base.config import BUSSINESS_COUNT_URL, BUSSINESS_IDS_URL
from hichao.keywords.models.classes import (
    get_class_two_id,
    get_classes_type_id_by_f_id,
)
from hichao.cache.cache import deco_cache
from hichao.util.formatter import format_price
from hichao.util.date_util import FIVE_MINUTES, DAY
from hichao.util.cms_action_builder import build_action
from icehole_client.files_client import get_image_filename
from hichao.sku.models.sku import get_sku_by_id
from . import cms_promotion_flags
from .cms_promotion_flags import *  # backwards compatible
import random
from hichao.keywords.models.classes import (
    get_classes_item_type_id_by_id,
    get_classes_type_id_by_type,
    )

JUMP_TYPE = ['tuanlist', 'worthylist', 'topiclist', 'starusers', 'jiaocheng', 'shoplist', 'news', 'news_star', 'flashsalelist', 'member', 'tutorial', 'bannerlist']
ITEM_TYPE = ['thread', 'star', 'sku', 'topic', 'user', 'groupsku', 'theme', 'news_detail', 'region', 'dailyTopics']
IMAGE_NAMESPACE = 'backend_images'

CMS_WIDTH_DICT = {
    'home_banner_01': 750,
    'home_banner_02': 750,
    'home_banner_03': 750,
    'home_banner_04': 750,
    'home_banner_05': 750,
    'home_banner_06': 750,
    'mall_banner_01': 750,
    'mall_banner_02': 750,
    'mall_banner_03': 750,
    'home_ad1': 710,
    'home_ad2': 710,
    'home_ad3': 710,
    'home_ad4': 710,
    'mall_ad1': 710,
    'mall_ad2': 710,
    'mall_ad3': 710,
    'mall_ad4': 710,
    'mall_ad5': 710,
    'mall_ad6': 710,
    'mall_ad7': 710,
    'mall_ad8': 710,
    'home_row_ad1': 345,
    'home_row_ad2': 345,
    'mall_grid_left': 314,
    'mall_grid_right_top': 434,
    'mall_grid_right_bottom': 434,
}

# 6.4.0新版首页专区个数
REGION_NUM = '6'


def build_banner_CMS_action(content, actionType):
    '''cms 正常action'''
    action = {}
    action['unixtime'] = content.start_time
    action['actionType'] = actionType
    action['id'] = content.action_value
    action['bannerId'] = str(content.position_id)
    action['title'] = content.title
    return action


def build_banner_detail_action(content, actionType, type_name):
    '''detail页跳转action'''
    if type_name == 'sku':
        return build_action(type_name, content.action_value)
    action = {}
    action['unixtime'] = content.start_time
    action['actionType'] = actionType
    action['type'] = type_name
    action['id'] = content.action_value
    action['bannerId'] = str(content.position_id)
    action['title'] = content.title
    return action


def build_banner_CMS_jump_action(ac_type, actionType, content, child):
    '''jump跳转action'''
    action = {}
    action['type'] = ac_type
    action['actionType'] = actionType
    action['bannerId'] = str(content.position_id)
    action['child'] = child
    return action


def build_banner_CMS_tuan_action(tuan_id=''):
    '''tuan跳转action'''
    action = {}
    if tuan_id:
        tuan_com = build_tuangou_by_tuangou_id(int(tuan_id), slide=True)
        if tuan_com:
            action = tuan_com['component']['action']
    return action


def build_banner_CMS_customer_action():
    action = {}
    action['id'] = '1'
    action['actionType'] = 'customer'
    return action


def build_banner_webview_action(actionType, content, means_type='push'):
    '''webview action'''
    action = {}
    action['actionType'] = actionType
    action['originUrl'] = content.action_value
    action['webUrl'] = content.action_value
    action['title'] = content.title
    action['needLogin'] = '0'
    action['means'] = means_type
    titleStyle = {}
    titleStyle['fontColor'] = "0,0,0,255"
    titleStyle['picUrl'] = "http://m2.pimg.cn/images/images/20150226/f318a2bb-73de-43ab-b602-afcdc8b32447.png"
    titleStyle['text'] = content.title
    action['titleStyle'] = titleStyle
    return action

def build_banner_ec_flashbuy_action(actionType, content, flag):
    action = {}
    action['actionType'] = actionType
    action['active_id'] = content.action_value
    action['active_type'] = '2'
    action['m_active_type'] = flag   # 1 限时抢购 2 光速狗
    return action

def build_topiccategory_action(actionType,content):
    action = {}
    action['actionType'] = actionType
    action['tag'] = content.action_value
    action['type'] = 'topic'
    action['id'] = ''
    return action

def build_banner_CMS_component(componentType, picUrl, action):
    '''封装成component数据 定义广告位的都一致'''
    com = {}
    com['componentType'] = componentType
    com['picUrl'] = picUrl
    com['action'] = action
    return com


@deco_cache(prefix='cms_thread_topic', recycle=FIVE_MINUTES)
def get_component_by_position_flag(flag, componentType='', offset=0, limit=1):
    '''通过 字符串标示获得 component数据结构  帖子和专题列表格式'''
    pc = PromotionClient()
    contents = pc.get_contents_by_flag_ts(flag, time.time(), offset=offset, limit=limit)
    items = []
    if contents:
        for content in contents:
            com = {}
            #com = get_component_by_content(content,componentType)
            type_value = content.action_type.type_value
            if type_value == 'thread':
                com = build_lite_thread_by_id(int(content.action_value), 0, 1)
            if type_value == 'topicDetail':
                com = build_topic_list_item_by_id(int(content.action_value), 1)
            if com:
                items.append(com)
    data = {}
    data['items'] = items
    if len(items) >= limit:
        data['flag'] = offset + len(items)
    return data


def get_component_by_content(contents, componentType=''):
    '''通过 中间件返回的一条条目信息 封装成 component数据'''
    com = {}
    if contents:
        #pc = PromotionClient()
        #cont = pc.get_action_type_by_id(contents.action_type_id)
        cont = contents.action_type
        imgurl = contents.image_url_app
        img_url = ''
        if imgurl:
            img_url = build_CMS_image_url_by_short_url(IMAGE_NAMESPACE, imgurl)
        if cont.type_value in JUMP_TYPE:
            ac_type = 'item'
            if cont.type_value == 'topiclist':
                ac_type = 'thread'
            if cont.type_value == 'news' or cont.type_value == 'news_star':
                ac_type = 'news'
            if cont.type_value == 'member':
                ac_type = 'member'
                cont.type_value = ''
            if cont.type_value == 'tutorial':
                ac_type = 'tutorial'
                cont.type_value = ''
            action = build_banner_CMS_jump_action(ac_type, 'jump', contents, cont.type_value)
        elif cont.type_value in ITEM_TYPE:
            if cont.type_value == 'groupsku':
                action = build_banner_detail_action(contents, 'group', 'sku')
            else:
                if cont.type_value == 'news_detail':
                    action = build_banner_detail_action(contents, 'detail', 'news')
                elif cont.type_value == 'dailyTopics':
                    action = build_banner_detail_action(contents, 'group', 'dailyTopics')
                #elif cont.type_value == 'user':
                #    action = build_banner_detail_action(contents, 'space', 'user')
                else:
                    action = build_banner_detail_action(contents, 'detail', cont.type_value)
        elif cont.type_value == 'tuan':
            action = build_banner_CMS_tuan_action(contents.action_value)
        elif cont.type_value == 'platform_service':
            action = build_banner_CMS_customer_action()
            action['showWelcome'] = '1'
        elif cont.type_value == 'webview':
            action = build_banner_webview_action(cont.type_value, contents)
            share = {}
            share['description'] = action['title']
            share['detailUrl'] = action['webUrl']
            share['picUrl'] = img_url
            share['shareType'] = 'webpage'
            share['title'] = action['title']
            share_action = {}
            share_action['actionType'] = 'share'
            share_action['type'] = 'webpage'
            share_action['share'] = share
            action['shareAction'] = share_action
        elif cont.type_value == 'browser':
            action = build_banner_webview_action('webview', contents, 'browser')
        elif cont.type_value == 'ecTimeToBuy':
            action = build_banner_ec_flashbuy_action('flpurchase', contents, '2')
        elif cont.type_value == 'ecHiGou':
            action = build_banner_ec_flashbuy_action('flpurchase', contents, '1')
        elif cont.type_value == 'topiccategory':
            action = build_topiccategory_action('tag',contents)
        else:
            if cont.type_value == 'nojump':
                action = {}
            else:
                action = build_banner_CMS_action(contents, cont.type_value)
        if action:
            action['post_id'] = str(contents.position_id)
            action['banner_id'] = str(contents.id)
            action['bannerId'] = str(contents.id)
            action['title'] = str(contents.title)
            pc = PromotionClient()
            p_position =  pc.get_position_by_id(contents.position_id)
            action['tab_id'] = ''
            if p_position:
                action['tab_id'] = str(p_position.tab_id)
        com = build_banner_CMS_component(componentType, img_url, action)
        if com:
            com['title'] = contents.title
            if componentType == 'sloganCell':
                region_id = contents.action_value
                count = get_region_num_by_bussiness_ids(region_id, use_cache=True)
                com['text'] = '{0}{1}'.format('今日上新：', int(count) + get_daily_news_num(region_id))
            if componentType == 'region_cell' or componentType =='region_today_cell':
                sku = get_sku_by_id(contents.action_value)
                if sku:
                    com['price'] = format(float(format_price(sku.get('curr_price'))), '.2f')
                    com['origin_price'] = format(float(format_price(sku.get('origin_price'))), '.2f')
                else:
                    com['price'] = ''
                    com['origin_price'] = ''
            com['width'] = '0'
            com['height'] = '0'
            if imgurl:
                image_size = get_image_filename(IMAGE_NAMESPACE, imgurl)
                com['width'] = str(image_size.width)
                com['height'] = str(image_size.height)
    return com


@deco_cache(prefix='get_daily_news_num', recycle=DAY)
def get_daily_news_num(region_id, use_cache=True):
    count = random.randint(80, 150)
    return count


def get_position_types_by_type_list(lt):
    '''把字符串标识 list 转换成一个list 用于批量接口'''
    type_list = []
    for item in lt:
        if isinstance(item, list):
            for sub_item in item:
                type_list.append(sub_item)
        else:
            type_list.append(item)
    return type_list


def build_row_component(lt, contents_dict, comType='cell', null_row_support=1):
    ''' 生成一整行数据'''
    com_list = []
    for item in lt:
        contents = contents_dict.get(item)
        com = {}
        if contents:
            for content in contents:
                com = {}
                com['component'] = get_component_by_content(content, comType)
                if com['component']:
                    if com['component']['picUrl']:
                        com['component']['picUrl'] = build_CMS_image_url_by_width(com['component']['picUrl'], CMS_WIDTH_DICT.get(item, 750))
                        com['width'] = com['component']['width']
                        com['height'] = com['component']['height']
                    else:
                        com['component']['picUrl']=''
                        com['width'] = '0'
                        com['height'] = '0'
                    com_list.append(com)
        elif len(lt) > 1:
            if null_row_support:
                com_list.append(com)
    return com_list


def get_components_by_flags_dict(position_dict, comType='cell', null_row_support=1):
    ''' 生成广告位所有数据'''
    type_list = get_position_types_by_type_list(position_dict)
    pc = PromotionClient()
    contents_dict = pc.get_contents_by_flags_ts(type_list, time.time())
    rows = []
    for value in position_dict:
        row = {}
        row['row'] = build_row_component(value, contents_dict, comType, null_row_support)
        if row['row']:
            if len(value) == len(row['row']):
                row['column'] = str(len(value))
                rows.append(row)
    return rows


def get_banner_components_by_flags_dict(position_dict, comType='cell', null_row_support=0, limit=1):
    ''' 生成banner所有数据'''
    type_list = get_position_types_by_type_list(position_dict)
    pc = PromotionClient()
    contents_dict = pc.get_contents_by_flags_ts(type_list, time.time(), limit)
    rows = []
    for value in position_dict:
        rows = rows + build_row_component(value, contents_dict, comType, null_row_support)
    return rows


@deco_cache(prefix='banner_CMS', recycle=FIVE_MINUTES)
def get_banner_components_by_flags_key_cache(keyname, comType='cell', null_row_support=0, limit=1, use_cache=True):
    position_dict = getattr(cms_promotion_flags, keyname, [])
    return get_banner_components_by_flags_dict(position_dict, comType, null_row_support, limit)


@deco_cache(prefix='banner_CMS_REGION', recycle=FIVE_MINUTES)
def get_region_components_by_flags_key_cache(keyname, comType='cell', null_row_support=0, limit=1, use_cache=True):
    position_dict = getattr(cms_promotion_flags, keyname, [])
    return get_banner_components_by_flags_dict(position_dict, comType, null_row_support, limit)

def rebuild_region_component(com, region_id):
    com_list = []
    for item in com:
        if item.get('component',{}).get('action',{}):
            item['component']['action']['region_id'] = str(region_id)
        com_list.append(item)
    return com_list
        

@deco_cache(prefix='banner_CMS_region', recycle=FIVE_MINUTES)
def get_banner_components_by_flags_key_region_cache(keyname, cms_id, comType='cell', null_row_support=0, limit=1, use_cache=True):
    position_dict = getattr(cms_promotion_flags, keyname, [])
    position_dict = generate_promotion_key_with_attr(position_dict, cms_id)
    return get_banner_components_by_flags_dict(position_dict, comType, null_row_support, limit)

# 新版6.4.0,region_id得到region内容
def get_region_components_by_region_id(region_id, comType='cell', null_row_support=0, limit=1):
    comType = 'cell'
    comType_sku = 'region_cell'
    type_name = 'home_region_nav'
    region_type_ids = get_classes_type_id_by_type(type_name)
    region_type_ids = [region_type_id[0] for region_type_id in region_type_ids]
    region_num = len(region_type_ids)
    if int(region_id) > region_num:
        return {}
    class_type_id = get_classes_item_type_id_by_id(region_type_ids[int(region_id)-1])
    if class_type_id:
        class_type_id = class_type_id[0]
    else:
        return {}
    region_position_list = CMS_REGION_ID_PROMOTION_CONTENT
    if not region_position_list:
        return {}
    data = {}
    region_name_list = get_banner_components_by_flags_key_region_cache(region_position_list[0],class_type_id, comType, null_row_support, limit)
    data['region_name'] = rebuild_region_component(region_name_list, class_type_id)
    region_brands_list = get_banner_components_by_flags_key_region_cache(region_position_list[1], class_type_id,comType, null_row_support, limit)
    data['region_brands'] = rebuild_region_component(region_brands_list, class_type_id)
    region_pictures_list = get_banner_components_by_flags_key_region_cache(region_position_list[2],class_type_id, comType, null_row_support, limit)
    data['region_pictures'] = rebuild_region_component(region_pictures_list, class_type_id)
    region_skus_list = get_banner_components_by_flags_key_region_cache(region_position_list[3], class_type_id,comType_sku, null_row_support, limit , use_cache=False)
    data['region_skus'] = rebuild_region_component(region_skus_list, class_type_id)
    data['region_num'] = region_num
    return data


def get_components_by_one_flag(position_key, offset=0, limit=1, comType='cell', null_row_support=0):
    ''' 通过单个key 获得一些数据 支持分页 '''
    pc = PromotionClient()
    contents_dict = pc.get_contents_by_flag_ts(position_key, time.time(), offset, limit)
    rows = []
    rows = build_row_component(value, contents_dict, comType, null_row_support)
    return rows


def get_components_by_flag_dict():
    '''暂时没有用'''
    items = []
    for position_name in HOME_TAB:
        item = get_component_by_position_flag(position_name, 'cell', 'jump')
        if item:
            items.append(item)
    return items


def get_staruser_components_by_flags_dict(position_dict):
    '''热门达人使用cms  只使用跳转数据字段 添加用户id '''
    type_list = get_position_types_by_type_list(position_dict)
    pc = PromotionClient()
    contents_dict = pc.get_contents_by_flags_ts(type_list, time.time())
    items = []
    for key in type_list:
        content = contents_dict.get(key)
        if len(content) <= 0:
            continue
        user_id = content[0].action_value
        if user_id:
            user_id = int(user_id)
        else:
            continue
        com = build_staruser_by_user_id(user_id)
        if com:
            com['component']['action']['post_id'] = str(content[0].position_id)
            com['component']['action']['bannerId'] = str(content[0].id)
            items.append(com)
    return items


def generate_promotion_key_with_attr(position_dict, id):
    temp = []
    for item in position_dict:
        sub_temp = []
        if isinstance(item, list):
            for sub_item in item:
                sub_item = sub_item % str(id)
                sub_temp.append(sub_item)
        temp.append(sub_temp)
    return temp


@deco_cache(prefix='get_region_num', recycle=FIVE_MINUTES)
def get_region_num_by_bussiness_ids(region_id, use_cache=True):
    ''' 
    url = BUSSINESS_IDS_URL
    region_id = region_id
    query_all = {}
    query = {}
    query['tag_id'] = region_id
    query['ip'] = socket.gethostbyname(socket.gethostname())
    query['referer'] = 'api'
    query_all['data'] = json.dumps(query)
    count = 0
    try:
        rt = requests.post(url,data=query_all,headers={},verify=True)
        result = json.loads(rt.text)
        result = result['data']
        business_ids = []
        for each in result:
            business_ids.append(each['business_id'])
        business_ids = ','.join(business_ids)
        count = get_region_number_info(business_ids)
    except Exception, e:
        print e
    '''
    cate_name = '品牌'
    cate_id = get_class_two_id(region_id, cate_name)
    if cate_id == 0:
        return 0
    items = get_classes_type_id_by_f_id(cate_id)
    ids = [str(item.type_id) for item in items]
    business_ids = ','.join(ids)
    count = get_region_number_info(business_ids)
    return count


def get_region_number_info(business_ids):
    url = BUSSINESS_COUNT_URL
    business_ids = str(business_ids)
    start_time = datetime.date.today().strftime('%Y-%m-%d %H:%M:%S')
    end_time = datetime.date.today().strftime('%Y-%m-%d 23:59:59')
    query_all = {}
    query = {}
    query['business_ids'] = business_ids
    query['start_time'] = start_time
    query['end_time'] = end_time
    query['ip'] = '127.0.0.1'
    query['referer'] = 'api'
    query_all['data'] = json.dumps(query)
    count = 0
    try:
        rt = requests.post(url, data=query_all, headers={}, verify=True)
        result = json.loads(rt.text)
        result = result['data']
        for each in result:
            count += int(each['count'])
    except Exception, e:
        print e
    return count
