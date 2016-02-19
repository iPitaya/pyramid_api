# -*- coding:utf-8 -*-

import os
import importlib
api_env = os.environ.get('thrift_stage','yanjiao')
print api_env
try:
    m = importlib.import_module('hichao.base.config.%s' % api_env)
    globals().update(vars(m))
    del m
except Exception as e:
    import traceback
    traceback.print_exc()
    from hichao.base.config.yanjiao import *

#脚本执行时使用
jiaoben_stage = os.environ.get('procname')
print jiaoben_stage
if not jiaoben_stage:
    USE_LOCAL_CACHE = 0
print 'USE_LOCAL_CACHE',USE_LOCAL_CACHE
##############################################################################
# LOCAL CACHE SECTION
LOCAL_CACHE_RECYCLE = 10
LOCAL_CACHE_PORT = 8010
LOCAL_CACHE_NAME = 'local'

##############################################################################
# CACHE SECTION
CACHE_PREFIX = 'api2'

##############################################################################
# GLOBAL SETTING SECTION

FALL_PER_PAGE_NUM = 18
MYSQL_MAX_INT = 2147483647L
MYSQL_MAX_BIG_INT = 9223372036854775807L
MYSQL_MAX_TIMESTAMP = '2038-01-19 03:14:07'
COMMENT_NUM_PER_PAGE = 11
SHOW_SKU_IMGS = '1'

UPDOWN_MYSQL_USER = MYSQL_USER
UPDOWN_MYSQL_PASSWD = MYSQL_PASSWD
UPDOWN_MYSQL_HOST = MYSQL_HOST
UPDOWN_MYSQL_PORT = MYSQL_PORT

SYNC_MYSQL_USER = MYSQL_USER
SYNC_MYSQL_PASSWD = MYSQL_PASSWD
SYNC_MYSQL_HOST = MYSQL_HOST
SYNC_MYSQL_PORT = MYSQL_PORT

READONLY_MYSQL_USER = MYSQL_SLAVE_USER
READONLY_MYSQL_PASSWD = MYSQL_SLAVE_PASSWD
READONLY_MYSQL_HOST = MYSQL_SLAVE_HOST
READONLY_MYSQL_PORT = MYSQL_SLAVE_PORT

UDID_MYSQL_USER = MYSQL_USER
UDID_MYSQL_PASSWD = MYSQL_PASSWD
UDID_MYSQL_HOST = MYSQL_HOST
UDID_MYSQL_PORT = MYSQL_PORT

POINT_MYSQL_USER = MYSQL_USER
POINT_MYSQL_PASSWD = MYSQL_PASSWD
POINT_MYSQL_HOST = MYSQL_HOST
POINT_MYSQL_PORT = MYSQL_PORT

SQLALCHEMY_CONF_URL = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8"\
                        %(MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'base')

##############################################################################
# SHORT URL SECTION

SHORTY_HOST = 'yj.s.hichao.com'

##############################################################################
# MONGO SECTION

MONGO_HOST = '192.168.1.8'
MONGO_PORT = '20000'

##############################################################################
# THIRD PARTY SECTION

THIRD_PARTY_APP = dict()

THIRD_PARTY_APP['qq'] = dict(
    client_id = 100276062,
    client_secret = '1b99e03a1120def3a3c12b39b930bac1',
    redirect_uri = 'http://haobao.com/connect/qq'
    )

THIRD_PARTY_APP['weibo'] = dict(
    client_id = 1415704957,
    client_secret = '738b122ce2021015b01d0043d7d672d3',
    redirect_uri = 'http://haobao.com/connect/weibo'
    )


THIRD_PARTY_APP['taobao'] = dict(
    client_id = 12629922,
    client_secret = '52ce4631a8b2e52ba47008d1ec09d573',
    redirect_uri = 'http://haobao.com/connect/taobao'
    )

THIRD_PARTY_USER_ENTER_POINT = {}

THIRD_PARTY_USER_ENTER_POINT['taobao'] = {
    'cart':'http://h5.m.taobao.com/awp/base/bag.htm',
    'order':'http://h5.m.taobao.com/mlapp/olist.html',
    'express':'http://h5.m.taobao.com/awp/mtb/olist.htm?sta=5',
}


#############################################################################
# CDN SECTION

from CDN import (
    CDN_IMAGE_PATH,
    CDN_TOPIC_IMAGE_PATH,
    CDN_TOPIC_CELL_IMAGE_PATH,
    CDN_DEFAULT_AVATAR_IMAGE_PATH,
    CDN_KEYWORD_IMAGE_PATH,
    CDN_VIDEO_PATH,
    CDN_ROOT_PATH,
    generate_cdn_image_url,
    generate_keyword_image_prefix,
    generate_search_star_list_image_prefix,
    generate_sku_detail_image_prefix,
    generate_forum_image_prefix,
    generate_sku_attached_image_prefix,
    generate_fast_dfs_image_prefix,
    generate_user_uploaded_image_prefix,
    )

