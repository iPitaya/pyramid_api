# -*- coding:utf-8 -*-
from hichao.util.statsd_client import timeit
from sqlalchemy import (
        Column,
        Integer,
        VARCHAR,
        BIGINT,
        func,
        )
from icehole_client.evaluation_client import EvaluationClient
from icehole_interface.evaluation.ttypes import *
from hichao.user.models.user import get_user_by_id
from hichao.comment.models.sub_thread  import get_image_by_id
import hashlib
import requests
import base64
import json
from hichao.base.config import ORDER_DETAIL_URL,EVALUATION_GOOD_ICON
import time
from hichao.util.image_url import build_choiceness_thread_image_url,default_user_avatar,build_evaluation_image_url
import datetime
from hichao.util.statsd_client import timeit
from hichao.util.ecshop_interface_util import get_message_from_ecshop_interface
from hichao.cache.cache import deco_cache
from hichao.util.date_util import HOUR, DAY, FIVE_MINUTES,WEEK
from hichao.cache.cache import delete_cache_by_key
from hichao.base.config import FALL_PER_PAGE_NUM

SIZE_DICT = {0:'适合',1:'偏大', 2: '偏小',-1:''}
BUSINESS_SCORE_DICT = {'goods':'产品描述','serve':'服务质量','logistics':'物流速度'}
CLOTH_CATEGORY = [17,20,19,98,250,171,60,61,104,255,221,258,271,272,300]
SHOES_CATEGORY = [21,62,274]

timer = timeit('hichao_backend.m_evaluation')

@timer
def comment_and_reply_list(comment_list, comment_id, client):
    #items = client.get_comment_reply_list_by_comment_id(comment_id)
    items = get_comment_and_reply_list( comment_id)
    for item in items:
        comment_list.append(item)
        if item.type != 2 and (item.is_replied == 1 or item.is_commented == 1):
            temp = comment_and_reply_list(comment_list, item.id, client)
    return comment_list

@timer
@deco_cache(prefix = 'get_comment_and_reply_list1', recycle = WEEK)
def get_comment_and_reply_list( comment_id, use_cache = True):
    client = EvaluationClient()
    items = client.get_comment_reply_list_by_comment_id(int(comment_id))
    return items

@timer
def get_comment_days_from_data(start,end):
    start_time = time.mktime(time.strptime(start,"%Y-%m-%d %H:%M:%S"))
    end_time = time.mktime(time.strptime(end,"%Y-%m-%d %H:%M:%S"))
    num = datetime.datetime.utcfromtimestamp(end_time) - datetime.datetime.utcfromtimestamp(start_time) 
    return num.days

@timer
def get_comment_days_timestamp(start,end,comment_type):
    tm_days = datetime.datetime.utcfromtimestamp(end)- datetime.datetime.utcfromtimestamp(start)
    day_num = str(tm_days.days)
    add_msg = '天后追加'
    reply_msg = '天后回复'
    result = ''
    if tm_days.days == 0:
        day_num = '当天'
    if str(comment_type) == '1':
        if tm_days.days == 0:
            result = '当天追加'
        else:
            result = day_num  + add_msg
    elif str(comment_type) == '2':
        if tm_days.days == 0:
            result = '当天回复'
        else:
            result = day_num  + reply_msg
    return result

@timer
@deco_cache(prefix = 'goods_comment_list_cache1', recycle = WEEK)
def get_goods_comment_list_cache(goods_id, comment_type, offset, limit, use_cache = True):
    client = EvaluationClient()
    comments = client.get_goods_comment_list(int(goods_id), int(comment_type), int(offset), int(limit))
    return comments
      
