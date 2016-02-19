# -*- coding:utf-8 -*-


from pyramid.view import (
    view_defaults,
    view_config,
)
from hichao.util.pack_data import pack_data, version_ge
from hichao.base.views.view_base import View
from hichao.util.statsd_client import statsd
from hichao.cache.cache import deco_cache, deco_cache_static_prefix
from hichao.keywords.models.classes import (
    get_classes_type_id_by_type,
    get_classes_type_id_by_f_id,
    get_region_component_by_id,
    build_regions_tag_component,
    get_classes_item_by_id,
    get_classes_by_f_id,
    get_classes_by_type_id,
    get_class_two_id,
    get_class_id_by_type_and_type_id,
    build_component_region_category_item,
    get_category_by_id,
    get_region_components_by_ids,
)
from hichao.util.object_builder import build_brand_collect_list_item_by_id,\
    build_brand_collect_list_item_by_id_with_action_type
from icehole_client.promotion_client import PromotionClient
from hichao.util.date_util import MINUTE, HOUR


@view_defaults(route_name='region_with_brands')
class RegionWithBrandsView(View):

    def __init__(self, request):
        super(RegionWithBrandsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_all.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    @deco_cache_static_prefix(prefix='interface.region_with_brands', recycle=HOUR)
    def get(self):
        result = get_classes_type_id_by_type('brand_region')
        data = {}
        data['items'] = []

        contents = get_region_components_by_ids([region.type_id for region in result])
        for item in contents:
            com = build_regions_tag_component(item, 'regionBrands', 'tagCell_v640')
            if com:
                com_data = {}
                com_type = 'BrandListCell_v640'
                if com['title'] == u'设计师':
                    com_type = 'designerCell'
                com['items'] = get_component_items_for_classes_v640(item.id, '精品品牌', com_type, 1)['items']
                com_data['component'] = com
                data['items'].append(com_data)
#         for region in result:
#             item = get_region_component_by_id(region.type_id)
#             com = build_regions_tag_component(item, 'regionBrands', 'tagCell_v640')
#             if com:
#                 com_data = {}
#                 com_type = 'BrandListCell_v640'
#                 if com['title'] == u'设计师':
#                     com_type = 'designerCell'
#                 com['items'] = get_component_items_for_classes_v640(region.type_id, '精品品牌', com_type, 1)['items']
#                 com_data['component'] = com
#                 data['items'].append(com_data)
        return '', data


# 专区精选品牌接口
@view_defaults(route_name='region_all')
class RegionAllView(View):

    def __init__(self, request):
        super(RegionAllView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_all.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        result = get_classes_type_id_by_type('brand_region')
        data = {}
        data['items'] = []
        for region in result:
            item = get_region_component_by_id(region.type_id)
            com = build_regions_tag_component(item)
            if com:
                com_data = {}
                com_data['component'] = com
                data['items'].append(com_data)
        return '', data


# 专区下全部精选品牌接口
@view_defaults(route_name='regions_brand')
class RegionsBrandView(View):

    def __init__(self, request):
        super(RegionsBrandView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_regions_brand.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        type_name = self.request.params.get('typeName', '')
        query_id = self.request.params.get('id', '')
        if not query_id:
            return '', {}
        com_type = 'BrandListCell'
        use_logo = 1
        if gf == 'iphone' and version_ge(gv, '6.3.4'):
            if type_name == '设计师' or type_name == '设计师专区':
                com_type = 'designerCell'
                use_logo = 0
        if gf == 'android' and version_ge(gv, '634'):
            if type_name == '设计师' or type_name == '设计师专区':
                com_type = 'designerCell'
                use_logo = 0
        cate_name = '品牌'
        data = get_component_items_for_classes(query_id, cate_name, com_type, use_logo)
        return '', data

# 专区精选品牌接口


@view_defaults(route_name='region_brand')
class RegionBrandView(View):

    def __init__(self, request):
        super(RegionBrandView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_regions_brand.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        query_id = self.request.params.get('id', '')
        type_name = self.request.params.get('typeName', '')
        if query_id:
            pc_item = PromotionClient().get_content_by_id(int(query_id))
            if pc_item:
                type_name = pc_item.title
        is_des = '0'
        if type_name == '设计师' or type_name == '设计师专区':
            is_des = '1'
        if not query_id:
            return '', {}
        cate_name = '精品品牌'
        data = {}
        com_type = 'BrandListCell'
        has_cate = 0
        use_logo = 1
        if gf == 'iphone' and version_ge(gv, '6.3.4'):
            com_type = 'hotCategoryCell'
            has_cate = 1
            use_logo = 0
            if version_ge(gv, '6.4.0'):
                com_type = 'BrandListCell'
            if str(is_des) == '1':
                com_type = 'designerCell'
        if gf == 'android' and version_ge(gv, '634'):
            com_type = 'hotCategoryCell'
            has_cate = 1
            use_logo = 0
            if version_ge(gv, '640'):
                com_type = 'BrandListCell'
            if str(is_des) == '1':
                com_type = 'designerCell'
        data = get_component_items_for_classes(query_id, cate_name, com_type, use_logo)
        if has_cate:
            data['categorys'] = get_items_by_type_and_type_id('region_category', int(query_id), 'hotCategoryCell', type_name)
        return '', data


def get_component_items_for_classes(query_id, cate_name, com_type='BrandListCell', use_logo=0):
    cate_id = get_class_two_id(query_id, cate_name)
    data = {}
    data['items'] = []
    if cate_id == 0:
        return data
    items = get_classes_type_id_by_f_id(cate_id)
    for item in items:
        com = build_brand_collect_list_item_by_id(item.type_id)
        if com:
            if use_logo:
                if com['component'].has_key('brandLogo'):
                    com['component']['picUrl'] = com['component']['brandLogo']
            com['component']['componentType'] = com_type
            data['items'].append(com)
    return data


def get_component_items_for_classes_v640(query_id, cate_name, com_type='BrandListCell', use_logo=0):
    cate_id = get_class_two_id(query_id, cate_name)
    data = {}
    data['items'] = []
    if cate_id == 0:
        return data
    items = get_classes_type_id_by_f_id(cate_id)
    for item in items:
        com = build_brand_collect_list_item_by_id_with_action_type(item.type_id, 'ecshopSearch')
        if com:
            if use_logo:
                if com['component'].has_key('brandLogo'):
                    com['component']['picUrl'] = com['component']['action']['picUrl']
            com['component']['componentType'] = com_type
            data['items'].append(com)
    return data


def get_items_by_type_and_type_id(type, type_id, com_type='BrandListCell', region_name=''):
    class_id = get_class_id_by_type_and_type_id(type, type_id)
    data = []
    if not class_id:
        return data
    items = get_classes_type_id_by_f_id(class_id)
    for item in items:
        com = {}
        com['component'] = {}
        item = get_category_by_id(item.type_id)
        com['component'] = build_component_region_category_item(item)
        if com:
            com['component']['componentType'] = com_type
            if region_name:
                com['component']['action']['regionName'] = region_name
                com['component']['action']['regionId'] = str(type_id)
            data.append(com)
    return data