CDN_IMAGE_PREFIX = generate_cdn_image_url(CDN_IMAGE_PATH).next
CDN_TOPIC_IMAGE_PREFIX = generate_cdn_image_url(CDN_TOPIC_IMAGE_PATH).next
CDN_TOPIC_CELL_IMAGE_PREFIX = generate_cdn_image_url(CDN_TOPIC_CELL_IMAGE_PATH).next
CDN_DEFAULT_AVATAR_IMAGE = generate_cdn_image_url(CDN_DEFAULT_AVATAR_IMAGE_PATH).next
CDN_PREFIX = generate_cdn_image_url(CDN_ROOT_PATH).next
CDN_KEYWORD_IMAGE_PREFIX = generate_keyword_image_prefix.next
CDN_VIDEO_PREFIX = generate_cdn_image_url(CDN_VIDEO_PATH).next
CDN_SEARCH_STAR_LIST_IMAGE_PREFIX = generate_search_star_list_image_prefix.next
CDN_SKU_DETAIL_IMAGE_PREFIX = generate_sku_detail_image_prefix.next
CDN_SKU_ATTACHED_IMAGE_PREFIX = generate_sku_attached_image_prefix.next
CDN_FORUM_IMAGE_PREFIX = generate_forum_image_prefix().next
CDN_FAST_DFS_IMAGE_PREFIX = generate_fast_dfs_image_prefix.next
CDN_MXYC_UPLOADED_IMAGE_PREFIX = generate_user_uploaded_image_prefix.next

#############################################################################
# CHANNEL SECTION

CHANNEL_DEFAULT = 0
CHANNEL_TAOBAO = 1
CHANNEL_TMALL = 2
CHANNEL_AMAZON = 3
CHANNEL_DANGDANG = 4
CHANNEL_VANCL = 5
CHANNEL_JD = 6
CHANNEL_MENGBASHA = 7
CHANNEL_VPLUS = 8
CHANNEL_YIXUN = 9
CHANNEL_MAIBAOBAO = 10
CHANNEL_YINTAI = 11
CHANNEL_LEFENG = 12
CHANNEL_VIP = 13
CHANNEL_ECSHOP = 14
TAOBAO_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20130523/67de9550-f4b5-49be-a608-f3c7cbd96dfb.png'
TMALL_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20130523/1bafc0c4-73c6-4ea7-8899-c548da32ed1b.png'
AMAZON_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20130828/3e7ddd63-82bf-42dc-b58f-5511f2fc661f.png'
DANGDANG_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20130828/70a34be8-03f3-4d5a-a109-d715925cbde5.png'
VANCL_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20130828/de039c57-8b1d-4013-b321-c056bd148c77.png'
JD_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20130828/eb8156e1-c2de-4cf7-9383-c4539a743546.png'
MENGBASHA_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20130828/31cd1d0b-311f-4acc-bc70-229849e2a9f7.png'
VPLUS_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20130828/fdc1286d-16c1-4a98-929c-bbf777cddc9e.png'
YIXUN_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20130828/0cee9b16-88bd-45e2-9fd5-5ac233f1990a.png'
MAIBAOBAO_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20130909/227b2e04-0adf-49b4-81fb-80470e3f4384.png'
YINTAI_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20130909/45bea6ee-7121-4d78-b441-cc9a0f3033d9.jpg'
LEFENG_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20140226/20d4157a-c822-4638-a4c7-a697e35db80d.png'
VIP_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20140226/8628f2f7-bb6c-446d-b97c-63dc7e80248b.png'
ECSHOP_CHANNEL_PIC_URL = CDN_PREFIX() + 'images/images/20150307/a6463948-6aa0-4cec-9eae-58298cd78df5.png'

IGNORE_CPS_PREFIX = ['taobao://', 'itaobao://', 'intent://',]
#IGNORE_CPS_PREFIX = []
WEB_AD_BLOCKER = '''if(location.hostname=='m.kiees.cn'&&window.jQuery){var dTable=$('#content').parents('table');dTable.siblings('table').remove();}var style=document.createElement('style');var aStyle=[];style.innerHTML=aStyle.join('');document.getElementsByTagName('head')[0].appendChild(style);'''

CHANNEL_DICT = {
        CHANNEL_DEFAULT:{
            'CHANNEL_NAME':u'链接详情',
            'CHANNEL_PIC_URL':'',
            },
        CHANNEL_TAOBAO:{
            'CHANNEL_NAME':u'来自淘宝',
            'CHANNEL_PIC_URL':TAOBAO_CHANNEL_PIC_URL,
            },
        CHANNEL_TMALL:{
            'CHANNEL_NAME':u'来自天猫',
            'CHANNEL_PIC_URL':TMALL_CHANNEL_PIC_URL,
            },
        CHANNEL_AMAZON:{
            'CHANNEL_NAME':u'来自亚马逊',
            'CHANNEL_PIC_URL':AMAZON_CHANNEL_PIC_URL,
            },
        CHANNEL_DANGDANG:{
            'CHANNEL_NAME':u'来自当当',
            'CHANNEL_PIC_URL':DANGDANG_CHANNEL_PIC_URL,
            },
        CHANNEL_VANCL:{
            'CHANNEL_NAME':u'来自凡客',
            'CHANNEL_PIC_URL':VANCL_CHANNEL_PIC_URL,
            },
        CHANNEL_JD:{
            'CHANNEL_NAME':u'来自京东',
            'CHANNEL_PIC_URL':JD_CHANNEL_PIC_URL,
            },
        CHANNEL_MENGBASHA:{
            'CHANNEL_NAME':u'来自梦芭莎',
            'CHANNEL_PIC_URL':MENGBASHA_CHANNEL_PIC_URL,
            },
        CHANNEL_VPLUS:{
            'CHANNEL_NAME':u'来自V+',
            'CHANNEL_PIC_URL':VPLUS_CHANNEL_PIC_URL,
            },
        CHANNEL_MAIBAOBAO:{
            'CHANNEL_NAME':u'来自麦包包',
            'CHANNEL_PIC_URL':MAIBAOBAO_CHANNEL_PIC_URL,
            },
        CHANNEL_YIXUN:{
            'CHANNEL_NAME':u'来自易迅',
            'CHANNEL_PIC_URL':YIXUN_CHANNEL_PIC_URL,
            },
        CHANNEL_YINTAI:{
            'CHANNEL_NAME':u'来自银泰',
            'CHANNEL_PIC_URL':YINTAI_CHANNEL_PIC_URL,
            },
        CHANNEL_LEFENG:{
            'CHANNEL_NAME':u'来自乐蜂',
            'CHANNEL_PIC_URL':LEFENG_CHANNEL_PIC_URL,
            },
        CHANNEL_VIP:{
            'CHANNEL_NAME':u'来自唯品会',
            'CHANNEL_PIC_URL':VIP_CHANNEL_PIC_URL,
            },
        CHANNEL_ECSHOP:{
            'CHANNEL_NAME':u'来自商城',
            'CHANNEL_PIC_URL':ECSHOP_CHANNEL_PIC_URL,
            },
        }