@timer
def get_goods_commets_by_goods_id( goods_id, comment_type, offset, limit):
    client = EvaluationClient()
    #comments = client.get_goods_comment_list(int(goods_id), int(comment_type), int(offset), int(limit))
    comments = get_goods_comment_list_cache(goods_id, comment_type, offset, limit)
    com = []
    for comment in comments:
        temp = {}
        temp = build_goods_comment_component(comment)
        temp['publishDate'] = time.strftime("%m-%d %H:%M", time.localtime(comment.create_ts)) 
        comment_list = []
        if comment.is_replied == 1 or comment.is_commented == 1:
            comment_and_reply_list(comment_list, comment.id, client)
        com_reply = []
        for reply in comment_list:
            reply_temp = {}
            reply_temp = build_reply_comment_component(reply)
            reply_temp['publishDate'] = get_comment_days_timestamp(comment.create_ts,reply.create_ts,reply.type)
            com_reply.append(reply_temp)
        temp['replys'] = com_reply
        com.append(temp)
    return com

@timer
def get_goods_commets_by_goods_id_to_app( goods_id, comment_type, offset, limit):
    #client = EvaluationClient()
    #comments = client.get_goods_comment_list(int(goods_id), int(comment_type), int(offset), int(limit))
    comments = get_goods_comment_list_cache(goods_id, comment_type, offset, limit)
    com = []
    for comment in comments:
        temp = {}
        temp['component'] = build_goods_comment_component(comment)
        if temp['component']:
            temp['component']['content'] = temp['component']['content'].replace('&lt;','<').replace('&gt;','>')
        comment_list = []
        #comment_and_reply_list(comment_list, comment.id, client)
        com_reply = []
        #for reply in comment_list:
        #    com_reply.append(build_reply_comment_component(reply))
        temp['component']['replys'] = com_reply
        com.append(temp)
    return com

@timer
def get_imgs_by_comment_id(comment_id):
    client = EvaluationClient()
    ids = client.get_goods_comment_imgs_by_id(comment_id)
    imgs = []
    for id in ids:
        img_url = get_image_by_id(id)
        img = ''
        if img_url:
            if not img_url.namespace:
                img = img_url.url
            else:
                img = build_choiceness_thread_image_url(img_url.url, img_url.namespace)
        if img:
            imgs.append(img)
    return imgs

@timer
def get_imgs_by_img_ids(ids, size=600):
    imgs = []
    for id in ids:
        img_url = get_image_by_id(id)
        img = ''
        if img_url:
            if not img_url.namespace:
                img = img_url.url
            else:
                img = build_evaluation_image_url(img_url.url, img_url.namespace, size)
        if img:
            imgs.append(img)
    return imgs

#生成类别相关属性
def generate_cateAddAttr(attr_json, category_id):
        cateAddAttr = ''
        if not attr_json:
            return ''
        data_attr = eval(attr_json)
        if category_id in CLOTH_CATEGORY:
            if data_attr.get('body_height',''):
                cateAddAttr ="身高: " + str(data_attr.get('body_height','')) + "cm"
            if data_attr.get('body_weight',''):
                if cateAddAttr:
                    cateAddAttr += "    "
                cateAddAttr +="体重: " + str(data_attr.get('body_weight','')) + "kg"
            if data_attr.get('color_diff','') != '':
                if cateAddAttr:
                    cateAddAttr += "    "
                temp = ''
                temp = "是" if data_attr.get('color_diff','') == '1' else "否"
                cateAddAttr +="是否有色差: " + temp
        if category_id in SHOES_CATEGORY:
            if data_attr.get('foot_length',''):
                cateAddAttr ="脚长: " + str(data_attr.get('foot_length','')) + "cm"
            if data_attr.get('foot_breadth',''):
                if cateAddAttr:
                    cateAddAttr += "    "
                cateAddAttr +="脚宽: " + str(data_attr.get('foot_breadth','')) + "cm"
            if data_attr.get('smells','') != '':
                if cateAddAttr:
                    cateAddAttr += "    "
                temp = ''
                temp = "是" if data_attr.get('smells','') == '1' else "否"
                cateAddAttr +="是否有异味: " + temp
        return cateAddAttr
     
