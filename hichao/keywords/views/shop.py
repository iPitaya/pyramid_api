# -*- coding:utf-8 -*-

from pyramid.view import (
    view_defaults,
    view_config,
)
from hichao.keywords.models.keywords import (
    get_hot_words,
    get_keyword_list,
    sort_keyword_list,
    build_keyword_list,
)
from hichao.keywords.models.hot_words import get_hot_words as get_find_words
from hichao.keywords.models.hot_words import (
    get_last_querys_id_by_type,
    get_querys_by_id,
    rebuild_hot_querys,
    rebuild_item_categorys,
    rebuild_shop_dress_categorys,
    rebuild_shop_dress_categorys_more,
    rebuild_shop_dress_brand,
    rebuild_shop_dress_brand_more,
    rebuild_shop_categorys_all,
    get_items_by_title_name,
    rebuild_shop_dress_categorys_one,
    rebuild_designer_brand_more,
    get_category_selection_items,
    build_component_brand,
    get_items_by_id,
    get_last_querys_by_type,
)
from hichao.util.pack_data import pack_data
from hichao.base.views.view_base import View
from hichao.topic.models.topic import get_more_app_list
from hichao.util import xpinyin
from hichao.util.statsd_client import statsd
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE
from icehole_client.brand_client import BrandClient
from hichao.util.pack_data import (
    pack_data,
    version_ge,
    version_gt,
)

Pinyin = xpinyin.Pinyin()


