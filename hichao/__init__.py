
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os

from pyramid.config import Configurator
from pyramid.renderers import JSONP
import ConfigParser


def main(global_config, **settings):
    ''' This function returns a Pyramid WSGI application.
    '''
    file_name = global_config['__file__']
    cf = ConfigParser.ConfigParser()
    cf.read(file_name)
    procname = cf.get('uwsgi', 'procname')
    os.environ['procname'] = procname
    config = Configurator(settings=settings)
    config.add_renderer('jsonp', JSONP(param_name='callback'))
    config.include('pyramid_mako')
    config.add_mako_renderer('.html')
    config.add_route('points_system', '/points_system/{fizzle:.*}')
    config.add_static_view('/static', 'hichao:templates/points_system', cache_max_age=3600)
    config.add_route('connect_weibo_authorize', '/connect/weibo/authorize')
    config.add_route('connect_weibo', '/connect/weibo')
    config.add_route('connect_weibo_sso', '/connect/weibo_sso')
    config.add_route('connect_qq_authorize', '/connect/qq/authorize')
    config.add_route('connect_qq', '/connect/qq')
    config.add_route('connect_qq_sso', '/connect/qq_sso')
    config.add_route('connect_taobao_authorize', '/connect/taobao/authorize')
    config.add_route('connect_taobao', '/connect/taobao')
    config.add_route('connect_taobao_sso', '/connect/taobao_sso')
    config.add_route('connect_auth2_token', '/connect/auth2/token')
    config.add_route('users', '/users')
    config.add_route('comments', '/comments')
    config.add_route('collections', '/collections')
    config.add_route('collection_ids', '/collection_ids')
    config.add_route('collection_ids_web', '/collection_ids/web')
    config.add_route('collection_merger', '/collection_merger')
    config.add_route('config', '/config')
    config.add_route('stars', '/stars')
    config.add_route('star_clues', '/star_clues')
    config.add_route('topics', '/topics')
    config.add_route('topic', '/topic')
    config.add_route('banner', '/banner')
    config.add_route('banners', '/banner/{tp}')
    config.add_route('keywords', '/keywords')
    config.add_route('search', '/search')
    config.add_route('device', '/device')
    config.add_route('android_push', '/android_push')
    config.add_route('search_list', '/search_list')
    config.add_route('feedback', '/feedback')
    config.add_route('more_apps', '/more_apps')
    config.add_route('third_party_share', '/third_party_share')
    config.add_route('user_activity_info', '/user_activity_info')
    config.add_route('topic_detail_without_cache', '/topic_detail_without_cache')
    config.add_route('img_upload_token', '/upload_token')
    config.add_route('qiniu_img_upload', '/qiniu_img_upload')
    config.add_route('img_upload_check', '/upload_check')
    config.add_route('exchange_access_token', '/exchange_access_token')
    config.add_route('thread', '/thread')
    config.add_route('threads', '/threads')
    config.add_route('hi_zone', '/hi_zone')
    config.add_route('check_subject_permission', '/check_subject_permission')
    config.add_route('sku_imgs', '/sku_imgs')
    config.add_route('hotwords', '/hotwords')
    config.add_route('items', '/items')
    config.add_route('notification_num', '/notification_num')
    config.add_route('new_forum_thread', '/new_forum/thread')
    config.add_route('new_forum_threads', '/new_forum/threads')
    config.add_route('new_forum_follow', '/new_forum/follow')
    config.add_route('new_forum_hots', '/new_forum/hots')
    config.add_route('new_forum_banner', '/new_forum/banner')
    config.add_route('new_forum_navigator', '/new_forum/navigator')
    config.add_route('new_forum_tag_threads', '/new_forum/tag/threads')
    config.add_route('following_ids', '/following_ids')
    config.add_route('starusers', '/new_forum/starusers')
    config.add_route('banwu_team', '/new_forum/banwu_team')
    config.add_route('sub_thread', '/new_forum/sub_thread')
    config.add_route('report', '/new_forum/report')
    config.add_route('message', '/message')
    config.add_route('follow', '/follow')
    config.add_route('user_info', '/user_info')
    config.add_route('official_message', '/official_message')
    config.add_route('message_reply', '/message/reply')
    config.add_route('sku_bind_stars', '/sku/bind_stars')
    config.add_route('new_forum_status', '/new_forum/status')
    config.add_route('suggester', '/sug')
    config.add_route('star', '/star')
    config.add_route('query', '/query')
    config.add_route('sku', '/sku')
    config.add_route('focus', '/focus')
    config.add_route('worthy_sku', '/worthy_sku')
    config.add_route('group_sku', '/group_sku')
    config.add_route('nvshen', '/nv_shen')
    config.add_route('cart', '/cart/{third_party}')
    config.add_route('order', '/order/{third_party}')
    config.add_route('express', '/express/{third_party}')
    config.add_route('event_nv_shen', '/event/nv_shen')
    config.add_route('event_nv_shen_quan', '/event/nv_shen/quan')
    config.add_route('event_nv_shen_info', '/event/nv_shen/info')
    config.add_route('event_nv_shen_user_info', '/event/nv_shen/user_info')
    config.add_route('event_nv_shen_check_order', '/event/nv_shen/check_order')
    config.add_route('tuan_list', '/tuanlist')
    config.add_route('tuan', '/tuan')
    config.add_route('tuan_sku_count', '/tuan_sku_attend')
    config.add_route('tuan_sku_normal', '/tuan_sku_normal')
    config.add_route('update_info', '/update_info')
    config.add_route('tuan_state', '/tuan_state')
    config.add_route('location', '/location')
    config.add_route('background', '/background')
    config.add_route('collect_state', '/collect_state')
    config.add_route('shop_dress_category', '/shop_dress_category')
    config.add_route('shop_dress_brand', '/shop_dress_brand')
    config.add_route('cdn_hosts', '/cdn_hosts')
    config.add_route('hide_edit_info', '/hide_edit_info')
    config.add_route('panic_buying', '/mall/panic_buying')
    config.add_route('message_classify', '/message/classify')
    config.add_route('message_reset_notify', '/message/reset_notify')
    config.add_route('p', '/p')
    config.add_route('user_register', '/user/user_register')
    config.add_route('send_SMS', '/user/send_SMS')
    config.add_route('send_SMS_customer', '/customer/send_SMS')
    config.add_route('send_SMS_notice', '/notice/send_SMS')
    config.add_route('find_password', '/user/find_password')
    config.add_route('change_password', '/user/change_password')
    config.add_route('change_nickname', '/user/change_nickname')
    config.add_route('cms_splash', '/splash')
    config.add_route('src2sku', '/sku/src2sku')
    config.add_route('home_tabs', '/cms/home_tabs')
    config.add_route('home_ad', '/cms/home_ad')
    config.add_route('home_banner', '/cms/home_banner')
    config.add_route('mall_banner', '/cms/mall_banner')
    config.add_route('jiaocheng', '/cms/jiaocheng')
    config.add_route('mall_ad', '/cms/mall_ad')
    config.add_route('update_avatar', '/user/update_avatar')
    config.add_route('check_update', '/config/check_update')
    config.add_route('device_state', '/device/state')
    config.add_route('device_push_state', '/device/push_state')
    config.add_route('hot_starusers', '/hot_starusers')
    config.add_route('member_daily_skus', '/member/daily_skus')
    config.add_route('statistics_info', '/statistics/info')
    config.add_route('splash', '/cms/splash')
    config.add_route('hot_album', '/cms/album')
    config.add_route('banner_selection', '/cms/category_selection')
    config.add_route('choiceness_threads', '/new_forum/daily_recommend')
    config.add_route('wodfan_page', '/cms/wodfan')
    config.add_route('theme', '/theme')
    config.add_route('themes', '/themes')
    config.add_route('theme_tags', '/theme_tags')
    config.add_route('category_selection', '/category/selection')
    config.add_route('region_category_all', '/category/all')
    config.add_route('flash_sale', '/flash_sale')
    config.add_route('flash_sale_skus', '/flash_sale_skus')
    config.add_route('luck_homepage', '/luck_homepage')
    config.add_route('luck_draw', '/luck_draw')
    config.add_route('winners_list', '/winners_list')
    config.add_route('update_winner_info', '/update_winner_info')
    config.add_route('goddess_shared', '/goddess_shared')
    config.add_route('news_list', '/news_list')
    config.add_route('news_star', '/news_star')
    config.add_route('share_theme', '/share/theme')
    config.add_route('mall_banner_new', '/mall/banner')
    config.add_route('mall_tags', '/mall/tags')
    config.add_route('mall_daily', '/mall/daily')
    config.add_route('mall_member', '/mall/member')
    config.add_route('mall_region', '/mall/region')
    config.add_route('mall_region_new', '/mall/region/new')
    config.add_route('mall_ad_new', '/mall/ad')
    config.add_route('mall_share', '/mall/share')
    config.add_route('mall_tv_ad', '/mall/tv_ad')
    config.add_route('mall_tv_banner', '/mall/tv_banner')
    config.add_route('dapei_tag', '/dapei/tags')
    config.add_route('region_banner', '/region/banner')
    config.add_route('region_ad', '/region/ad')
    config.add_route('region_coupon', '/region/coupon')
    config.add_route('region_panicbuy', '/region/panicbuy')
    config.add_route('region_brand', '/region/brand')
    config.add_route('regions_brand', '/regions/brand')
    config.add_route('region_skus', '/region/skus')
    config.add_route('region_all', '/regions')
    config.add_route('region_with_brands', '/region_with_brands')
    config.add_route('region_category', '/region/category')
    config.add_route('region_recommend_tag', '/region/recommend/tag')
    config.add_route('region_banner_brands', '/region/banner/brands')
    config.add_route('region_banner_today', '/region/banner/today')
    config.add_route('mall_daily_topics', '/mall/daily_topics')
    config.add_route('hot_sale_skus', '/items/hot_sale')
    config.add_route('hot_sale', '/cms/hot_sale')
    config.add_route('search_sku', '/search/skus')
    config.add_route('mix_topics', '/mix_topics')
    config.add_route('goddess_clothes_luck', '/goddess_clothes/luck')
    config.add_route('goddess_clothes_lefttime', '/goddess_clothes/lefttime')
    config.add_route('user_space_numbers', '/user/space_numbers')
    config.add_route('ad_remind', '/mall/remind')
    config.add_route('goddess_clothes_winners_list', '/goddess_clothes/list')
    config.add_route('evaluation_goods_comments', '/evaluation/goods_comments')
    config.add_route('evaluation_goods_comments_inner', '/evaluation/goods_comments_inner')
    config.add_route('evaluation_goods_comment', '/evaluation/goods_comment')
    config.add_route('evaluation_business_comment', '/evaluation/business_comment')
    config.add_route('evaluation_business_score', '/evaluation/business_score')
    config.add_route('evaluation_comment_state', '/evaluation/comment_state')
    config.add_route('evaluation_comment_num', '/evaluation/comment_num')
    config.add_route('evaluation_detail_comments', '/evaluation/detail_comment')
    config.add_route('evaluation_shop_comments', '/evaluation/shop_comments')
    config.add_route('evaluation_additional_comments', '/evaluation/additional_comments')
    config.add_route('evaluation_update_cache','/evaluation/update_cache')
    config.add_route('followfans', '/new_forum/followfans')
    config.add_route('img_code', '/user/img_code')
    config.add_route('web_send_SMS', '/user/web_send_SMS')
    config.add_route('bind_mobile', '/user/bind_mobile')
    config.add_route('check_tel_code', '/user/check_tel_code')
    config.add_route('bind_SMS', '/user/bind_SMS')
    config.add_route('search_thread_sku', '/search/thread_sku')
    config.add_route('new_forum_post_tags', '/new_forum/post/tags')
    config.add_route('post_comments', '/post_comments')
    config.add_route('post', '/post')
    config.add_route('brand_category_banner', '/brand_category_banner')
    config.add_route('region_navigator','/region_navigator')
    config.add_route('webhotstarids','/web/hot_star_ids')
    config.add_route('mgtv_sg_mobile', '/event/mgtv/sg_mobile')
    config.scan()
    app = config.make_wsgi_app()
    return app