#############################################################################
# HOME CATEGORY SECTION

class HOME_CATEGORY():
    CATEGORY_QUERY_STR_LAST = u'最新'
    CATEGORY_QUERY_STR_HOT = u'热门榜'
    CATEGORY_QUERY_STR_EURO = u'欧美'
    CATEGORY_QUERY_STR_JPKR = u'日韩'
    CATEGORY_QUERY_STR_LOCAL = u'本土'
    CATEGORY_QUERY_STR_SOAP = u'热播'
    CATEGORY_QUERY_STR_MALE = u'男模明星'
    CATEGORY_QUERY_STR_DATE = u'约会'
    CATEGORY_QUERY_STR_WORK = u'职场'
    CATEGORY_QUERY_STR_VACA = u'度假'
    CATEGORY_QUERY_STR_LEISURE = u'休闲'
    CATEGORY_QUERY_STR_GUESS = u'猜你喜欢'
    CATEGORY_QUERY_STR_SELFIE = u'优选'

    CATEGORY_STR_LAST_1 = u'最新'
    CATEGORY_STR_LAST = u'全部'
    CATEGORY_STR_HOT = u'热门榜'
    CATEGORY_STR_HOT_1 = u'热门'
    CATEGORY_STR_EURO = u'欧美'
    CATEGORY_STR_JPKR = u'日韩'
    CATEGORY_STR_LOCAL = u'本土'
    CATEGORY_STR_SOAP = u'热播'
    CATEGORY_STR_MALE = u'hi潮男'
    CATEGORY_STR_MALE_NEW = u'潮男'
    CATEGORY_STR_DATE = u'约会'
    CATEGORY_STR_WORK = u'职场'
    CATEGORY_STR_VACA = u'度假'
    CATEGORY_STR_LEISURE = u'休闲'
    CATEGORY_STR_GUESS = u'猜你喜欢'
    CATEGORY_STR_SELFIE = u'优选'


