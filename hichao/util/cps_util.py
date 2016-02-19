# -*- coding:utf-8 -*-

from hichao.convert_url.models.taobaoke import get_taobaoke_url, getTaobaoURL
from hichao.convert_url.models.amazon import get_amazon_url
from hichao.convert_url.models.dangdang import get_dangdang_url
from hichao.convert_url.models.maibaobao import get_maibaobao_url
from hichao.convert_url.models.vancl import get_vancl_url
from hichao.convert_url.models.vplus import get_vplus_url
from hichao.convert_url.models.mengbasha import get_mengbasha_url
from hichao.convert_url.models.jd import get_jd_url
from hichao.convert_url.models.yintai import get_yintai_url
from hichao.convert_url.models.lefeng import get_lefeng_url
from hichao.convert_url.models.vip import get_vip_url
from hichao.convert_url import CpsType
from hichao.util.statsd_client import timeit

from hichao.base.config import (
        CHANNEL_DICT,
        CHANNEL_TAOBAO,
        CHANNEL_TMALL,
        CHANNEL_AMAZON,
        CHANNEL_DANGDANG,
        CHANNEL_VANCL,
        CHANNEL_JD,
        CHANNEL_MENGBASHA,
        CHANNEL_VPLUS,
        CHANNEL_YIXUN,
        CHANNEL_MAIBAOBAO,
        CHANNEL_YINTAI,
        CHANNEL_LEFENG,
        CHANNEL_VIP,
        CHANNEL_DEFAULT,
        CHANNEL_ECSHOP,
        CDN_PREFIX,
        DEFAULT_TITLE_STYLE_PIC,
        )
import copy
from icehole_client.cps_client import CPSClient
import functools

timer = timeit('hichao_backend.util_cpsutil')

def check_cps_type(func):
    @functools.wraps(func)
    def _(self, *args, **kw):
        self.cps_type = CpsType.IPHONE
        gf = self.request.params.get('gf', '')
        if gf == 'ipad':
            self.cps_type = CpsType.IPAD
        return func(self, *args, **kw)
    return _

cps_source_dict = {
        'taobao':CHANNEL_TAOBAO,
        'tmall':CHANNEL_TMALL,
        'z':CHANNEL_AMAZON,
        'jd':CHANNEL_JD,
        'moonbasa':CHANNEL_MENGBASHA,
        'vancl':CHANNEL_VANCL,
        'dangdang':CHANNEL_DANGDANG,
        'vjia':CHANNEL_VPLUS,
        'yixun':CHANNEL_YIXUN,
        'mbaobao':CHANNEL_MAIBAOBAO,
        'yintai':CHANNEL_YINTAI,
        'lefeng':CHANNEL_LEFENG,
        'vip':CHANNEL_VIP,
        'ecshop':CHANNEL_ECSHOP,
        }

cps_title_styles_dict = {
        CHANNEL_DEFAULT:{'text':'链接详情', 'fontColor':'0,0,0,255',
            'picUrl':DEFAULT_TITLE_STYLE_PIC},
        CHANNEL_TAOBAO:{'text':'手机淘宝网', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/40b08de1-cd5c-466e-a4bf-8c236c90475c.png'},
        CHANNEL_TMALL:{'text':'手机天猫网', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/476bb59f-265c-4293-b0f8-8d308f448c79.png'},
        CHANNEL_AMAZON:{'text':'亚马逊', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/4daa17d7-64c2-429b-afaa-f3ce06bc5786.png'},
        CHANNEL_JD:{'text':'京东', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/dc450880-631b-4c0e-a24e-eb94f3a4e9bf.png'},
        CHANNEL_MENGBASHA:{'text':'梦巴莎', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/d329fd33-a730-423d-a85c-e6bd986cda01.png'},
        CHANNEL_VANCL:{'text':'凡客', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/dff955d8-4712-4e7b-9551-2c4325a41541.png'},
        CHANNEL_DANGDANG:{'text':'当当网', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/df11c7f5-08c9-4fcb-bb07-3ee369b66df8.png'},
        CHANNEL_VPLUS:{'text':'V+', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/a82dbc63-f111-466c-8f02-e8b218a2b43f.png'},
        CHANNEL_YIXUN:{'text':'易迅网', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/59461945-a379-47bb-bc9f-08ca3c512db6.png'},
        CHANNEL_MAIBAOBAO:{'text':'麦包包', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/54a3490e-9758-4e1c-b200-18e8db099d28.png'},
        CHANNEL_YINTAI:{'text':'银泰', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/56211923-6187-4faa-84d1-fe3a26cf1472.png'},
        CHANNEL_LEFENG:{'text':'乐蜂网', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/40b08de1-cd5c-466e-a4bf-8c236c90475c.png'},
        CHANNEL_VIP:{'text':'唯品会', 'fontColor':'255,255,255,255',
            'picUrl':CDN_PREFIX() + 'images/images/20131024/40b08de1-cd5c-466e-a4bf-8c236c90475c.png'},
        CHANNEL_ECSHOP:{'text':'IF', 'fontColor':'255,255,255,255',
            'picUrl':''},
        }

@timer
def get_cps_url(source, source_id, info = {}, cps_type = CpsType.IPHONE):
    client = CPSClient()
    url = client.get_cps_url_app(source_id, source, '', '', cps_type)
    return url

@timer
def get_cps_source_info(source, link, info):
    if 'taobao.com' in link: source = 'tmall'
    elif 'tmall.com' in link: source = 'tmall'
    if not cps_source_dict.get(source, ''): return ''
    return CHANNEL_DICT[cps_source_dict[source]][info]

@timer
def get_cps_source_img(source, link):
    return get_cps_source_info(source, link, 'CHANNEL_PIC_URL')

@timer
def get_cps_source_name(source, link):
    return get_cps_source_info(source, link, 'CHANNEL_NAME')

@timer
def get_cps_key(source, link):
    if 'taobao.com' in link: source = 'tmall'
    elif 'tmall.com' in link: source = 'tmall'
    return cps_source_dict.get(source, CHANNEL_DEFAULT)

@timer
def get_cps_key_by_link(link):
    domain_dict = {
            #'taobao.com':'taobao',
            'taobao.com':'tmall',
            'tmall.com':'tmall',
            'amazon':'z',
            'jd.com':'jd',
            'moonbasa.com':'moonbasa',
            'vancl.com':'vancl',
            'dangdang.com':'dangdang',
            'vjia.com':'vjia',
            'mbaobao.com':'mbaobao',
            'yintai.com':'yintai',
            'lefeng.com':'lefeng',
            'vip.com':'vip',
            }
    for k in domain_dict.keys():
        if k in link:
            return cps_source_dict.get(domain_dict[k])
    return CHANNEL_DEFAULT

@timer
def get_title_style_by_link(link):
    return copy.deepcopy(cps_title_styles_dict[get_cps_key_by_link(link)])

