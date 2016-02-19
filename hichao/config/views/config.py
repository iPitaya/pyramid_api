# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.config.models.splash import (
        get_last_splash_version,
        get_match_splash,
        )
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        version_eq,
        )
from hichao.base.views.view_base import View
from hichao.base.config import (
        CONFIG_CATEGORYS,
        VITEM_STAR_CATEGORYS,
        HOME_CATEGORY,
        TOPIC_CATEGORY,
        IGNORE_CPS_PREFIX,
        WEB_AD_BLOCKER,
        SHOW_SKU_IMGS,
        CUSTOMER_SERVICE_PHONE_NUMBER,
        STAR_COPYRIGHT_INFO,
        )
from hichao.banner.models.banner_CMS import get_banner_components_by_flags_key_cache
from hichao.util.object_builder import build_forum_status_by_ids
from hichao.util.statsd_client import statsd
import json
import copy
import time

category_config = {
        'version':'43',
        'starCategories':CONFIG_CATEGORYS,
        'starCopyrightInfo':STAR_COPYRIGHT_INFO,
        'vItemStarCategories':VITEM_STAR_CATEGORYS,
        'starCategoryDefault':HOME_CATEGORY.CATEGORY_STR_LAST,
        'starCategoryUI':[
            HOME_CATEGORY.CATEGORY_STR_HOT,
            HOME_CATEGORY.CATEGORY_STR_LAST,
            ],
        'showBanner':[HOME_CATEGORY.CATEGORY_STR_LAST,],
        'showTimer':[
            HOME_CATEGORY.CATEGORY_STR_EURO,
            HOME_CATEGORY.CATEGORY_STR_JPKR,
            HOME_CATEGORY.CATEGORY_STR_LOCAL,
            HOME_CATEGORY.CATEGORY_STR_SOAP,
            HOME_CATEGORY.CATEGORY_STR_MALE,
            HOME_CATEGORY.CATEGORY_STR_MALE_NEW,
            HOME_CATEGORY.CATEGORY_STR_DATE,
            HOME_CATEGORY.CATEGORY_STR_WORK,
            HOME_CATEGORY.CATEGORY_STR_VACA,
            HOME_CATEGORY.CATEGORY_STR_LEISURE,
            ],
        'countly':{
                    'host':'',
                    'appkey':'',
                    'available':'0'
            },
        'subjectCategories':{},
        'mobileSubjectCategories':{},
        'subjectCategoryDefault':'',
        'subjectCategoryUI':[],
        'topicCategories':TOPIC_CATEGORY.MOBILE_CATEGORYS,
        'mobileTopicCategories':TOPIC_CATEGORY.MOBILE_CATEGORYS,
        'topicCategoryDefault':TOPIC_CATEGORY.STR.DEFAULT,
        'topicCategoryUI':[],
        'ignoreCpsPrefix':[],
        'webAdBlocker':WEB_AD_BLOCKER,
        'showSkuImgs':SHOW_SKU_IMGS,
        'lady_duration':'60',
        'customerPhoneNumber':CUSTOMER_SERVICE_PHONE_NUMBER,
    }

iphone_app = {
        'version':'6.3.6',
        'versionName':'v6.3.6',
        'content':'''更新说明\n1、 首页全新改版，新增海外专区，让你轻轻松松海外购；\n2、 Tab栏新增购物车，让你购物更方便；\n3、 商品列表支持排序功能，更多心愿单品抢先获得；\n4、 优化商品详情页，便捷浏览100分；\n5、 品牌店全新改版，更多惊喜购不停！''',
        'uri':'',
        'url':'https://itunes.apple.com/app/id533055152?ls=1&mt=8',
        }

iphone_lite_app = {
        'version':'6.0.0',
        'versionName':'v6.0.0',
        'content':'''v6.1.0更新说明:\n1.商城全新升级改版；\n2.会员系统全新上线，会员享受更大优惠；\n3.限量抢购改为闪购，同一时段更多单品优惠；\n4.多种红包玩法，想减哪单减哪单！''',
        'uri':'',
        'url':'https://itunes.apple.com/app/id533055152?ls=1&mt=8',
        #'url':'https://itunes.apple.com/app/id641428847?ls=1&mt=8',
        }