class TOPIC_CATEGORY():
    class STR():
        DEFAULT = u'全部'
        CHAOXUN = u'潮讯'
        SHEWU = u'奢品'
        SHEWU1 = u'奢物'
        DIANPING = u'点评'
        XINGNAN = u'型男'
        CHUANDA = u'穿搭'
        FENGGE = u'风格'
        MEIRONG = u'美容'
        DAKA = u'大咖'
        XINGZUO = u'星座'
        GEWU = u'格物'
        LVXING = u'旅行'
        BAGUA = u'八卦'
        TOP10 = u'TOP10'
        ZHANBU = u'占卜'
        HUAJIA = u'花嫁'
        XIANGMAI = u'想买'
        QITA = u'其它'
        CHAOLIU = u'潮流'
        MEIDA = u'美搭'
        SHENGHUO = u'生活'
        LEHUO = u'乐活'
        YULE = u'娱乐'
        REBO = u'热播'
        REJU = u'热剧'
        LAPING = u'辣评'
        JIEPAI = u'街拍'
        NVSHEN = u'女神'
        MANHUA = u'漫画'

    class TYPE():
        DEFAULT = u''
        CHAOXUN = u'潮流资讯'
        SHEWU = u'精品鉴赏'
        DIANPING = u'穿搭点评'
        XINGNAN = u'型男'
        CHUANDA = u'穿衣战术'
        FENGGE = u'风格馆'
        MEIRONG = u'爱美达人'
        DAKA = u'热门大咖'
        XINGZUO = u'星座'
        GEWU = u'创意时尚生活'
        LVXING = u'时尚旅行'
        BAGUA = u'每日娱乐星播报'
        TOP10 = u'top10'
        ZHANBU = u'占卜'
        HUAJIA = u'花嫁'
        XIANGMAI = u'想买'
        CHAOLIU = u'潮流'
        MEIDA = u'美搭'
        JIEPAI = u'街拍'
        YULE = u'娱乐'
        REBO = u'热播'
        LAPING = u'辣评'
        MEIRONG = u'美容'
        SHENGHUO = u'生活'
        XINGZUO = u'星座'
        REJU = u'热剧'
        NVSHEN = u'女神的新衣'
        MANHUA = u'漫画'

    MOBILE_CATEGORYS = [
        {
            'name':STR.DEFAULT,
            'picUrl': CDN_PREFIX() + 'images/images/20140310/8130523b-ecaf-4a46-8436-9f34f5e5cde9.png',
        },
        {
            'name':STR.NVSHEN,
            'picUrl': CDN_PREFIX() + 'images/images/20140825/4103bf27-83c5-4cc4-9986-bba4960153f3.png',
        },
        {
            'name':STR.XIANGMAI,
            'picUrl': CDN_PREFIX() + 'images/images/20140310/45c7a04e-d0cf-4677-8a72-a69c2c5553f2.png',
        },
        {
            'name':STR.CHAOLIU,
            'picUrl': CDN_PREFIX() + 'images/images/20140310/a705c7af-172a-4a59-a5c8-fc3c454d339f.png',
        },
        {
            'name':STR.MEIDA,
            'picUrl': CDN_PREFIX() + 'images/images/20140310/9cb1989e-5d0f-4f29-b3a9-4f7a13187e6b.png',
        },
        {
            'name':STR.JIEPAI,
            'picUrl': CDN_PREFIX() + 'images/images/20140310/8f64b315-2bc1-4dbe-8602-23597b2521d4.png',
        },
        {
            'name':STR.YULE,
            'picUrl': CDN_PREFIX() + 'images/images/20140310/fd2103e6-0717-4ea6-82e0-df368240025b.png',
        },
        {
            'name':STR.REJU,
            'picUrl': CDN_PREFIX() + 'images/images/20140310/57f585bd-3df2-4080-ad39-e3da6c1fbf1a.png',
        },
        {
            'name':STR.LAPING,
            'picUrl': CDN_PREFIX() + 'images/images/20140310/c6ec4c56-d774-4c23-9d79-74a1feee8916.png',
        },
        {
            'name':STR.MEIRONG,
            'picUrl': CDN_PREFIX() + 'images/images/20140310/39f00a61-899b-4c6e-8ba2-292e530b41be.png',
        },
        {
            'name':STR.XINGZUO,
            'picUrl': CDN_PREFIX() + 'images/images/20140310/762d2273-2d1f-419b-b9aa-19604687ebf9.png',
        },
        {
            'name':STR.LEHUO,
            'picUrl': CDN_PREFIX() + 'images/images/20140310/365b6500-d925-431a-9b49-d1b9e2a496d9.png',
        },
        {
            'name':STR.MANHUA,
            'picUrl': CDN_PREFIX() + 'images/images/20150112/73dd7e1f-1648-4ac7-ad5c-476bc108e3d1.png',
        },
        ]

    CATEGORY_DICT = {
        STR.DEFAULT:TYPE.DEFAULT,
        STR.CHAOXUN:TYPE.CHAOLIU,
        STR.SHEWU:TYPE.CHAOLIU,
        STR.SHEWU1:TYPE.CHAOLIU,
        STR.DIANPING:TYPE.LAPING,
        STR.XINGNAN:TYPE.YULE,
        STR.CHUANDA:TYPE.MEIDA,
        STR.FENGGE:TYPE.MEIDA,
        STR.MEIRONG:TYPE.MEIRONG,
        STR.DAKA:TYPE.REBO,
        STR.XINGZUO:TYPE.XINGZUO,
        STR.GEWU:TYPE.SHENGHUO,
        STR.LVXING:TYPE.SHENGHUO,
        STR.BAGUA:TYPE.YULE,
        STR.TOP10:TYPE.JIEPAI,
        STR.ZHANBU:TYPE.SHENGHUO,
        STR.HUAJIA:TYPE.CHAOLIU,
        STR.XIANGMAI:TYPE.XIANGMAI,
        STR.CHAOLIU:TYPE.CHAOLIU,
        STR.MEIDA:TYPE.MEIDA,
        STR.SHENGHUO:TYPE.SHENGHUO,
        STR.YULE:TYPE.YULE,
        STR.REBO:TYPE.REJU,
        STR.LAPING:TYPE.LAPING,
        STR.JIEPAI:TYPE.JIEPAI,
        STR.REJU:TYPE.REJU,
        STR.LEHUO:TYPE.SHENGHUO,
        STR.NVSHEN:TYPE.NVSHEN,
        STR.MANHUA:TYPE.MANHUA,
        }

    TYPE_2_STR_DICT = {
        TYPE.DEFAULT:STR.QITA,
        TYPE.CHAOXUN:STR.CHAOLIU,
        TYPE.SHEWU:STR.CHAOLIU,
        TYPE.DIANPING:STR.LAPING,
        TYPE.XINGNAN:STR.YULE,
        TYPE.CHUANDA:STR.MEIDA,
        TYPE.FENGGE:STR.MEIDA,
        TYPE.MEIRONG:STR.MEIRONG,
        TYPE.DAKA:STR.REBO,
        TYPE.XINGZUO:STR.XINGZUO,
        TYPE.GEWU:STR.LEHUO,
        TYPE.LVXING:STR.LEHUO,
        TYPE.BAGUA:STR.YULE,
        TYPE.TOP10:STR.JIEPAI,
        TYPE.ZHANBU:STR.LEHUO,
        TYPE.HUAJIA:STR.CHAOLIU,
        TYPE.XIANGMAI:STR.XIANGMAI,
        TYPE.CHAOLIU:STR.CHAOLIU,
        TYPE.MEIDA:STR.MEIDA,
        TYPE.SHENGHUO:STR.LEHUO,
        TYPE.YULE:STR.YULE,
        TYPE.REBO:STR.REJU,
        TYPE.LAPING:STR.LAPING,
        TYPE.JIEPAI:STR.JIEPAI,
        TYPE.REJU:STR.REJU,
        TYPE.NVSHEN:STR.NVSHEN,
        TYPE.MANHUA:STR.MANHUA,
        }

    TYPE_2_INT = {
        TYPE.DEFAULT:0,
        TYPE.CHAOXUN:1,
        TYPE.SHEWU:2,
        TYPE.DIANPING:3,
        TYPE.XINGNAN:4,
        TYPE.CHUANDA:5,
        TYPE.FENGGE:6,
        TYPE.MEIRONG:7,
        TYPE.DAKA:8,
        TYPE.XINGZUO:9,
        TYPE.GEWU:10,
        TYPE.LVXING:11,
        TYPE.BAGUA:12,
        TYPE.TOP10:13,
        TYPE.ZHANBU:14,
        TYPE.HUAJIA:15,
        TYPE.XIANGMAI:16,
        TYPE.NVSHEN:17,
        }

