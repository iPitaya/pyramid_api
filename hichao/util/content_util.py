# -*- coding:utf-8 -*-
import re
import json
from hichao.util.cps_util import (
        get_title_style_by_link,
        get_cps_source_name,
        get_cps_source_img,
        get_cps_url,
        )
from hichao.util.short_url import generate_short_url
from icehole_client.blackhole import test_word
from icehole_client.spider_client import spider_append, spider_append_with_thread_id, spider_get
from hichao.base.config.ui_action_type import SKU_DETAIL
from hichao.util.image_url import build_crawl_small_url, build_crawl_normal_url,build_category_and_brand_image_url
from hichao.util.statsd_client import timeit
from hichao.sku.models.sku import (
        get_sku_id_by_source_sourceid,
        get_sku_by_id,
        )
from icehole_client.brand_client import BrandClient

#p = re.compile('([https?://]*?[\da-z\.-]+\.[\da-z\.]+[/\w\.-?%&=]*)', re.I)
#p = re.compile('([https?://][-A-Za-z0-9+&@#/%?=~_|!:,.;]*[-A-Za-z0-9+&@#/%=~_|])', re.I)
p = re.compile('(https?://[\w\d_\.~@!#%&_\-+=:\?/,;]*|www\.[\w\d_\.~!@#%&_\-+=:\?/,;]*)', re.I)
p_star = re.compile('.*hichao.com/star/(\d+).*')
p_topic = re.compile('.*hichao.com/topic/(\d+).*')
p_thread = re.compile('.*hichao.com/thread/(\d+).*')
p_ecshop = re.compile('.*hichao.com/goods/(\d+).*')
p_ecshop_m = re.compile('.*hichao.com/m/goods\?.*[goods_id=|source_id=](\d+).*')
p_ec_brand = re.compile('.*hichao.com/brand/(\d+).*')
short_api = 'http://s.hichao.com/'

timer = timeit('hichao_backend.util_contentutl')

def split_with_url(content):
    return p.split(content)

def content_has_urls(content):
    li = p.split(content)
    if len(li) > 1: return 1
    else: return 0

@timer
def match_urls(content):
    content_list = split_with_url(content)
    res_list = []
    for i in range(len(content_list)):
        if i % 2 > 0:
            res_list.append(content_list[i])
    return res_list

def urls_push_to_crawl(user_id, urls, thread_id):
    thread_id = int(thread_id)
    for url in urls:
        if thread_id == 0:
            spider_append(int(user_id), url)
        else:
            spider_append_with_thread_id(int(user_id), thread_id, url)

@timer
def content_to_crawl(user_id, content, thread_id = 0):
    urls = match_urls(content)
    urls_push_to_crawl(user_id, urls, thread_id)

@timer
def rebuild_content(content, user_id = 0, support_embed = 0, font_color = ''):
    content = content + ' '
    content_list = split_with_url(content)
    count = len(content_list)
    res_list = []
    for i in xrange(count):
        if i % 2 == 0:
            if content_list[i]:
                res_list.append(content_rebuilder(content_list[i], 'text', font_color = font_color))
        else:
            res_list.append(content_rebuilder(content_list[i], 'url', user_id, support_embed, font_color = font_color))
    return res_list

@timer
def rebuild_content_by_split_item(content, user_id = 0, support_embed = 0, font_color = '', inner_redirect = 0, support_brandstore = 0):
    content = content + ' '
    content_list = split_with_url(content)
    count = len(content_list)
    lite_action = 1
    con_list = []
    item_list = []
    for i in xrange(count):
        if i % 2 == 0:
            if content_list[i]:
                con_list.append(content_rebuilder(content_list[i], 'text', font_color = font_color))
        else:
            com = content_rebuilder(content_list[i], 'url', user_id, support_embed, font_color = font_color, lite_action = lite_action, inner_redirect = inner_redirect, support_brandstore = support_brandstore)
            if com:
                if com['component']['componentType'] == 'embedItem' or com['component']['componentType'] == 'brandstoreCell':
                    item_list.append(com)
                else:
                    con_list.append(com)
    return con_list, item_list