@timer
def build_goods_comment_component(comment):
    com = {}
    if comment:
        com['userId'] = comment.user_id
        user_name = u'匿名'
        user_avatar = default_user_avatar
        user = None
        login_time = 1
        if comment.user_id > 0:
            user = get_user_by_id(comment.user_id)
        if user:
            user_name = user.get_component_user_name()
            #user_name = user_name.encode('utf-8')
            user_avatar = user.get_component_user_avatar()
            login_time = int((time.time() - user.get_register_date())/(24*60*60)) + 1
        if comment.use_anonymous:
            #user_name = '匿名'
            user_name = user_name[0:1] + '***' + user_name[-1:]
            user_avatar = default_user_avatar
            '''
            if user_name:
                if user_name[0:1].isalnum():
                    user_name_temp = user_name[0:1] + '***'
                else:
                    user_name_temp = user_name[0:3] + '***'
                if user_name[-1:].isalnum():
                    user_name_temp += user_name[-1:0]
                else:
                    user_name_temp += user_name[-3]
                user_name = user_name_temp
            '''
        com['userName'] = user_name
        com['userAvatar'] = user_avatar
        com['useAppTime'] = '加入衣橱' + str(login_time) + '天'
        com['userScore'] = comment.goods_satisfy
        com['publishDate'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment.create_ts))
        com['create_ts'] = comment.create_ts
        if comment.content:
            com['content'] = comment.content
        else:
            com['content'] = '好评！'
        com['goodsId'] = str(comment.goods_id)
        com['sourceId'] = str(comment.source_id)
        #if not comment.size_type:
        #    comment.size_type = 'M'
        com['sizeType'] = comment.size_type
        com['isReply'] = str(comment.is_replied)
        com['commentType'] = str(comment.type)
        com['size'] = SIZE_DICT[comment.size_state]
        com['goodsAttr'] = ''
        if comment.size_type:
            com['goodsAttr'] = '尺码: '+comment.size_type+'     ' + '尺码大小: ' + com['size']
        if comment.has_img:
            #com['imgs'] = get_imgs_by_comment_id(comment.id)
            com['imgs'] = get_imgs_by_img_ids(comment.imgs, 100)
            com['big_imgs'] = get_imgs_by_img_ids(comment.imgs, 600)
        else:
            com['imgs'] = []
            com['big_imgs'] = []
        com['cateAddAttr'] = generate_cateAddAttr(comment.attr_json,comment.category_id)
        com['essenceIcon'] = ''
        if comment.is_essence:
            com['essenceIcon'] = EVALUATION_GOOD_ICON
        com['id'] = comment.id
        com['componentType'] = 'evaluation'
    return com

@timer
def build_reply_comment_component(comment):
    com = {}
    if comment:
        com['publishDate'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment.create_ts))
        com['content'] = comment.content
        com['componentType'] = 'evaluation_reply'
        com['id'] = str(comment.id)
        com['businessId'] = str(comment.business_id)
        com['goodsId'] = str(comment.goods_id)
        com['commentType'] = str(comment.type)
        if comment.has_img:
            #com['imgs'] = get_imgs_by_comment_id(comment.id)
            com['imgs'] = get_imgs_by_img_ids(comment.imgs, 100)
            com['big_imgs'] = get_imgs_by_img_ids(comment.imgs, 600)
        else:
            com['imgs'] = []
            com['big_imgs'] = []
    return com

def shop_comment_and_reply_list(comment_list, comment_id, client, temp):
    comment_temp = get_comment_and_reply_list(comment_id)
    com_reply = []
    flag = 0
    tmp = ''
    for reply in comment_temp:
        if int(reply.type) == 2:
            flag = 1
            com_reply.append(build_reply_comment_component(reply))
            temp['replys'] = com_reply
            comment_list.append(temp)
        else:
            tmp = build_goods_comment_component(reply)
            shop_comment_and_reply_list(comment_list, reply.id, client, tmp)
    if flag == 0 and tmp:
        tmp['replys'] = []
        comment_list.append(tmp)
    return comment_list        
        