ipad_app = iphone_app
#ipad_app = {
#        'version':'6.0.0',
#        'versionName':'v6.0.0',
#        'content':'''1. 商城全新上线，全球时尚精品一网打尽；\n2. 商城内单品直接下单，购物更方便；\n3. 商城支持支付宝、微信一键支付，安全便捷；\n4. 个人空间独立订单入口，随时查看订单状态；\n5. 添加优惠券、红包功能，享受超值优惠；\n6. UI调整优化，操作更简单！''',
#        'uri':'',
#        'url':'https://itunes.apple.com/app/id533055152?ls=1&mt=8',
#        # 'url':'https://itunes.apple.com/app/id582628075?ls=1&mt=8',       # ipad 原应用下载地址，现ipad也指向iphone应用。
#        }

android_app = {
        'version':'636',
        'versionName':'v6.3.6',
        'content':'''更新说明\n1、提升售后服务体验，购买更放心；\n2、 优化商品展示，浏览更舒心；\n3、优化部分交互体验，使用更顺心 ''',
        'uri':'http://android.hichao.com/wodfan_hichao_v6_3_6.apk ',
        'url':'',
        }

default_splash = {
        'version':'0',
        'url':'',
        }

mxyc_lite_ip_appkey = '25a28f3b1da845eccbea466dc5c7959284eb437f'
mxyc_lite_ad_appkey = '7a0f91ec0a0dde0f3516386a6bd2a7e38b8d5c18'

ADDRESS_VERSION = '4'

@view_defaults(route_name = 'config')
class Config(View):
    def __init__(self, request):
        super(Config, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_config.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        config_version = self.request.params.get('config_version', '')
        splash_version = self.request.params.get('splash_version', '')
        app_version = self.request.params.get('gv', '0') 				# generic app version
        app_from = self.request.params.get('gf', None) 					# generic app platform
        app_name = self.request.params.get('gn', '')
        screen_width = int(self.request.params.get('screen_width', 0))
        screen_height = int(self.request.params.get('screen_height', 1))
        channel = self.request.params.get('gc', '')
        global category_config
        config_version = (config_version == '' and [0,] or [int(config_version),])[0]
        splash_version = (splash_version == '' and [0,] or [int(splash_version),])[0]
        _config = copy.deepcopy(category_config)
        forum_4 = 0
        if version_ge(5.2,app_version) and app_from == 'iphone':
            forum_4 = 1
        _config['subjectCategories'] = build_forum_status_by_ids([], with_all = 0, forum_4 = forum_4)
        _config['mobileSubjectCategories'] = build_forum_status_by_ids([], with_all = 1, forum_4 = forum_4)
        _splash = {}
        if splash_version != get_last_splash_version():
            _splash = get_match_splash(screen_width, screen_height)
            if not _splash:
                _splash = default_splash
            else:
                _splash = _splash.get_dict()
        _app = {}
        if app_from == 'android':
            if android_app['version'] and not version_eq(android_app['version'], app_version):
                _app = android_app
        elif app_from == 'ipad':
            if ipad_app['version'] and not version_eq(ipad_app['version'], app_version):
                _app = ipad_app
        elif app_name == 'mxyc_ip':
            if iphone_app['version'] and not version_eq(iphone_app['version'], app_version):
                _app = iphone_app
        elif app_name == 'mxyc_lite_ip':
            if iphone_lite_app['version'] and not version_eq(iphone_lite_app['version'], app_version):
                _app = iphone_lite_app
        _config['unixtime'] = str(int(time.time()))
        _config['showCheckUpdate'] = get_update_info()
        result = {}
        result['config'] = _config
        result['splash'] = _splash
        result['app'] = _app
        result['addressVersion'] = ADDRESS_VERSION
        message = ''
        return message, result


def get_update_info():
    data = {}
    showCheckUpdate = 0
    comType = 'adCell'
    data['items'] = get_banner_components_by_flags_key_cache('UPDATE_BANNER',comType)
    if data['items']:
        showCheckUpdate = 1
    return showCheckUpdate    
