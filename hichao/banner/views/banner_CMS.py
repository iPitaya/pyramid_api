# -*- coding:utf-8 -*-

from hichao.util.statsd_client import timeit, statsd
from pyramid.view import (
    view_defaults,
    view_config,
)


from hichao.base.views.view_base import View
from hichao.util.pack_data import (
    pack_data,
    version_ge,
    version_gt,
    version_eq,
)
from hichao.banner.models.banner_CMS import (
    get_components_by_flags_dict,
    HOME_TAB,
    HOME_TAB_NEW,
    get_banner_components_by_flags_dict,
    HOME_AD,
    HOME_BANNER,
    MALL_BANNER,
    get_component_by_position_flag,
    MALL_AD,
    HOT_SPECIAL,
    CATEGORY_SELECTED,
    WODFAN_DAILY_LOOK,
    WODFAN_BANNER,
    get_staruser_components_by_flags_dict,
    HOT_STARUSER,
    MALL_AD_NEW,
    MALL_REGION,
    MALL_MEMBER,
    MALL_DAILY,
    DAPEI_TAG,
    MALL_TAG,
    MALL_BANNER_NEW,
    generate_promotion_key_with_attr,
    HOT_SALE,
    BANNER_APPLE,
    AD_REMIND,
    get_banner_components_by_flags_key_cache,
    get_banner_components_by_flags_key_region_cache,
    get_region_components_by_region_id,
)
from hichao.base.config import FAKE_ACTION