@timer
def get_goods_commets_by_business_id( business_id, comment_type, offset, limit):
    client = EvaluationClient()
    comments = client.get_goods_comment_list_by_business_id(int(business_id), int(comment_type), int(offset), int(limit))
    com = []
    com_test = []
    for comment in comments:
        temp = {}
        temp = build_goods_comment_component(comment)
        
        comment_list = []
        if comment.is_replied == 1 or comment.is_commented == 1:
            comment_list = get_comment_and_reply_list(comment.id)
        com_reply = []
        flag = 0
        for reply in comment_list:
            if int(reply.type) == 2:
                com_reply = []
                flag = 1
                com_reply.append(build_reply_comment_component(reply))
                temp['replys'] = com_reply
                com.append(temp)
        if flag == 0:
            temp['replys'] = []
            com.append(temp)
        for reply in comment_list:
            if int(reply.type) == 1:
                temp1 = {}
                temp1 = build_goods_comment_component(reply)
                comment_list1 = []
                if reply.is_replied == 1 or reply.is_commented == 1:
                    comment_list1 = get_comment_and_reply_list(reply.id)
                com_reply1 = []
                flag1 = 0
                for reply1 in comment_list1:
                    if int(reply1.type) == 2:
                        com_reply1 = []
                        flag1 = 1
                        com_reply1.append(build_reply_comment_component(reply1))
                        flag = 1
                        temp1['replys'] = com_reply1
                        com.append(temp1)
                if flag1 == 0:
                    temp1['replys'] = []
                    com.append(temp1)
        #shop_comment_and_reply_list(com_test, comment.id, client, temp)    
    #print com_test  , 'com_test'
    return com

@timer
def generate_GoodsComment(content = '', goods_satisfy = 5, size_state = 0, has_img = 0,use_anonymous =0, business_id = 0, order_id = 0, rec_id = 0, sku_id = 0, source_id = 0, goods_id = 0, product_id = 0, user_id = 0, parent_id = 0, type = 0, fake = 0, size_type = '', color = '', platform = ''):
    gd = GoodsComment()
    gd.content = content
    gd.goods_satisfy = goods_satisfy
    gd.size_state = size_state
    gd.has_img = has_img
    gd.use_anonymous = use_anonymous
    gd.business_id = business_id
    gd.order_id = order_id
    gd.rec_id = rec_id
    gd.sku_id = sku_id
    gd.source_id = source_id
    gd.goods_id = goods_id
    gd.product_id = product_id
    gd.user_id = user_id
    gd.review = 1
    gd.parent_id = parent_id
    gd.type = type
    gd.fake = fake
    gd.size_type = size_type
    gd.color = color
    gd.platform = platform
    return gd

def get_goods_comment_dict():
    comment = {}
    comment['business_id'] = 0
    comment['content'] = ''
    comment['parent_id'] = 0
    comment['type'] = 0
    comment['platform'] = ''
    comment['goods_satisfy'] = 5
    comment['size_state'] = 0
    comment['has_img'] = 0
    comment['use_anonymous'] = 0
    comment['order_id'] = 0
    comment['rec_id'] = 0
    comment['sku_id'] = 0
    comment['source_id'] = 0
    comment['goods_id'] = 0
    comment['product_id'] = 0
    comment['user_id'] = 0
    comment['fake'] = 0
    comment['size_type'] = ''
    comment['color'] = ''
    return comment

def GoodsComment_to_dict(comment):
    comment_dict = {}
    comment_dict['business_id'] = comment.business_id
    comment_dict['content'] = comment.content
    comment_dict['parent_id'] = comment.parent_id
    comment_dict['type'] = comment.type
    comment_dict['platform'] = comment.platform
    comment_dict['goods_satisfy'] = comment.goods_satisfy
    comment_dict['size_state'] = comment.size_state
    comment_dict['has_img'] = comment.has_img
    comment_dict['use_anonymous'] = comment.use_anonymous
    comment_dict['order_id'] = comment.order_id
    comment_dict['rec_id'] = comment.rec_id
    comment_dict['sku_id'] = comment.sku_id
    comment_dict['source_id'] = comment.source_id
    comment_dict['goods_id'] = comment.goods_id
    comment_dict['product_id'] = comment.product_id
    comment_dict['user_id'] = comment.user_id
    comment_dict['fake'] = comment.fake
    comment_dict['size_type'] = comment.size_type
    comment_dict['color'] = comment.color
    return comment_dict

def get_goods_comment_by_comment_id(comment_id):
    client = EvaluationClient()
    comment = client.get_goods_comment_by_comment_id(comment_id)
    return comment

