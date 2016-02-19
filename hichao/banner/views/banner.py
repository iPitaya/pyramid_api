# -*- coding:utf-8 -*-

from hichao.util.statsd_client import timeit, statsd
from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.banner.models.banner import (
        get_last_banner_ids,
        get_last_banners_by_type,
        )
from hichao.banner.models.shopactivity import (
        get_shop_activity_ids,
        get_shop_category_ids,
    )
from hichao.base.views.view_base import View
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        version_gt,
        )
from hichao.topic.models.topic import get_topic_by_id
from hichao.forum.models.thread import get_thread_by_id
from hichao.util.component_builder import build_component_banner_item
from hichao.util.cps_util import get_cps_key, cps_title_styles_dict
from hichao.collect.models.thread import thread_user_count
from hichao.comment.models.comment import get_comment_count
from hichao.base.config import COMMENT_TYPE_THREAD
from hichao.cache.cache import deco_cache
from hichao.util.date_util import TEN_MINUTES
from hichao.util.image_url import (
        build_banner_group_image_url,
        build_banner_worthy_image_url,
        build_banner_topic_image_url,
        build_banner_tuangou_image_url,
        build_banner_mall_image_url,
        build_banner_nojump_image_url,
        )
from hichao.util.object_builder import (
        build_banner_item_by_topic_id,
        build_banner_item_by_thread_id,
        build_banner_item_by_tuangou_id,
        )
from icehole_client.banner_recommend_client import BannerRecommendClient
from icehole_client.files_client import get_filename as get_img_file
from random import randint
import copy
import time
from  distutils.version  import  LooseVersion