@timer
def content_rebuilder(con, _type, user_id = 0, support_embed = 0, font_color = '', lite_action = 0, inner_redirect = 0, support_brandstore = 0):
    ui = {}
    com = {}
    if _type == 'url':
        if inner_redirect:
            if con.endswith('.mp4'):
                com['componentType'] = 'msgText'
                com['text'] = u' 点击播放视频 '
                com['color'] = '255,149,171,255'
                com['style'] = 'underline'
                action = {}
                action['actionType'] = 'video'
                action['videoUrl'] = con
                com['action'] = action
                ui['component'] = com
                return ui
            inner_type = ''
            inner_type_id = 0
            r_thread = p_thread.findall(con)
            if r_thread:
                inner_type = 'thread'
                inner_type_id = r_thread[0]
            # 跳转专题会造成循环引用，暂不支持。。。
            #r_topic = p_topic.findall(con)
            #if r_topic:
            #    inner_type = 'topic'
            #    inner_type_id = r_topic[0]
            r_star = p_star.findall(con)
            if r_star:
                inner_type = 'star'
                inner_type_id = r_star[0]
            r_ecsid = p_ecshop.findall(con)
            if r_ecsid:
                inner_type = 'ec_sku'
                inner_type_id = r_ecsid[0]
            else:
                r_ecsid = p_ecshop_m.findall(con)
                if r_ecsid:
                    inner_type = 'ec_sku'
                    inner_type_id = r_ecsid[0]
            r_ec_brand = p_ec_brand.findall(con)
            if r_ec_brand:
                inner_type = 'ec_brand'
                inner_type_id = r_ec_brand[0]
            if inner_type:
                if inner_type == 'ec_sku':
                    sku_id = get_sku_id_by_source_sourceid('ecshop', inner_type_id)
                    sku = get_sku_by_id(sku_id)
                    if sku:
                        sku['support_ec'] = 1
                        com['componentType'] = 'embedItem'
                        com['picUrl'] = sku.get_small_pic_url()
                        com['description'] = sku.get_component_description()
                        com['price'] = sku.get_component_price()
                        com['channelPicUrl'] = sku.get_channel_url()
                        com['source'] = sku.get_channel_name()
                        com['action'] = sku.to_lite_ui_action()
                        ui['component'] = com
                        return ui
                elif inner_type == 'ec_brand':
                    brand = BrandClient().get_brand_info_by_brand_id(inner_type_id)
                    name = brand.brand_name
                    en_name = brand.brand_english_name
                    picUrl = brand.brand_logo
                    if support_brandstore == 0:
                        com['componentType'] = 'msgText'
                        com['text'] = '「{0}」'.format(name)
                        com['color'] = '255,149,171,255'
                        com['style'] = ''
                    else:
                        com['componentType'] = 'brandstoreCell'
                        com['title'] = name
                        com['picUrl'] = build_category_and_brand_image_url(picUrl)

                    action = {}
                    action['actionType'] = 'ecshopSearch'
                    action['id'] = str(inner_type_id)
                    action['query'] = en_name
                    action['en_title'] = en_name
                    action['title'] = name
                    com['action'] = action
                    ui['component'] = com
                    return ui
                else:
                    com['componentType'] = 'msgText'
                    #com['text'] = '{0}...'.format(con[:20])
                    com['text'] = '「查看详情」'
                    com['color'] = '255,149,171,255'
                    #com['style'] = 'underline'
                    com['style'] = ''
                    action = {}
                    action['actionType'] = 'detail'
                    action['type'] = inner_type
                    action['id'] = str(inner_type_id)
                    com['action'] = action
                    ui['component'] = com
                    return ui
        has_sku = False
        if user_id:
            try:
                sku = spider_get(int(user_id), con)
                if sku.user_id != -1: has_sku = True
            except Exception, ex:
                has_sku = False
        if not has_sku:
            com['componentType'] = 'msgText'
            #if len(con) > 20:
            #    com['text'] = '{0}...'.format(con[:20])
            #else:
            #    com['text'] = con
            com['text'] = u'「网页链接」'
            com['color'] = '255,149,171,255'
            #com['style'] = 'underline'
            com['style'] = ''
            action = {}
            action['actionType'] = 'webview'
            action['titleStyle'] = get_title_style_by_link(con)
            action['webUrl'] = pack_url(con)
            action['originUrl'] = con
            action['title'] = action['titleStyle']['text']
            action['means'] = 'push'
            com['action'] = action
        else:
            channel_img = get_cps_source_img(sku.source, sku.link)
            channel_name = get_cps_source_name(sku.source, sku.link)
            if not support_embed:
                com['componentType'] = 'msgText'
                #if len(con) > 20:
                #    com['text'] = '{0}...'.format(con[:20])
                #else:
                #    com['text'] = con
                com['text'] = u'「查看详情」'
                com['color'] = '255,149,171,255'
                #com['style'] = 'underline'
                com['style'] = ''
            else:
                com['componentType'] = 'embedItem'
                com['picUrl'] = build_crawl_small_url(sku.self_img_url)
                com['description'] = sku.title
                com['price'] = str(sku.curr_price)
                com['channelPicUrl'] = channel_img
                com['source'] = channel_name
            action = {}
            if lite_action:
                action['actionType'] = 'detail'
                action['type'] = 'sku'
                action['id'] = str(sku.sku_id)
            else:
                action['actionType'] = SKU_DETAIL
                action['price'] = str(sku.curr_price)
                action['originLink'] = sku.link
                cps_url = get_cps_url(sku.source, sku.source_id)
                if cps_url:
                    action['link'] = cps_url
                else:
                    action['link'] = sku.link
                action['id'] = str(sku.sku_id)
                action['normalPicUrl'] = build_crawl_normal_url(sku.self_img_url)
                action['description'] = sku.title
                action['channelPicUrl'] = get_cps_source_img(sku.source, sku.link)
                action['source_id'] = str(sku.source_id)
                action['source'] = channel_name
            com['action'] = action
    else:
        com['componentType'] = 'msgText'
        com['text'] = con.strip()
        if font_color:
            com['color'] = font_color
        else:
            com['color'] = '102,102,102,255'
    ui['component'] = com
    return ui

def pack_url(url):
    if not url.lower().startswith('http'):
        url = 'http://' + url
    return generate_short_url(url) + '?cps=0'

@timer
def content_has_sensitive_words(content):
    try:
        res = test_word(content.encode('utf-8'))
        if res: return 1
        else: return 0
    except Exception, ex:
        print Exception, ex
        return 0

def filter_tag(content):
    return content.replace('<', '&lt;').replace('>', '&gt;')