def generate_GoodsComment_from_dict(comment):
    gd = GoodsComment()
    gd.content = comment.get('content','')
    gd.goods_satisfy = int(comment.get('goods_satisfy',5))
    size_state = comment.get('size_state',0)
    if size_state == '':
        size_state = -1
    gd.size_state = int(size_state)
    if comment.get('imgs',[]):
        gd.has_img = 1
        gd.imgs = [int(img) for img in comment['imgs']]
    else:
        gd.has_img = 0
        gd.imgs = []
    gd.use_anonymous = int(comment.get('use_anonymous',1))
    gd.business_id = int(comment.get('business_id',0))
    gd.order_id =  int(comment.get('order_id',0))
    gd.rec_id = int(comment.get('rec_id',0))
    if comment.has_key('sku_id'):
        gd.sku_id = int(comment['sku_id'])
    else:
        gd.sku_id = 0
    gd.source_id = int(comment.get('source_id',0))
    gd.goods_id = int(comment.get('goods_id',0))
    gd.product_id = int(comment.get('product_id',0))
    gd.user_id = int(comment.get('user_id',0))
    gd.review = 1
    gd.parent_id = int(comment.get('parent_id',0) if comment.get('parent_id',0) else 0)
    gd.type = int(comment.get('type',0))
    gd.fake = int(comment.get('fake',0))
    gd.size_type = comment.get('size_type','')
    gd.color = comment.get('color','')
    gd.platform = comment.get('platform','')
    gd.attr_json = str(comment.get('attr_json',''))
    category_id = comment.get('category_id',0)
    gd.category_id = 0
    if category_id:
        gd.category_id = int(category_id)
    return gd

def generate_BusinessComment_from_dict(business):
    bu = BusinessComment()
    bu.business_id = int(business.get('business_id',0))
    bu.order_id = int(business.get('order_id',0))
    bu.user_id = int(business.get('user_id',0))
    bu.goods_ratio = int(business.get('goods_ratio',5))
    bu.serve_satisfy = int(business.get('serve_satisfy',5))
    bu.logistics_satisfy = int(business.get('logistics_satisfy',5))
    bu.review = 1
    return bu
    
@timer
def add_comment_business_replace(comment):
    comment = generate_GoodsComment_from_dict(comment)
    client = EvaluationClient()
    result = client.add_goods_comment_only(comment)
    return result

@timer
def add_additional_comments(comments):
    client = EvaluationClient()
    result = client.add_goods_comment_list(comments)
    return result

@timer
def add_goods_business_comment(goods_list, business_list):
    client = EvaluationClient()
    '''
    goods = generate_GoodsComment()
    business = BusinessComment()
    business.business_id = 10
    business.goods_ratio = 5
    business.serve_satisfy = 5
    business.logistics_satisfy = 5
    business.review = 1
    '''
    client.add_goods_business_comment_list(goods_list,business_list)
    return 1

def build_business_score_component(comment):
    com = {}
    if comment:
        com['id'] = str(comment.business_id)
        com['goods'] = str(comment.goods_score)
        com['serve'] = str(comment.serve_score)
        com['logistics'] = str(comment.logistics_score)
    else:
        com['id'] = 0
        com['goods'] = '5.0'
        com['serve'] = '5.0'
        com['logistics'] = '5.0'
    return com

def rebuild_business_score_component(comment):
    com_list = []
    for key in ['goods','serve','logistics']:
        com = {}
        com['name'] = BUSINESS_SCORE_DICT[key]
        com['value'] = comment[key]
        level = 2
        if float(comment[key]) <= 2.0:
            level = 0
        elif float(comment[key]) <= 4.0:
            level = 1
        com['level'] = str(level)
        com_list.append(com)
    return com_list

@timer
@deco_cache(prefix = 'business_score', recycle = WEEK)
def get_business_score(business_id, use_cache = True):
    client = EvaluationClient()
    item = client.get_business_score_by_id(business_id)
    result = build_business_score_component(item)
    result = rebuild_business_score_component(result)
    return result

@timer
def get_comment_state(order_id):
    client = EvaluationClient()
    result = client.get_goods_comment_state(int(order_id))
    return result