@view_defaults(route_name='home_tabs')
class HomeTab(View):

    def __init__(self, request):
        super(HomeTab, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_home_tabs.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'homeTabCell'
        default_dict = HOME_TAB
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        #data['items'] = get_banner_components_by_flags_dict(default_dict,comType)
        data['items'] = get_banner_components_by_flags_key_cache('HOME_TAB', comType)
        if gf == 'iphone' and version_gt('6.1.0', gv):
            data['items'] = self.update_new_version_data(data['items'])
        elif gf == 'android' and version_gt(110, gv):
            data['items'] = self.update_new_version_data(data['items'])
        return '', data

    # 强制老版本升级
    def update_new_version_data(self, items):
        for item in items:
            if item['component']['action']:
                action = item['component']['action']
                if action['actionType'] == 'jump':
                    if action['child'] == 'flashsalelist' or action['type'] == 'member':
                        action = FAKE_ACTION
                item['component']['action'] = action
        return items


@view_defaults(route_name='home_ad')
class HomeAd(View):

    def __init__(self, request):
        super(HomeAd, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_home_ad.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        null_row_support = 0
        data['items'] = get_components_by_flags_dict(HOME_AD, comType, null_row_support)
        return '', data


@view_defaults(route_name='home_banner')
class HomeBanner(View):

    def __init__(self, request):
        super(HomeBanner, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_home_banner.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        data = {}
        comType = 'cell'
        null_row_support = 0
        #data['items'] = get_banner_components_by_flags_dict(HOME_BANNER,comType,null_row_support)
        data['items'] = get_banner_components_by_flags_key_cache('HOME_BANNER', comType)
        #apple_items = get_banner_components_by_flags_dict(BANNER_APPLE,comType,null_row_support)
        apple_items = get_banner_components_by_flags_key_cache('BANNER_APPLE', comType)
        if apple_items:
            if gf == 'iphone' and version_eq(gv, apple_items[0]['component']['title']):
                item = apple_items[0]
                item['component']['action']['title'] = ''
                item['component']['action']['titleStyle'] = {}
                data['items'].insert(0, item)
        return '', data


@view_defaults(route_name='mall_banner')
class MallBanner(View):

    def __init__(self, request):
        super(MallBanner, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mall_banner.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        null_row_support = 0
        #data['items'] = get_banner_components_by_flags_dict(MALL_BANNER,comType,null_row_support)
        data['items'] = get_banner_components_by_flags_key_cache('MALL_BANNER', comType)
        return '', data


@view_defaults(route_name='brand_category_banner')
class CategoryBanner(View):

    def __init__(self, request):
        super(CategoryBanner, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_brand_category_banner.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        null_row_support = 0
        #data['items'] = get_banner_components_by_flags_dict(MALL_BANNER,comType,null_row_support)
        data['items'] = get_banner_components_by_flags_key_cache('CATEGORY_BANNER_BG', comType)
        return '', data


@view_defaults(route_name='jiaocheng')
class JiaoCheng(View):

    def __init__(self, request):
        super(JiaoCheng, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_jiaocheng.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', 0)
        if not flag:
            flag = 0
        data = {}
        comType = 'cell'
        position_name = 'bbs_teach_list'
        data = get_component_by_position_flag(position_name, comType, offset=int(flag), limit=10)
        return '', data


@view_defaults(route_name='mall_ad')
class MallAd(View):

    def __init__(self, request):
        super(MallAd, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mall_ad.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        #data['items'] = get_banner_components_by_flags_dict(MALL_AD,comType)
        data['items'] = get_banner_components_by_flags_key_cache('MALL_AD', comType)
        return '', data

# 热门专辑


@view_defaults(route_name='hot_album')
class HotSpecial(View):

    def __init__(self, request):
        super(HotSpecial, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_hot_album.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        null_row_support = 0
        #data['items'] = get_banner_components_by_flags_dict(HOT_SPECIAL,comType,null_row_support)
        data['items'] = get_banner_components_by_flags_key_cache('HOT_SPECIAL', comType)
        return '', data

# 精选 banner


@view_defaults(route_name='banner_selection')
class CategorySelect(View):

    def __init__(self, request):
        super(CategorySelect, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_banner_selection.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        #data['items'] = get_banner_components_by_flags_dict(CATEGORY_SELECTED,comType)
        data['items'] = get_banner_components_by_flags_key_cache('CATEGORY_SELECTED', comType)
        return '', data

# 我的范 主页 cms接口


@view_defaults(route_name='wodfan_page')
class WodfanPage(View):

    def __init__(self, request):
        super(WodfanPage, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_wodfan_page.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        cms_type = self.request.params.get('type', '')
        data = {}
        if not cms_type:
            return '', data
        comType = 'cell'
        dict_type_name = {}
        if cms_type == 'daily':
            dict_type_name = WODFAN_DAILY_LOOK
            #data['items'] = get_banner_components_by_flags_dict(dict_type_name,comType)
            data['items'] = get_banner_components_by_flags_key_cache('WODFAN_DAILY_LOOK', comType)
        if cms_type == 'style':
            dict_type_name = WODFAN_BANNER
            #data['items'] = get_banner_components_by_flags_dict(dict_type_name,comType, limit = 5)
            data['items'] = get_banner_components_by_flags_key_cache('WODFAN_BANNER', comType, limit=5)
        if cms_type == 'staruser':
            dict_type_name = HOT_STARUSER
            data['items'] = get_staruser_components_by_flags_dict(HOT_STARUSER)
            #data['items'] = get_banner_components_by_flags_key_cache('HOT_STARUSER',comType)
        return '', data

# 新版首页banner


@view_defaults(route_name='mall_banner_new')
class NewMallBanner(View):

    def __init__(self, request):
        super(NewMallBanner, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mall_banner_new.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        null_row_support = 0
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        if gf == 'iphone':
            if version_ge(gv, '6.4.0'):
                data['items'] = get_banner_components_by_flags_key_cache('MALL_BANNER_NEW_SQUARE', comType)
            else:
                data['items'] = get_banner_components_by_flags_key_cache('MALL_BANNER_NEW', comType)
        elif gf == 'android':
            if version_ge(gv, '640'):
                data['items'] = get_banner_components_by_flags_key_cache('MALL_BANNER_NEW_SQUARE', comType)
            else:
                data['items'] = get_banner_components_by_flags_key_cache('MALL_BANNER_NEW', comType)
        else:
            data['items'] = get_banner_components_by_flags_key_cache('MALL_BANNER_NEW', comType)
        return '', data

# 新版首页banner


@view_defaults(route_name='mall_share')
class MallShare(View):

    def __init__(self, request):
        super(MallShare, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mall_share.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        data['items'] = get_banner_components_by_flags_key_cache('MALL_SHARE', comType)
        return '', data

# 首页五个入口标签


@view_defaults(route_name='mall_tags')
class MallTag(View):

    def __init__(self, request):
        super(MallTag, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mall_tags.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        msg_type = self.request.params.get('type', '0')
        data = {}
        comType = 'homeTabCell'
        #data['items'] = get_banner_components_by_flags_dict(MALL_TAG,comType)
        if msg_type == '0':
            data['items'] = get_banner_components_by_flags_key_cache('MALL_TAG', comType)
        else:
            data['items'] = get_banner_components_by_flags_key_cache('BAOSHUICANG_TAG', comType)
        return '', data

# 首页每日上新


@view_defaults(route_name='mall_daily')
class MallDaily(View):

    def __init__(self, request):
        super(MallDaily, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mall_daily.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        data = {}
        comType = 'cell'
        null_row_support = 0
        #data['items'] = get_banner_components_by_flags_dict(MALL_DAILY,comType,null_row_support)
        components = get_banner_components_by_flags_key_cache('MALL_DAILY', comType)
        if gf == 'iphone':
            if version_ge(gv, '6.3.4'):
                data['items'] = components
            else:
                data['items'] = components[0:3]
        elif gf == 'android':
            if version_ge(gv, '634'):
                data['items'] = components
            else:
                data['items'] = components[0:3]
        else:
            data['items'] = components[0:3]

        return '', data

# 首页会员专区


@view_defaults(route_name='mall_member')
class MallMember(View):

    def __init__(self, request):
        super(MallMember, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mall_member.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        null_row_support = 0
        #data['items'] = get_banner_components_by_flags_dict(MALL_MEMBER,comType,null_row_support)
        data['items'] = get_banner_components_by_flags_key_cache('MALL_MEMBER', comType)
        return '', data

# 首页地域专区


@view_defaults(route_name='mall_region')
class MallRegion(View):

    def __init__(self, request):
        super(MallRegion, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mall_region.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        data = {}
        comType = 'sloganCell'
        null_row_support = 0
        if gf == 'iphone':
            if version_ge(gv, '6.3.4'):
                data['items'] = get_banner_components_by_flags_key_cache('MALL_REGION_NEW', comType)
            else:
                data['items'] = get_banner_components_by_flags_key_cache('MALL_REGION', comType)
        elif gf == 'android':
            if version_ge(gv, '634'):
                data['items'] = get_banner_components_by_flags_key_cache('MALL_REGION_NEW', comType)
            else:
                data['items'] = get_banner_components_by_flags_key_cache('MALL_REGION', comType)
        else:
            data['items'] = get_banner_components_by_flags_key_cache('MALL_REGION', comType)

        return '', data

# 6.4.0以上新版地域专区


@view_defaults(route_name='mall_region_new')
class MallRegionNew(View):

    def __init__(self, request):
        super(MallRegionNew, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mall_region_new.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        region_id = self.request.params.get('region_id')
        data = {}
        comType = 'cell'
        data = get_region_components_by_region_id(str(region_id))
        return '', data

# 首页通栏banner


@view_defaults(route_name='mall_ad_new')
class MallAdNew(View):

    def __init__(self, request):
        super(MallAdNew, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mall_ad_new.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        #data['items'] = get_banner_components_by_flags_dict(MALL_AD_NEW,comType)
        data['items'] = get_banner_components_by_flags_key_cache('MALL_AD_NEW', comType)
        return '', data


# 搭配tab三个推广位
@view_defaults(route_name='dapei_tag')
class DapeiTag(View):

    def __init__(self, request):
        super(DapeiTag, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_dapei_tag.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        #data['items'] = get_banner_components_by_flags_dict(DAPEI_TAG,comType)
        data['items'] = get_banner_components_by_flags_key_cache('DAPEI_TAG', comType)
        return '', data


# 专区详情 banner
@view_defaults(route_name='region_banner')
class RegionBanner(View):

    def __init__(self, request):
        super(RegionBanner, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_banner.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        cms_id = self.request.params.get('id', '')
        data = {}
        comType = 'cell'
        data['items'] = get_banner_components_by_flags_key_region_cache('REGION_BANNER', cms_id, comType)
        return '', data


# 专区优惠券
@view_defaults(route_name='region_coupon')
class RegionCoupon(View):

    def __init__(self, request):
        super(RegionCoupon, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_coupon.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        cms_id = self.request.params.get('id', '')
        data = {}
        comType = 'cell'
        data['items'] = get_banner_components_by_flags_key_region_cache('REGION_COUPON', cms_id, comType)
        return '', data


# 专区一元抢购
@view_defaults(route_name='region_panicbuy')
class RegionPanicBuy(View):

    def __init__(self, request):
        super(RegionPanicBuy, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_panicbuy.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        cms_id = self.request.params.get('id', '')
        data = {}
        comType = 'cell'
        data['items'] = get_banner_components_by_flags_key_region_cache('REGION_PANICBUY', cms_id, comType)
        return '', data


# 专区详情 通栏
@view_defaults(route_name='region_ad')
class RegionAD(View):

    def __init__(self, request):
        super(RegionAD, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_banner.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        cms_id = self.request.params.get('id', '')
        data = {}
        comType = 'cell'
        promotion_key = []
        data['items'] = get_banner_components_by_flags_key_region_cache('REGION_TONGLAN', cms_id, comType)
        return '', data

# 每日热销后的专题列表


@view_defaults(route_name='mall_daily_topics')
class MallDailyTopics(View):

    def __init__(self, request):
        super(MallDailyTopics, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_mall_daily_topics.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', 0)
        if not flag:
            flag = 0
        data = {}
        comType = 'cell'
        position_name = 'mall_daily_topics'
        data = get_component_by_position_flag(position_name, comType, offset=int(flag), limit=10)
        return '', data

# 每日热销 banner


@view_defaults(route_name='hot_sale')
class HotSale(View):

    def __init__(self, request):
        super(HotSale, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_hot_sale.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        #data['items'] = get_banner_components_by_flags_dict(HOT_SALE,comType)
        data['items'] = get_banner_components_by_flags_key_cache('HOT_SALE', comType)
        return '', data

# v6.4.0社区首页banner


@view_defaults(route_name='new_forum_banner')
class ForumBanner(View):

    def __init__(self, request):
        super(ForumBanner, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_forum_banner.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        data['items'] = get_banner_components_by_flags_key_cache('FORUM_BANNER', comType)
        return '', data


# 广告提醒 banner
@view_defaults(route_name='ad_remind')
class AdRemind(View):

    def __init__(self, request):
        super(AdRemind, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_ad_remind.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        gv = self.request.params.get('gv', '')
        gf = self.request.params.get('gf', '')
        gs = self.request.params.get('gs', '')
        data = {}
        comType = 'adCell'
        #data['items'] = get_banner_components_by_flags_dict(AD_REMIND,comType)
        data['items'] = get_banner_components_by_flags_key_cache('AD_REMIND', comType)
        if data['items']:
            data = data['items'][0]['component']
            del data['componentType']
            if gf == 'iphone':
                if version_eq(gv, '6.3.2') or version_eq(gv, '6.3.3'):
                    index = str(gs).find('x')
                    width = float(gs[0:index])
                    height = float(gs[index + 1:])
                    if width == float(1242) or width == float(1125):
                        data['width'] = str(width / 640 * (int(data['width']) / 3))
                        data['height'] = str(width / 640 * (int(data['height']) / 3))
                    else:
                        data['width'] = str(width / 640 * (int(data['width']) / 2))
                        data['height'] = str(width / 640 * (int(data['height']) / 2))
                else:
                    data['width'] = str(int(data['width']) / 2)
                    data['height'] = str(int(data['height']) / 2)
        else:
            data = {}
        return '', data


# 爱上超模demo
@view_defaults(route_name='mall_tv_ad')
class TVAd(View):

    def __init__(self, request):
        super(TVAd, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_tv_ad.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        null_row_support = 0
        data['items'] = get_banner_components_by_flags_key_cache('TV_AD', comType)
        return '', data

# 爱上超模demo banner


@view_defaults(route_name='mall_tv_banner')
class TVBanner(View):

    def __init__(self, request):
        super(TVBanner, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_tv_ad.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = {}
        comType = 'cell'
        null_row_support = 0
        data['items'] = get_banner_components_by_flags_key_cache('TV_BANNER', comType)
        return '', data

# 专区品牌推荐


@view_defaults(route_name='region_banner_brands')
class RegionBannerBrands(View):

    def __init__(self, request):
        super(RegionBannerBrands, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_banner_brands.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        cms_id = self.request.params.get('id', '')
        comType = 'cell'
        data = {
            'items': get_banner_components_by_flags_key_region_cache(
                'REGION_BRANDS', cms_id, comType)
        }
        return '', data

# 专区今日爆款


@view_defaults(route_name='region_banner_today')
class RegionBannerToday(View):

    def __init__(self, request):
        super(RegionBannerToday, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_region_banner_today.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        cms_id = self.request.params.get('id', '')
        comType = 'region_today_cell'
        data = {
            'items': get_banner_components_by_flags_key_region_cache(
                'REGION_TODAY', cms_id, comType, use_cache=False)
        }
        return '', data