CATEGORY_DICT = {
        HOME_CATEGORY.CATEGORY_STR_LAST : HOME_CATEGORY.CATEGORY_QUERY_STR_LAST,
        HOME_CATEGORY.CATEGORY_STR_LAST_1 : HOME_CATEGORY.CATEGORY_QUERY_STR_LAST,
        HOME_CATEGORY.CATEGORY_STR_HOT : HOME_CATEGORY.CATEGORY_QUERY_STR_HOT,
        HOME_CATEGORY.CATEGORY_STR_HOT_1 : HOME_CATEGORY.CATEGORY_QUERY_STR_HOT,
        #HOME_CATEGORY.CATEGORY_STR_EURO : HOME_CATEGORY.CATEGORY_QUERY_STR_EURO,
        #HOME_CATEGORY.CATEGORY_STR_JPKR : HOME_CATEGORY.CATEGORY_QUERY_STR_JPKR,
        #HOME_CATEGORY.CATEGORY_STR_LOCAL : HOME_CATEGORY.CATEGORY_QUERY_STR_LOCAL,
        #HOME_CATEGORY.CATEGORY_STR_SOAP : HOME_CATEGORY.CATEGORY_QUERY_STR_SOAP,
        #HOME_CATEGORY.CATEGORY_STR_MALE : HOME_CATEGORY.CATEGORY_QUERY_STR_MALE,
        #HOME_CATEGORY.CATEGORY_STR_DATE : HOME_CATEGORY.CATEGORY_QUERY_STR_DATE,
        #HOME_CATEGORY.CATEGORY_STR_WORK : HOME_CATEGORY.CATEGORY_QUERY_STR_WORK,
        #HOME_CATEGORY.CATEGORY_STR_VACA : HOME_CATEGORY.CATEGORY_QUERY_STR_VACA,
        #HOME_CATEGORY.CATEGORY_STR_LEISURE : HOME_CATEGORY.CATEGORY_QUERY_STR_LEISURE,
        #HOME_CATEGORY.CATEGORY_STR_MALE_NEW : HOME_CATEGORY.CATEGORY_QUERY_STR_MALE,
        HOME_CATEGORY.CATEGORY_STR_GUESS : HOME_CATEGORY.CATEGORY_QUERY_STR_GUESS,
        HOME_CATEGORY.CATEGORY_STR_SELFIE : HOME_CATEGORY.CATEGORY_QUERY_STR_SELFIE,
        }

CONFIG_CATEGORYS = [
        {'name':HOME_CATEGORY.CATEGORY_STR_LAST,},
        {'name':HOME_CATEGORY.CATEGORY_STR_HOT,},
        {'name':HOME_CATEGORY.CATEGORY_STR_EURO,},
        {'name':HOME_CATEGORY.CATEGORY_STR_JPKR,},
        {'name':HOME_CATEGORY.CATEGORY_STR_LOCAL,},
        {'name':HOME_CATEGORY.CATEGORY_STR_SOAP,},
        {'name':HOME_CATEGORY.CATEGORY_STR_MALE,},
        {'name':HOME_CATEGORY.CATEGORY_STR_DATE,},
        {'name':HOME_CATEGORY.CATEGORY_STR_VACA,},
        {'name':HOME_CATEGORY.CATEGORY_STR_LEISURE}
        ]

VITEM_STAR_CATEGORYS = [
        {'name':HOME_CATEGORY.CATEGORY_STR_LAST,},
        {'name':HOME_CATEGORY.CATEGORY_STR_EURO,},
        {'name':HOME_CATEGORY.CATEGORY_STR_JPKR,},
        {'name':HOME_CATEGORY.CATEGORY_STR_LOCAL,},
        {'name':HOME_CATEGORY.CATEGORY_STR_MALE_NEW,},
        {'name':HOME_CATEGORY.CATEGORY_STR_SOAP,},
        ]

INVISIBLE_TOPIC_CATEGORYS = [
        u'服搭专场',
        u'美妆专场',
]

#############################################################################
# ACTIVITY SECTION

WINNER_INFO_FORM = {
        'actionType':'dialog',
        'title':u'填写信息',
        'callbackUrl':'http://api2.hichao.com/user_activity_info',
        'params':[
            {'name':u'姓名', 'key':'name', 'value':''},
            {'name':u'联系电话', 'key':'cellphone', 'value':''},
            {'name':u'电子邮箱', 'key':'email', 'value':''},
            {'name':u'收件地址', 'key':'address', 'value':''},
            {'name':u'补充说明', 'key':'attachment', 'value':''}
            ]
        }

WINNER_SHOW_CELL = {
        'cells':[
                {
                    'height':52,
                    'width':320,
                    'y':0,
                    'x':6,
                    'component':{
                        'picUrl':CDN_PREFIX() + 'images/images/20130319/45368d89-b712-415a-8901-cdbc01c8b400.png',
                        'componentType':'cell',
                        'action':{}
                        }
                },
            ],
            'height':56
        }

#############################################################################
# FAKE_ACTION

FAKE_ACTION = {'actionType':'FAKE',}

#############################################################################
# COMMENT TYPE SECTION