@timer
@deco_cache(prefix = 'goods_comment_num', recycle = WEEK)
def get_comment_num(goods_id, use_cache = True):
    client = EvaluationClient()
    result = client.get_goods_comment_num(int(goods_id), 0)
    return result

@timer
def get_order_detail(d_attr):
    API_SECRET_KEY = '71e5d83f6480523cb7b52e13445c2865'
    data = {}
    data['source'] = 'mxyc_ios'
    data['version'] = '6.3.1'
    data['method'] = 'order.detail'
    data['token'] = d_attr['token']
    data['app_uid'] = d_attr['app_uid']
    order_id = d_attr['order_id']
    data['data'] = base64.b64encode(json.dumps({'order_id':order_id}))
    sign = data['source'] + data['version'] + data['method'] + data['token'] + data['app_uid'] + data['data'] + API_SECRET_KEY
    data['sign'] = hashlib.md5(sign).hexdigest()
    #$validate = md5($source.$version.$method.$token.$app_uid.$data.API_SECRET_KEY);
    #url = 'http://v1.api.mall.hichao.com/hichao/interface.php'
    url = ORDER_DETAIL_URL
    r = requests.post(url, data = data,verify=False)
    return r.text

def get_order_detail_new(source, app_uid, method, token, version, d_attr):
    result = get_message_from_ecshop_interface(source, app_uid, method, token, version, d_attr)
    return result

@timer
def set_order_comment_state(d_attr):
    API_SECRET_KEY = '71e5d83f6480523cb7b52e13445c2865'
    data = {}
    data['source'] = 'mxyc_ios'
    data['version'] = '6.3.1'
    data['method'] = 'order.update.evaluatestatus'
    data['token'] = d_attr['token']
    data['app_uid'] = d_attr['app_uid']
    order_id = d_attr['order_id']
    evaluate_status = d_attr['status']
    data['data'] = base64.b64encode(json.dumps({'order_id':order_id,'evaluate_status':evaluate_status}))
    sign = data['source'] + data['version'] + data['method'] + data['token'] + data['app_uid'] + data['data'] + API_SECRET_KEY
    data['sign'] = hashlib.md5(sign).hexdigest()
    #$validate = md5($source.$version.$method.$token.$app_uid.$data.API_SECRET_KEY);
    #url = 'http://v1.api.mall.hichao.com/hichao/interface.php'
    url = ORDER_DETAIL_URL
    r = requests.post(url, data = data,verify=False)
    return r.text

@timer
def update_order_comment_state(order_id,app_uid,token,comment_type):
    d_attr = {}
    d_attr['token'] = str(token)
    d_attr['app_uid'] = str(app_uid)
    d_attr['order_id'] = str(order_id)
    r = ''
    if comment_type == 0:
        d_attr['status'] = '2'
        r = set_order_comment_state(d_attr)
    elif comment_type == 1:
        state = get_comment_state(order_id)
        if state == '2':
            d_attr['status'] = '0'
            r = set_order_comment_state(d_attr)     
    elif comment_type == 3:
        d_attr['status'] = '0'
        r = set_order_comment_state(d_attr)
    return r