@view_defaults(route_name='region_category_all')
class ShopAllLayerCategory(View):
    '''
        for V6.4.0
    '''

    def __init__(self, request):
        super(ShopAllLayerCategory, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_category_with_dresses.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        version = self.request.params.get('version', '')
        version = (version and [int(version), ] or [0, ])[0]

        data = {}

        last_query = get_last_querys_by_type('mall_brand_category')
        if not last_query or version == last_query.id:
            return '', data

        querys = eval(last_query.value)
        if not querys:
            return '', {}

        data['items'] = rebuild_shop_categorys_all(querys)
        data['version'] = str(last_query.id)
        return '', data


@view_defaults(route_name='shop_dress_category')
class ShopCategoryView(View):

    def __init__(self, request):
        super(ShopCategoryView, self).__init__()
        self.request = request
        self.data_type = {'shop': 'mallcategory', 'mall': 'mall_brand_category'}

    @statsd.timer('hichao_backend.r_shop_dress_category.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        version = self.request.params.get('version', '')
        version = (version and [int(version), ] or [0, ])[0]
        cate_type = self.request.params.get('type', 'cate_main')
        _type = self.request.params.get('data_type', 'shop')
        query_id = self.request.params.get('query_id', -1)
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')

        support_brand_region = 0
        if (gf == 'iphone' and version_ge(gv, '6.1.0')) or (gf == 'android' and version_ge(gv, '110')):
            support_brand_region = 1

        #_type = 'itemcategory'
        #_type = 'mallcategory'
        #_type = data_type
        _type = self.data_type.get(_type, self.data_type['shop'])

        last_version = int(get_last_querys_id_by_type(_type))
        if version == last_version:
            return '', {}

        data = {}
        values = []
        querys = get_querys_by_id(last_version)
        if not querys:
            return '', {}
        querys = eval(querys)
        if not querys:
            return '', {}

        #method = cate_type == 'cate_main' and rebuild_shop_dress_categorys or rebuild_item_categorys

        #for query in querys: values.append(method(query))
        #query_item = querys[0]
        support_en_title = 0
        if _type == 'mall_brand_category':
            support_en_title = 1
        if cate_type == 'cate_main':
            values = rebuild_shop_dress_categorys(querys)
        if cate_type == 'cate_more':
            values = rebuild_shop_dress_categorys_more(querys)
        if cate_type == 'cate_hot' and _type == 'mall_brand_category':
            #querys = querys[:-1]
            if support_brand_region:
                querys = self.get_big_brand_region_list() + querys
            values = rebuild_shop_dress_categorys_one(querys)
        if cate_type == 'cate_select' and _type == 'mall_brand_category':
            if support_brand_region:
                querys = self.get_big_brand_region_list() + querys
            values = rebuild_shop_dress_categorys(querys, support_en_title, query_id)
            if values and support_brand_region:
                if not values[0]['items']:
                    values[0]['items'] = values[0]['brands']
        if cate_type == 'cate_main' or cate_type == 'cate_more':
            data['querys'] = values
        else:
            if len(values) > 0:
                data = values[0]
            else:
                data['items'] = []
        data['version'] = str(last_version)
        return '', data

    def get_big_brand_region_data(self, _type):
        ''' 欧美 日韩 国内品牌专区 '''
        last_version = int(get_last_querys_id_by_type(_type))
        data = {}
        querys = get_querys_by_id(last_version)
        if not querys:
            return []
        querys = eval(querys)
        if not querys:
            return []
        return querys

    def get_big_brand_region_list(self):
        brand_tab_list = ['category_om', 'category_rh', 'category_cn']
        items = []
        for tab in brand_tab_list:
            item = self.get_big_brand_region_data(tab)
            if item:
                items += item
        return items


@view_defaults(route_name='shop_dress_brand')
class ShopBrandView(View):

    def __init__(self, request):
        super(ShopBrandView, self).__init__()
        self.request = request
        self.data_type = {'shop': 'mallcategory', 'brand': 'mall_brand', 'designer': 'designer_brand'}

    @statsd.timer('hichao_backend.r_shop_dress_brand.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        version = self.request.params.get('version', '')
        version = (version and [int(version), ] or [0, ])[0]
        cate_type = self.request.params.get('type', 'brand_main')
        _type = self.request.params.get('data_type', 'shop')

        #_type = 'itemcategory'
        #_type = 'mallcategory'
        is_en = 0
        if _type == 'brand' or _type == 'designer':
            is_en = 1
        _type = self.data_type.get(_type, self.data_type['shop'])
        last_version = int(get_last_querys_id_by_type(_type))
        if version == last_version:
            return '', {}

        data = {}
        values = []
        if is_en == 1:
            querys = get_brand_info_from_icehole(last_version)
        else:
            querys = get_querys_by_id(last_version)
            if not querys:
                return '', {}
            querys = eval(querys)
        if not querys:
            return '', {}

        #method = cate_type == 'cate_main' and rebuild_shop_dress_categorys or rebuild_item_categorys

        #for query in querys: values.append(method(query))
        if is_en == 0:
            query_item = querys[-1]
        else:
            query_item = querys
        #title_name = u'品牌'
        #query_item = get_items_by_title_name(querys,title_name)
        if cate_type == 'brand_main':
            values = rebuild_shop_dress_brand(query_item, is_en)
        if cate_type == 'brand_more':
            values = rebuild_shop_dress_brand_more(query_item, is_en)

        if cate_type == 'designer_main' and _type == 'designer_brand':
            values = rebuild_designer_brand_more(query_item, is_en, 7)
        if cate_type == 'designer_more' and _type == 'designer_brand':
            values = rebuild_designer_brand_more(query_item, is_en)

        if is_en == 0:
            data['querys'] = values
        else:
            if len(values) >= 1:
                data = values[0]
        data['version'] = str(last_version)
        return '', data


@view_defaults(route_name='category_selection')
class CategorySelectionView(View):

    def __init__(self, request):
        super(CategorySelectionView, self).__init__()
        self.request = request
        self.data_type = {'shop': 'mallcategory'}

    @statsd.timer('hichao_backend.r_category_selection.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        version = self.request.params.get('version', '')
        version = (version and [int(version), ] or [0, ])[0]
        cate_type = self.request.params.get('type', 'selection')
        _type = self.request.params.get('data_type', 'shop')

        last_version = int(get_last_querys_id_by_type('selection'))
        if version == last_version:
            return '', {}
        querys = get_querys_by_id(last_version)
        if not querys:
            return '', {}
        querys = eval(querys)
        data = {}
        data = get_category_selection_items(querys)
        data['version'] = str(last_version)
        return '', data

'''
#专区精选品牌接口
@view_defaults(route_name = 'region_brand')
class RegionBrandView(View):
    def __init__(self, request):
        super(RegionBrandView, self).__init__()
        self.request = request
        self.data_type = {'shop':'mall_brand_category'}

    @statsd.timer('hichao_backend.r_region_brand.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        version = self.request.params.get('version', '')
        version = (version and [int(version),] or [0,])[0]
        query_id = self.request.params.get('id', '')
        if not query_id:
            return '',{}
        
        last_version = int(get_last_querys_id_by_type('mall_brand_type'))
        if version == last_version: return '', {}
        querys = get_querys_by_id(last_version)
        if not querys: return '', {}
        querys = eval(querys)
        querys = get_items_by_id(querys,query_id)
        if not querys:
            return '',data
        data={}
        comType = 'BrandListCell'
        actionType = 'ecshopSearch'
        items = build_component_brand(querys['items'],comType,actionType)
        data['items'] = items
        data['version'] = str(last_version)
        return '',data

#专区下全部精选品牌接口
@view_defaults(route_name = 'regions_brand')
class RegionsBrandView(View):
    def __init__(self, request):
        super(RegionsBrandView, self).__init__()
        self.request = request
        self.data_type = {'shop':'mall_brand_category'}

    @statsd.timer('hichao_backend.r_regions_brand.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        version = self.request.params.get('version', '')
        version = (version and [int(version),] or [0,])[0]
        query_id = self.request.params.get('id', '')
        if not query_id:
            return '',{}
        
        last_version = int(get_last_querys_id_by_type('mall_brand_type'))
        if version == last_version: return '', {}
        querys = get_querys_by_id(last_version)
        if not querys: return '', {}
        querys = eval(querys)
        querys = get_items_by_id(querys,query_id)
        if not querys:
            return '',{}
        data={}
        comType = 'BrandListCell'
        actionType = 'ecshopSearch'
        items = build_component_brand(querys['brands'],comType,actionType)
        data['items'] = items
        data['version'] = str(last_version)
        return '',data

#获取所有专区列表
@view_defaults(route_name = 'region_all')
class RegionAllView(View):
    def __init__(self, request):
        super(RegionAllView, self).__init__()
        self.request = request
        self.data_type = {'shop':'mall_brand_category'}

    @statsd.timer('hichao_backend.r_region_all.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        version = self.request.params.get('version', '')
        version = (version and [int(version),] or [0,])[0]
        
        last_version = int(get_last_querys_id_by_type('mall_brand_type'))
        if version == last_version: return '', {}
        querys = get_querys_by_id(last_version)
        if not querys: return '', {}
        querys = eval(querys)
        data={}
        support_en_title = 1
        comType = 'tagCell'
        actionType = 'regionBrands'
        values = rebuild_shop_dress_categorys_one(querys, comType, actionType)
        if len(values) > 0:
            data = values[0]
        else:
            data['items'] = []
        data['version'] = str(last_version)
        return '',data
'''


@deco_cache(prefix='brand_info', recycle=MINUTE)
def get_brand_info_from_icehole(last_version):
    return BrandClient().get_brand_info_list_by_updown_all_id(last_version)