COMMENT_TYPE_TOPIC_DETAIL_STR = 'topic_detail'
COMMENT_TYPE_STAR_DETAIL_STR = 'star_detail'
COMMENT_TYPE_STAR_STR = u'star'
COMMENT_TYPE_TOPIC_STR = u'topic'
COMMENT_TYPE_THREAD_STR = u'subject'
COMMENT_TYPE_THEME_STR = u'theme'
COMMENT_TYPE_NEWS_STR = u'news'
COMMENT_TYPE_STAR = 1
COMMENT_TYPE_TOPIC = 2
COMMENT_TYPE_THREAD = 3
COMMENT_TYPE_TOPIC_DETAIL = 4
COMMENT_TYPE_THEME = 5
COMMENT_TYPE_NEWS = 6

COMMENT_TYPE_DICT = {
        COMMENT_TYPE_TOPIC_DETAIL_STR:COMMENT_TYPE_TOPIC,
        COMMENT_TYPE_STAR_DETAIL_STR:COMMENT_TYPE_STAR,
        COMMENT_TYPE_STAR_STR:COMMENT_TYPE_STAR,
        COMMENT_TYPE_TOPIC_STR:COMMENT_TYPE_TOPIC,
        COMMENT_TYPE_THREAD_STR:COMMENT_TYPE_THREAD,
        COMMENT_TYPE_THEME_STR:COMMENT_TYPE_THEME,
        COMMENT_TYPE_NEWS_STR:COMMENT_TYPE_NEWS,
        }

#############################################################################
# COLLECTION TPYE SECTION

class COLLECTION_TYPE():
    ALL = u'all'
    STAR = u'star'
    SKU = u'sku'
    TOPIC = u'topic'
    THREAD = u'subject'
    NEWS = u'news'
    MIX = u'mix'
    THEME = u'theme'
    BRAND = u'brand'

    CODE = {
        ALL:0,
        STAR:1,
        SKU:2,
        TOPIC:3,
        THREAD:4,
        NEWS:5,
        MIX:6,
        THEME:7,
        BRAND:8,
    }

    TYPES = {
        0:ALL,
        1:STAR,
        2:SKU,
        3:TOPIC,
        4:THREAD,
        5:NEWS,
        6:ALL,
        7:THEME,
        8:BRAND,
    }

############################################################################
# FORUM SECTION

class FOLLOWING_TYPE():
    ALL = u'all'
    HOT = u'hot'
    DESIGN = u'design'
    STAR = u'star'

    CODE = {
        ALL:0,
        STAR:1,
        DESIGN:2,
        HOT:3,
    }

    TYPES = {
        0:ALL,
        1:STAR,
        2:DESIGN,
        3:HOT,
    }


TOP_ICON = CDN_FAST_DFS_IMAGE_PREFIX() + 'group5/M00/74/6A/wKgBfVXtOS-AEHNQAAAD7WSP_WA026.png'
FAVOR_ICON = CDN_FAST_DFS_IMAGE_PREFIX() + 'group5/M00/76/4F/wKgBf1XtOfuAY6MHAAAECrmjk4I011.png'
HAS_IMG_ICON = CDN_PREFIX() + 'images/images/20140419/594cd760-cdf3-462c-9713-f416539e9da7.png'

TANGZHU_ICON = CDN_PREFIX() + 'images/images/20140505/8a4be6c0-d7cd-4f4e-90fe-eb3370ed46c3.png'
STARUSER_ICON = CDN_PREFIX() + 'images/images/20140505/5a82f938-8c0c-4921-a857-ae304bda55da.png'

APP_LOGO = CDN_PREFIX() + 'images/images/20140507/4e327469-68ee-45cb-88f7-9e2ac5b41522.png'

DEFAULT_IMG = CDN_PREFIX() + 'images/images/20140530/5a721698-e805-490b-811c-c2a787f19571.png'
DEFAULT_TITLE_STYLE_PIC = CDN_PREFIX() + 'images/images/20150226/f318a2bb-73de-43ab-b602-afcdc8b32447.png'

ROLE_THREAD_STARUSER_ICON = CDN_PREFIX() + 'images/images/20140721/5b2c08ab-aa5f-4e72-b2c4-037e8dbdc9b2.png'
ROLE_THREAD_ADMIN_ICON = CDN_PREFIX() + 'images/images/20140721/34350779-1e7c-4667-808a-b12ebfadf266.png'
ROLE_THREAD_NV_SHEN_ICON = CDN_PREFIX() + 'images/images/20140919/75ab68f2-c64d-44e5-ada5-361731375db3.png'
ROLE_USERINFO_STARUSER_ICON = CDN_PREFIX() + 'images/images/20140721/40e5e284-7e01-492a-a2a2-71bdd16862bd.png'
ROLE_USERINFO_ADMIN_ICON = CDN_PREFIX() + 'images/images/20140721/62ae8b8a-5776-4592-9b83-64623d3d6aae.png'
ROLE_USERINFO_NV_SHEN_ICON = CDN_PREFIX() + 'images/images/20140919/044920b4-d31e-4051-9585-ad35b9b297a0.png'
THREAD_OWNER_ICON = CDN_PREFIX() + 'images/images/20140721/ee1c69f7-0592-42a4-9920-575cc705a8a5.png'
ROLE_THREAD_CUSTOM_ICON = CDN_FAST_DFS_IMAGE_PREFIX() + 'group5/M00/8F/DA/wKgBf1YCT2qABZzgAAAFggSC5YQ748.png'