@timer
def get_items_from_order_detail(data, order_id):
    if not data:
        return []
    items = []
    for item in data['items']:
        com = {}
        com['brand_name'] = item.get('brand_name','')
        com['business_id'] = item.get('business_id','')
        com_items = []
        for goods in item['goods']:
            state = check_goods_additional_state(goods['product_id'], order_id, goods['rec_id'])
            if state:
                continue
            temp = {}
            temp['goods_name'] = goods['goods_name']
            temp['goods_attr'] = goods['goods_attr']
            temp['rec_id'] = goods['rec_id']
            temp['product_id'] = goods['product_id']
            temp['goods_number'] = goods['goods_number']
            temp['goods_paid_price'] = goods['goods_paid_price']
            temp['goods_image'] = goods['goods_image']
            '''
            #goods['rec_id'] = 100
            attr_list = []
            goods_attr0 = {}
            goods_attr0['opName'] = 'order_id'
            goods_attr0['opValue'] = int(order_id)
            goods_attr0['op'] = '=='
            attr_list.append(goods_attr0)
            goods_attr1 = {}
            goods_attr1['opName'] = 'product_id'
            goods_attr1['opValue'] = int(goods['product_id'])
            goods_attr1['op'] = '=='
            attr_list.append(goods_attr1)
            goods_attr2 = {}
            goods_attr2['opName'] = 'review'
            goods_attr2['opValue'] = 1
            goods_attr2['op'] = '=='
            attr_list.append(goods_attr2)
            goods_attr3 = {}
            goods_attr3['opName'] = 'type'
            goods_attr3['opValue'] = 0
            goods_attr3['op'] = '=='
            attr_list.append(goods_attr3)
            comments = get_goods_comment_public(str(attr_list))
            comment = None
            if comments:
                comment = comments[0]
            '''
            comment = order_detail_comment_reply(order_id,int(goods['product_id']),0,goods['rec_id'])
            if not comment:
                continue
            temp['reply'] = build_additional_comment_component(comment)
            if temp['reply']:
                '''
                attr_list = []
                goods_attr0 = {}
                goods_attr0['opName'] = 'order_id'
                goods_attr0['opValue'] = int(order_id)
                goods_attr0['op'] = '=='
                attr_list.append(goods_attr0)
                goods_attr1 = {}
                goods_attr1['opName'] = 'product_id'
                goods_attr1['opValue'] = int(goods['product_id'])
                goods_attr1['op'] = '=='
                attr_list.append(goods_attr1)
                goods_attr2 = {}
                goods_attr2['opName'] = 'review'
                goods_attr2['opValue'] = 1
                goods_attr2['op'] = '=='
                attr_list.append(goods_attr2)
                goods_attr3 = {}
                goods_attr3['opName'] = 'type'
                goods_attr3['opValue'] = 2
                goods_attr3['op'] = '=='
                attr_list.append(goods_attr3)
                comments = get_goods_comment_public(str(attr_list))
                comment1 = None
                if comments:
                    comment1 = comments[0]
                '''
                comment1 = order_detail_comment_reply(order_id,int(goods['product_id']),2,goods['rec_id'])
                temp['reply']['shopReplyDate'] = ''
                temp['reply']['shopReplyContent'] = ''
                if comment1 and comment1.content:
                    temp['reply']['shopReplyDate'] = '[' + get_comment_days_timestamp(comment.create_ts,comment1.create_ts,2) + ']'
                    temp['reply']['shopReplyContent'] = comment1.content
            if temp:
                com_items.append(temp)
        com['goods'] = com_items
        items.append(com)
    return items

def order_detail_comment_reply(order_id,product_id,type,rec_id = 0):
    '''
    attr_list = []
    goods_attr0 = {}
    goods_attr0['opName'] = 'order_id'
    goods_attr0['opValue'] = int(order_id)
    goods_attr0['op'] = '=='
    attr_list.append(goods_attr0)
    goods_attr1 = {}
    goods_attr1['opName'] = 'product_id'
    goods_attr1['opValue'] = int(product_id)
    goods_attr1['op'] = '=='
    attr_list.append(goods_attr1)
    goods_attr2 = {}
    goods_attr2['opName'] = 'review'
    goods_attr2['opValue'] = 1
    goods_attr2['op'] = '=='
    attr_list.append(goods_attr2)
    goods_attr3 = {}
    goods_attr3['opName'] = 'type'
    goods_attr3['opValue'] = int(type)
    goods_attr3['op'] = '=='
    attr_list.append(goods_attr3)
    comments = get_goods_comment_public(str(attr_list))
    '''
    comments = get_goods_comment_by_rec_id(rec_id, order_id, product_id, type, 1)
    comment = None
    if comments:
        comment = comments[0]
    return comment