@view_defaults(route_name = 'banner')
class Banner(View):
    def __init__(self, request):
        super(Banner, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_banner.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        data = {}
        data['items'] = []
        support_tuan = 0
        support_thread = 0
        support_tuanlist = 0
        support_worthy = 0
        support_group_sku = 0
        support_webp = 0
        lite_action = 0
        gv = self.request.params.get('gv', '')
        platform = self.request.params.get('gf', '')
        gi = self.request.params.get('gi', '')
        gn = self.request.params.get('gn', '')
        gos = self.request.params.get('gos', '')
        gc = self.request.params.get('gc', '')
        if not gos: gos = '6'
        gos = float(gos[:3])
        if not gv: gv = 0
        #gv = gv_float(gv)
        if platform == 'iphone':
            if version_ge(gv, 3.5):
                support_tuan = 1
                support_thread = 1
            if version_ge(gv, 5.0):
                lite_action = 1
            if version_gt(gv, 5.0):
                support_tuanlist = 1
            if version_ge(gv, 5.2):
                support_worthy = 1
                support_group_sku = 1
            if version_ge(gv, 6.0):
                support_webp = 1
        elif platform == 'android':
            if version_ge(gv, 45):
                support_tuan = 1
                support_thread = 1
            if version_ge(gv, 50):
                lite_action = 1
                support_tuanlist = 1
            if version_ge(gv, 60):
                support_worthy = 1
                support_group_sku = 1
        elif platform == 'ipad':
            if version_gt(gv, 2.0):
                support_tuan = 1
            if version_ge(gv, 4.0):
                support_thread = 1
                support_tuanlist = 1
                support_worthy = 1
                lite_action = 1
            if version_ge(gv, 5.0):
                support_group_sku = 1
        ts = self.request.params.get('ts', '')
        if ts:
            ids = get_last_banner_ids(support_tuan, support_thread, support_worthy, support_group_sku, ts, use_cache = False)
        else:
            ids = get_last_banner_ids(support_tuan, support_thread, support_worthy, support_group_sku)
        for _id in ids:
            idx, id, tp, img_url, iid = _id
            ui = {}
            if tp == 'topic':
                ui = build_banner_item_by_topic_id(id, support_webp)
                tm = time.time()
            elif tp == 'thread' and support_thread:
                com = build_banner_item_by_thread_id(id, img_url, lite_action, support_webp)
                if com:
                    coll_count = thread_user_count(id)
                    if not coll_count: coll_count = 0
                    com['action']['collectionCount'] = str(coll_count)
                    comm_count = get_comment_count(COMMENT_TYPE_THREAD, id)
                    if not comm_count: comm_count = 0
                    com['action']['commentCount'] = str(comm_count)
                    ui['component'] = com
            elif (tp == 'tuan' or tp == 'tuanlist') and support_tuan:
                com = build_banner_item_by_tuangou_id(id, tp, support_tuanlist, support_webp)
                if com:
                    ui['component'] = com
                    if img_url:
                        img_url = build_banner_tuangou_image_url(img_url, support_webp)
                        ui['component']['picUrl'] = img_url
            elif tp == 'worthylist' and support_worthy:
                com = {}
                com['componentType'] = 'cell'
                com['action'] = {'actionType':'jump', 'type':'item', 'child':'worthylist'}
                com['picUrl'] = build_banner_worthy_image_url(img_url, support_webp)
                ui['component'] = com
            elif tp == 'groupsku' and support_group_sku:
                com = build_banner_group_sku(id, support_webp)
                ui['component'] = com
            if ui:
                if iid:
                    ui['component']['action']['bannerId'] = str(iid)
                else:
                    ui['component']['action']['bannerId'] = ui['component']['action']['id']
                data['items'].append(ui)
        tm = time.time()
        return '', data

@timeit('hichao_backend.v_banner')
@deco_cache(prefix = 'component_banner_group_sku', recycle = TEN_MINUTES)
def build_banner_group_sku(id, support_webp = 0, use_cache = True):
    client = BannerRecommendClient()
    obj = client.getRecommend(int(id))
    com = {}
    if obj.img_url:       #obj 中间返回的是一个对象 不会返回None  和其他的中间件不同 所以可以这样判断
        com['componentType'] = 'cell'
        com['picUrl'] = build_banner_group_image_url(obj.img_url, support_webp)
        action = {}
        action['actionType'] = 'group'
        action['type'] = 'sku'
        action['id'] = str(id)
        com['action'] = action
    return com

def banner_ad(gf, gv, gi, gn):
    url = 'http://yj.s.hichao.com/j7Ynbyb6mb'
    means = 'push'
    webUrl = '{0}?gf={1}&gv={2}&gi={3}&gn={4}'.format(url, gf, gv, gi, gn)
    title_style = copy.deepcopy(cps_title_styles_dict[get_cps_key('', '')])
    title_style['text'] = u'双十一必败最IN潮单榜！'
    title_style['picUrl'] = ''
    com = {'component':{
        'componentType':'cell',
        'picUrl':'http://img1.hichao.com/images/images/20141110/7a71aa32-4a3a-4ddf-8225-5b58c2b9381f.jpg',
        'action':{
            'actionType':'webview',
            'title':u'双十一必败最IN潮单榜！',
            'titleStyle':title_style,
            'means':means,
            'webUrl':webUrl,
            }}}
    return com

def banner_comment_ad(gf, gn):
    url = 'http://www.hichao.com/grade'
    means = 'push'
    webUrl = '{0}?from={1}'.format(url, gn)
    title_style = copy.deepcopy(cps_title_styles_dict[get_cps_key('', '')])
    title_style['text'] = u'评论有奖 感谢有你'
    com = {'component':{
        'componentType':'cell',
        'picUrl':'http://mxyc.qiniudn.com/images/images/20140401/1cc3451d-90d5-4b13-8f71-e0630ed25af8.jpg',
        'action':{
            'actionType':'webview',
            'title':u'评论有奖 感谢有你',
            'titleStyle':title_style,
            'means':means,
            'webUrl':webUrl,
            }}}
    return com

@view_defaults(route_name = 'banners')
class Banners(View):
    def __init__(self, request):
        super(Banners, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_banners.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        data = {}
        data['items'] = []
        ttp = self.request.matchdict.get('tp', '')
        #return '',data
        if not ttp:
            ttp = 'item'
        if ttp == 'item':
            bns = get_last_banners_by_type(ttp)
        elif ttp == 'shopactivity':
            bns = get_shop_activity_ids()
        elif ttp == 'shopcategory':
            query_id = self.request.params.get('query_id',-1)
            #query = query.strip().encode('utf-8')
            bns = get_shop_category_ids(query_id)
        else:
            return '',data
        lite_action = 1
        support_tuanlist = 1
        support_webp = 0
        is_shop = 0
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        if (version_ge(gv, '6.0') and gf == 'iphone'):
            support_webp = 1
        for bn in bns:
            ui = {}
            if ttp == 'shopactivity':
                if bn == None:
                    if len(data['items']) < 3:
                        data['items'].append(ui)
                    continue
            idx, id, tp, img_url, iid = bn
            if ttp == 'shopactivity' or ttp == 'shopcategory':
                img_url = get_img_file('shop',img_url) 
                img_url = build_banner_mall_image_url(img_url, support_webp)
                is_shop = 1
            if tp == 'topic':
                ui = build_banner_item_by_topic_id(id, support_webp)
                if img_url:
                    if not is_shop:
                        img_url = build_banner_topic_image_url(img_url, support_webp)
                if ui:
                    ui['component']['picUrl'] = img_url
            elif tp == 'thread':
                com = build_banner_item_by_thread_id(id, img_url, lite_action, support_webp)
                if com:
                    coll_count = thread_user_count(id)
                    if not coll_count: coll_count = 0
                    com['action']['collectionCount'] = str(coll_count)
                    comm_count = get_comment_count(COMMENT_TYPE_THREAD, id)
                    if not comm_count: comm_count = 0
                    com['action']['commentCount'] = str(comm_count)
                    ui['component'] = com
                    if is_shop:
                        ui['component']['picUrl'] = img_url
            elif tp == 'tuan' or tp == 'tuanlist':
                com = build_banner_item_by_tuangou_id(id, tp, support_tuanlist, support_webp)
                if com:
                    ui['component'] = com
                    if img_url:
                        if not is_shop:
                            img_url = build_banner_tuangou_image_url(img_url, support_webp)
                    ui['component']['picUrl'] = img_url
            elif tp == 'worthylist':
                com = {}
                com['componentType'] = 'cell'
                com['action'] = {'actionType':'jump', 'type':'item', 'child':'worthylist'}
                if not is_shop:
                    img_url = build_banner_worthy_image_url(img_url, support_webp)
                com['picUrl'] = img_url
                ui['component'] = com
            elif tp == 'groupsku':
                com = build_banner_group_sku(id, support_webp)
                if com:
                    ui['component'] = com
            else:
                com = {}
                com['componentType'] = 'cell'
                ui['component'] = com
                if img_url:
                    if not is_shop:
                        img_url = build_banner_nojump_image_url(img_url, support_webp)
                ui['component']['picUrl'] = img_url
                ui['component']['action'] = {}

            if ui:
                if ui['component']['action']:
                    ui['component']['action']['bannerId'] = str(iid)
                data['items'].append(ui)
            elif ttp == 'shopactivity':
                if len(data['items']) < 3:
                    data['items'].append(ui)
        return '', data