ROLE_FDFS_TALENT_MEIDA = CDN_PREFIX() + 'images/images/20150521/aa142c11-44ce-4e43-95de-11ed0f19e2e5.png'
ROLE_FDFS_TALENT_MEIDA_X2 = CDN_PREFIX() + 'images/images/20150521/aa142c11-44ce-4e43-95de-11ed0f19e2e5.png'
ROLE_FDFS_TALENT_MEIRONG = CDN_PREFIX() + 'images/images/20150521/1e63c140-dd96-468d-8d2d-47d988cea224.png'
ROLE_FDFS_TALENT_MEIRONG_X2 = CDN_PREFIX() + 'images/images/20150521/1e63c140-dd96-468d-8d2d-47d988cea224.png'
ROLE_FDFS_TALENT_LEHUO = CDN_PREFIX() + 'images/images/20150521/55af9a69-805b-43e1-ba09-77f354460f26.png'
ROLE_FDFS_TALENT_LEHUO_X2 = CDN_PREFIX() + 'images/images/20150521/55af9a69-805b-43e1-ba09-77f354460f26.png'
ROLE_FDFS_TALENT_GOUWU = CDN_PREFIX() + 'images/images/20150521/55af9a69-805b-43e1-ba09-77f354460f26.png'
ROLE_FDFS_TALENT_GOUWU_X2 = CDN_PREFIX() + 'images/images/20150521/55af9a69-805b-43e1-ba09-77f354460f26.png'
ROLE_FDFS_TALENT_LIESHOU = CDN_FAST_DFS_IMAGE_PREFIX() + 'group6/M00/F4/24/wKgBjFVnzBWAV589AAAGysKQFyI668.png'
ROLE_FDFS_TALENT_LIESHOU_X2 = CDN_FAST_DFS_IMAGE_PREFIX() + 'group6/M00/F4/24/wKgBjFVnzBWAV589AAAGysKQFyI668.png'
ROLE_FDFS_ADMIN = CDN_FAST_DFS_IMAGE_PREFIX() + 'group1/M00/13/2B/wKgBV1RDl6OAWIFrAAAHFDtpYC0999.png'
ROLE_FDFS_ADMIN_X2 = CDN_FAST_DFS_IMAGE_PREFIX() + 'group1/M00/13/2B/wKgBV1RDl6OAGctgAAAJVLFfypc523.png'
ROLE_FDFS_TALENT_PAJIE = CDN_FAST_DFS_IMAGE_PREFIX() + 'group6/M00/36/E8/wKgBjFWfMoKAHK5pAAAKpepnEwY128.png'
ROLE_FDFS_TALENT_PAJIE_X2 = CDN_FAST_DFS_IMAGE_PREFIX() + 'group6/M00/36/E8/wKgBjFWfMoKAHK5pAAAKpepnEwY128.png'
ROLE_FDFS_TALENT_JIAJU = CDN_FAST_DFS_IMAGE_PREFIX() + 'group5/M00/F8/9B/wKgBfVWfMveAW67nAAAKxo0QzKw874.png'
ROLE_FDFS_TALENT_JIAJU_X2 = CDN_FAST_DFS_IMAGE_PREFIX() + 'group5/M00/F8/9B/wKgBfVWfMveAW67nAAAKxo0QzKw874.png'
ROLE_FDFS_TALENT_QINGGAN = CDN_FAST_DFS_IMAGE_PREFIX() + 'group6/M00/37/15/wKgBjFWfRASAGZwzAAAJdq-M1H0141.png'
ROLE_FDFS_TALENT_QINGGAN_X2 = CDN_FAST_DFS_IMAGE_PREFIX() + 'group6/M00/37/15/wKgBjFWfRASAGZwzAAAJdq-M1H0141.png'
TUANGOU_SKU_FDFS_REMAI_ICON = CDN_FAST_DFS_IMAGE_PREFIX() + 'group6/M00/68/33/wKgBjFXDNdeATJZfAAAM-00IlXc381.png'
TUANGOU_SKU_FDFS_TUIJIAN_ICON = CDN_FAST_DFS_IMAGE_PREFIX() + 'group5/M00/29/EE/wKgBfVXDNi6ABPl0AAALVSURHlk040.png'
TUANGOU_SKU_FDFS_YESHI_ICON = CDN_FAST_DFS_IMAGE_PREFIX() + 'group5/M00/2B/CC/wKgBf1XDNkCAYQeSAAAOEXEj-6Q074.png'

ROLE_FDFS_TALENT_LIST = [ROLE_FDFS_TALENT_MEIDA_X2, ROLE_FDFS_TALENT_MEIRONG_X2, ROLE_FDFS_TALENT_GOUWU_X2, ROLE_FDFS_TALENT_LEHUO_X2, ROLE_FDFS_TALENT_LIESHOU_X2, ROLE_FDFS_TALENT_PAJIE_X2, ROLE_FDFS_TALENT_JIAJU_X2, ROLE_FDFS_TALENT_QINGGAN_X2]