@timer
def check_goods_additional_state(product_id, order_id, rec_id = 0):
    '''
    attr_list = []
    goods_attr0 = {}
    goods_attr0['opName'] = 'order_id'
    goods_attr0['opValue'] = int(order_id)
    goods_attr0['op'] = '=='
    attr_list.append(goods_attr0)
    goods_attr1 = {}
    goods_attr1['opName'] = 'product_id'
    goods_attr1['opValue'] = int(product_id)
    goods_attr1['op'] = '=='
    goods_attr2 = {}
    goods_attr2['opName'] = 'type'
    goods_attr2['opValue'] = 1
    goods_attr2['op'] = '=='
    goods_attr3 = {}
    goods_attr3['opName'] = 'review'
    goods_attr3['opValue'] = 1
    goods_attr3['op'] = '=='
    attr_list.append(goods_attr3)
    attr_list.append(goods_attr2)
    attr_list.append(goods_attr1)
    items = get_goods_comment_public(str(attr_list))
    '''
    items = get_goods_comment_by_rec_id(rec_id, order_id, product_id, 1, 1)
    return len(items)

@timer
def get_goods_comment_by_rec_id(rec_id, order_id, product_id, comment_type, review):
    client = EvaluationClient()
    result = client.get_goods_comment_list_rec_order_product_id(int(rec_id), int(order_id), int(product_id), int(comment_type), int(review))
    return result
    
@timer
def get_goods_comment_public(goods_str):
    client = EvaluationClient()
    result = client.get_goods_comment_list_public(goods_str,0,1,1)
    return result
    
@timer
def get_goods_comment_num_public(goods_str):
    client = EvaluationClient()
    result = client.get_goods_comment_num_public(goods_str)
    return result
    
@timer
def build_additional_comment_component(comment):
    com = {}
    if comment:
        com['publishDate'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment.create_ts))
        com['content'] = comment.content.replace('&lt;','<').replace('&gt;','>')
        com['componentType'] = 'evaluation_reply'
        com['id'] = str(comment.id)
        com['businessId'] = str(comment.business_id)
        com['goodsId'] = str(comment.goods_id)
        com['commentType'] = str(comment.type)
        com['userScore'] = comment.goods_satisfy
        com['sizeType'] = comment.size_type
        com['size'] = SIZE_DICT[comment.size_state]
        com['cateAddAttr'] = generate_cateAddAttr(comment.attr_json,comment.category_id)
        if comment.has_img:
            #com['imgs'] = get_imgs_by_comment_id(comment.id)
            com['imgs'] = get_imgs_by_img_ids(comment.imgs, 100)
            com['big_imgs'] = get_imgs_by_img_ids(comment.imgs, 600)
        else:
            com['imgs'] = []
            com['big_imgs'] = []
    return com

@timer
def check_goods_additional_comment_business_reply(comment_id,comment_type):
    client = EvaluationClient()
    result = client.get_goods_comment_list_by_parent_id_and_type(int(comment_id),int(comment_type))
    return result

def check_evaluation_legal(access_token, gv, gf, user_id, data, eva_auth):
    key = '3f97ed86870dd5a02842978598a54f50'
    get_eva_auth = hashlib.md5(access_token + gv + gf + str(user_id) + base64.b64encode(data) + key).hexdigest()
    if get_eva_auth != eva_auth:
        return False
    else:
        return True
    
@timer
def delete_comment_cache(g_id):
    try:
        delete_cache_by_key('goods_comment_list_cache1_'+str(g_id)+ '_4_0_2')
        comment_num = get_comment_num(g_id)
        for i in range(1,int(comment_num)/FALL_PER_PAGE_NUM+1):
            comment_list_key = 'goods_comment_list_cache1_'+str(g_id)+ '_0_' + str(i*FALL_PER_PAGE_NUM) + '_' + str(FALL_PER_PAGE_NUM) 
            delete_cache_by_key(comment_list_key)
            comment_list_key = 'goods_comment_list_cache1_'+str(g_id)+ '_1_' + str(i*FALL_PER_PAGE_NUM) + '_' + str(FALL_PER_PAGE_NUM) 
            delete_cache_by_key(comment_list_key)
            comment_list_key = 'goods_comment_list_cache1_'+str(g_id)+ '_2_' + str(i*FALL_PER_PAGE_NUM) + '_' + str(FALL_PER_PAGE_NUM) 
            delete_cache_by_key(comment_list_key)
            print comment_list_key,'comment_list_key'
    except Exception,e:
        print e