LEANCLOUD_APP_ID_AND_KEY = {
        "mxyc" : {
                "LEANCLOUD_APP_ID" : 'quy410gby9s3kfa4bk7vuga4bx6z36hkuurjqqd6bz8ba7jy',
                "LEANCLOUD_APP_KEY" : 'mhbcgvqoze8upmqjsxnhxn8pbfitdl8x2usqn650dv00zggi',
            },
        "Look" : {
                "LEANCLOUD_APP_ID" : '020pwn5tyad6onvaaxasbvp15cq1buo2dfzl7naafx45qbvh',
                "LEANCLOUD_APP_KEY" : '40a6p8ztscs0lb15m31w5yvx6e7af9jyh8u1iao628o4xout',
            },
        "taofener" : {
                "LEANCLOUD_APP_ID" : '2edlrmw0knlwwejso7nii5rb3vksuad1ylxkdp5izom2ajso',
                "LEANCLOUD_APP_KEY" : 'idg3tlimq0gtxv6k8xnqgs9tdqpwk2shgjbo26tu2c3ecfix',
            },
        "customer" : {
                "LEANCLOUD_APP_ID" : '8dahdfi7hmw7oifpdxxjjtjftpon8vw3mj819nwqsh1er6gu',
                "LEANCLOUD_APP_KEY" : '81o75m0vr2z7a19s7f5tdyc12leqtcxovsk54tm0hktwvbqj',
            },
        "SMS_notice" : {
                "LEANCLOUD_APP_ID" : '8dahdfi7hmw7oifpdxxjjtjftpon8vw3mj819nwqsh1er6gu',
                "LEANCLOUD_APP_KEY" : '81o75m0vr2z7a19s7f5tdyc12leqtcxovsk54tm0hktwvbqj',
            }
    }

###########################################################################
# CUSTOMER SERVICE SECTION

CUSTOMER_SERVICE_PHONE_NUMBER = '400-650-6468'

############################################################################
# SHOP SECTION

COUPON_URL = 'http://api.mall.hichao.com/hichao/promote/getpromote.php?promote_id={0}&type=promote'
BONUS_URL = 'http://api.mall.hichao.com/hichao/promote/getpromote.php?promote_id={0}&type=bonus'
BUTIE_ICON = CDN_FAST_DFS_IMAGE_PREFIX() + 'group6/M00/1B/0A/wKgBjVY7MA-ASpINAAAIlg-sNgc779.png'
SOLD_OUT = CDN_FAST_DFS_IMAGE_PREFIX() + 'group5/M00/B5/18/wKgBf1VlZQCANOdqAABIBHl6OaM900.png'

############################################################################
# MEMBER SECTION

MEMBER_RANK_0 = CDN_PREFIX() + 'images/images/20150414/2f613e66-e831-47f8-879b-27cde14c0874.png'
MEMBER_RANK_1 = CDN_PREFIX() + 'images/images/20150414/1904681d-4bd0-4c71-a696-5467269c0a7f.png'
MEMBER_RANK_2 = CDN_PREFIX() + 'images/images/20150414/002c9814-b654-489c-98af-4f141ca5167f.png'
MEMBER_RANK_3 = CDN_PREFIX() + 'images/images/20150414/f06205fc-9357-46b0-92ce-d20ea7394fd9.png'
MEMBER_RANK_4 = CDN_FAST_DFS_IMAGE_PREFIX() + 'group5/M00/94/F9/wKgBf1YE-cWAR4IMAAAGW8X0-u8099.png'
MEMBER_RANKS = {
    0:MEMBER_RANK_0,
    1:MEMBER_RANK_1,
    2:MEMBER_RANK_2,
    3:MEMBER_RANK_3,
    4:MEMBER_RANK_4,
}

############################################################################
# STAR_COPYRIGHT_INFO
STAR_COPYRIGHT_INFO = '''该图片产生的收益部分，明星衣橱只收取部分技术服务费，图片版权方和肖像权方拥有剩余部分的收益。版权或肖像权拥有方,可以第一时间联系我们，邮箱：copyright@hichao.com''';

############################################################################
# THEME SECTION
THEME_SHARE_URL = API2_URL_DOMAIN + '/share/theme?id={0}&src=share'

############################################################################
#获取国旗的url
NATIONAL_FLAG_URL = SHOP_URL_DOMAIN + '/goodsSource/GetCountry'

############################################################################
#根据专区id获取bussiness_ids的url
BUSSINESS_IDS_URL = SHOP_URL_DOMAIN + '/businessTag/GetBusinessByTagId/'

############################################################################
#根据business_id获取每日上新数量的url
BUSSINESS_COUNT_URL = SHOP_URL_DOMAIN + '/goods/GetSaleGoodsCountByBusinessIds'

################################################################################
#通过sourceids获得ecshop单品信息
ECSHOP_SKU_INFO = SHOP_URL_DOMAIN + '/goodsSource/GetBaseGoodsInfoBySourceIds'

# 获取单品活动信息接口
SKU_ACTIVITY_URL = SHOP_URL_DOMAIN + '/ruleGoods/GetStartGoodsRule'

############################################################################
# 明星图瀑布流格子显示图标

FALL_THREAD_ICON = CDN_FAST_DFS_IMAGE_PREFIX() + 'group6/M00/A9/5A/wKgBjFXmfMGABkXlAAANBJnHZi0179.png'

ERROR_404_PAGE = H5_URL_DOMAIN + '/templates/wap/h5_web/404_error.html'

#同步红包优惠券
PROMOTE_URL = ORDER_SHOP_URL_DOMAIN + '/hichao/promote/promoteservice.php'

#订单详情页接口
ORDER_DETAIL_URL = ORDER_SHOP_URL_DOMAIN + '/hichao/interface.php'

############################################################################
# SMS_SERVICE
SMS_SERVICE_TYPE = 'weiwang' #leancloud | mandao | weiwang | all(随机选择一个)

#国家图标
from hichao.base.config.country_img import COUNTRY_NAME_IMG

#商家id换取国家id
BUSINESS_ID_TO_COUNTRY_ID_URL = SHOP_URL_DOMAIN + '/business/GetBusinessCountryId'

#精品评价图标
EVALUATION_GOOD_ICON = CDN_FAST_DFS_IMAGE_PREFIX() + 'group6/M00/70/29/wKgBjVZxQ36Ab4nYAAAIHlEQfSw964.png'
