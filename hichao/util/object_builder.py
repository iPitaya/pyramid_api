# -*- coding:utf-8 -*-
from hichao.util.statsd_client import timeit
from hichao.util.collect_util import sku_collect_counter
from hichao.util.sku_util import rebuild_sku
from hichao.cache.cache import deco_cache
from hichao.sku.models.sku import (
    get_sku_by_id,
    get_old_sku_by_id,
)
from hichao.drop.models.drop import get_drop_by_id
from hichao.android_push.models.android_push import get_last_android_push
from hichao.tuangou.models.tuangouinfo import build_tuangou_by_tuangou_id
from hichao.topic.models.topic import (
    get_topic_by_id,
    get_pre_topic,
    get_next_topic,
)
from hichao.comment.models.comment import (
    get_comment_by_id,
    get_comment_count,
)
from hichao.comment.models.sub_thread import (
    get_subthread_by_id,
    get_forum_comment_count,
)
from hichao.star.models.star import (
    get_star_by_star_id,
    get_star_id_by_iid,
    get_star_action_by_star_id,
)
from hichao.star.models.star_sku import (
    get_tabs_index_by_star_id,
    get_skus_by_star_tab,
    get_star_id_by_sku_id,
    get_star_ids_by_sku_id,
)
from hichao.forum.models.thread import (
    get_thread_by_id,
    get_sub_threads_by_id,
    get_forum_thread_count,
)
from hichao.forum.models.forum import (
    get_forum_by_id,
    get_all_forums,
)
from hichao.forum.models.tag import get_tag_by_id
from hichao.post.models.post import get_post_by_id
from hichao.util.image_url import build_banner_thread_image_url
from hichao.timeline.models.timeline import get_timeline_unit_by_type_id
from hichao.timeline.models.showlist_flow import get_flow_by_id
from hichao.forum.models.online import online_user_count
from hichao.forum import FORUM_ALL
from hichao.cooperation.models.nv_shen import get_nv_shen_entry
from hichao.sku.models.sku import get_sku_imgs
from hichao.util.component_builder import (
    build_component_star,
    build_component_item,
    build_component_item_with_sku,
    build_component_topic_list_item,
    build_component_banner_item,
    build_component_calendar,
    build_component_hangtag,
    build_component_drop,
    build_component_sku,
    build_component_android_push,
    build_component_comment,
    build_component_rtf_comment,
    build_component_thread,
    build_component_topic_drop,
    build_component_theme_list_item,
    build_component_sku_imgs,
    build_component_sub_thread,
    build_component_lite_thread,
    build_component_lite_top_thread,
    build_component_lite_subthread,
    build_component_staruser,
    build_component_tangzhu,
    build_component_embde_star,
    build_component_search_thread,
    build_component_search_topic,
    build_component_worthy_sku,
    build_component_group_sku,
    build_component_choiceness_thread,
    build_component_threaduser,
    build_component_user,
    build_component_hot_staruser,
    build_component_news_list_item,
    build_component_star_tags,
    build_component_brand_collect,
    build_component_brand_action,
    build_component_star_info,
    build_component_post,
    build_component_post_comment,
    build_component_lite_post,
    build_component_brand_collect_with_action_type)
from hichao.util.date_util import (
    HALF_MINUTE,
    MINUTE,
    FIVE_MINUTES,
    TEN_MINUTES,
    HOUR,
    DAY,
    FOREVER,
    MONTH,
)
from hichao.base.config import (
    COMMENT_TYPE_TOPIC_STR,
    COMMENT_TYPE_STAR_STR,
    COMMENT_TYPE_THREAD_STR,
    COMMENT_TYPE_TOPIC_DETAIL_STR,
    COMMENT_TYPE_STAR_DETAIL_STR,
    COMMENT_TYPE_NEWS_STR,
    COMMENT_TYPE_THEME_STR,
    COMMENT_TYPE_DICT,
    COMMENT_TYPE_TOPIC,
    COMMENT_TYPE_THREAD,
    COMMENT_TYPE_NEWS,
    COMMENT_TYPE_THEME,
    FALL_THREAD_ICON,
)
from hichao.util.collect_util import build_collection_count, build_collection_count_detail
from hichao.util.check_user_info import check_user_info
from hichao.util.comment_util import build_comment_count, build_view_count, build_view_topic_detail_count
from hichao.collect.models.topic import topic_user_count
from hichao.convert_url import CpsType
from hichao.forum.models.banwu_tangzhu import get_tangzhu_by_id
from hichao.forum.models.star_user import get_staruser_by_id
from hichao.forum.models.hot_star_user import get_hot_staruser_by_id
from hichao.base.config import CDN_PREFIX, CDN_FAST_DFS_IMAGE_PREFIX
from hichao.theme.models.theme import get_theme_by_id
import time
import datetime
from hichao.upload.models.image import get_image_by_id
from hichao.forum.models.star_user import (
    get_star_user_icon_by_user_id,
    get_staruser_by_user_id,
)
from hichao.util.image_url import build_choiceness_thread_image_url
from hichao.forum.models.thread_choiceness import get_choiceness_thread_by_id
from icehole_client.brand_client import BrandClient
from hichao.post.models.post import get_post_by_id
from hichao.user.models.user import get_user_by_id

timer = timeit('hichao_backend.util_object_builder')


@timer
def build_star_by_star_iid(star_iid, crop=0):
    star_id = get_star_id_by_iid(star_iid)
    if not star_id:
        return {}
    return build_star_by_star_id(star_id, crop)


@timer
@build_collection_count()
#@build_comment_count(comment_type = COMMENT_TYPE_STAR_STR)
@deco_cache(prefix='component_star', recycle=TEN_MINUTES)
def build_star_by_star_id(star_id, crop=0, lite_action=0, support_webp=0, use_cache=True):
    star = get_star_by_star_id(star_id, use_cache=use_cache)
    if star:
        star.lite_action = lite_action
        star.support_webp = support_webp
    com = build_component_star(star, crop)
    if com:
        com['component']['commentCount'] = '0'
        com['component']['action']['commentCount'] = '0'
    return com


@timer
@deco_cache(prefix='component_drop', recycle=TEN_MINUTES)
def build_drop_by_timeline_unit_id(type, type_id, support_webp=0, use_cache=True):
    unit = get_timeline_unit_by_type_id(type, type_id, use_cache=use_cache)
    if unit:
        unit.support_webp = support_webp
    return build_component_drop(unit)


@timer
@deco_cache(prefix='component_calendar', recycle=TEN_MINUTES)
def build_calendar_by_timeline_unit_id(type, type_id, support_webp=0, use_cache=True):
    unit = get_timeline_unit_by_type_id(type, type_id, use_cache=use_cache)
    if unit:
        unit.support_webp = support_webp
    return build_component_calendar(unit)


@timer
@deco_cache(prefix='component_hangtag', recycle=TEN_MINUTES)
def build_hangtag_by_timeline_unit_id(type, type_id, support_webp=0, use_cache=True):
    unit = get_timeline_unit_by_type_id(type, type_id, use_cache=use_cache)
    if unit:
        unit.support_webp = support_webp
    return build_component_hangtag(unit)


@timer
@deco_cache(prefix='component_banner_topic', recycle=FIVE_MINUTES)
def build_banner_item_by_topic_id(id, support_webp=0, use_cache=True):
    topic = get_topic_by_id(id, use_cache=use_cache)
    if topic:
        topic.support_webp = support_webp
    return build_component_banner_item(topic)


@timer
@deco_cache(prefix='component_banner_thread', recycle=FIVE_MINUTES)
def build_banner_item_by_thread_id(id, img_url, lite_action, support_webp=0, use_cache=True):
    thread = get_thread_by_id(id, use_cache=use_cache)
    com = {}
    if thread:
        thread.support_webp = support_webp
        com['componentType'] = 'cell'
        if img_url:
            com['picUrl'] = build_banner_thread_image_url(img_url, support_webp)
        else:
            com['picUrl'] = thread.get_component_pic_url()
        if lite_action:
            action = thread.to_lite_ui_action()
        else:
            action = thread.to_ui_action(both_img=1)
        com['action'] = action
    return com


@timer
@deco_cache(prefix='component_banner_tuan', recycle=FIVE_MINUTES)
def build_banner_item_by_tuangou_id(id, type, support_tuanlist, support_webp=0, use_cache=True):
    tuan_com = build_tuangou_by_tuangou_id(id, slide=True)
    com = {}
    if tuan_com:
        tuan_com = tuan_com['component']
        com['componentType'] = 'cell'
        com['picUrl'] = tuan_com['picUrl']
        if type == 'tuanlist' and support_tuanlist:
            com['action'] = {'actionType': 'jump', 'type': 'item', 'child': 'tuanlist'}
        else:
            com['action'] = tuan_com['action']
    return com


@timer
@build_comment_count(comment_type=COMMENT_TYPE_STAR_DETAIL_STR)
@deco_cache(prefix='star_detail', recycle=TEN_MINUTES)
def build_star_detail_by_star_id(star_id, support_webp=0, support_ec=1, support_part_color=0, use_cache=True):
    lite_action = 1
    star = get_star_by_star_id(star_id, use_cache=use_cache)
    data = {}
    if star:
        star.support_webp = support_webp
        star.support_ec = support_ec
        data['id'] = star.get_component_id()
        data['picUrl'] = star.get_normal_pic_url()
        data['description'] = star.get_component_content()
        data['userName'] = star.get_component_user_name()
        data['userAvatar'] = star.get_component_user_avatar()
        data['videoUrl'] = star.get_video_url()
        data['width'] = star.get_component_width()
        data['height'] = star.get_component_height()
        data['dateTime'] = star.get_date()
        data['unixtime'] = star.get_unixtime()
        data['trackValue'] = 'star_detail_{0}'.format(data['id'])
        data['items'] = build_star_skus_by_star_id(star_id, CpsType.IPHONE, lite_action, support_webp, support_ec, use_cache=use_cache)
        data['tags'] = build_component_star_tags(star)
        star_data = build_component_star_info(star)
        data['color'] = star_data['star_color']
        if support_part_color:
            data['itemPicUrlList'] = star_data['star_part']
        else:
            data['itemPicUrlList'] = star.get_tabs_info()
    return data


@timer
@build_collection_count()
@deco_cache(prefix='component_star_drop', recycle=HOUR)
def build_drop_with_star_id(star_id, support_webp=0, use_cache=True):
    star = get_star_by_star_id(star_id, use_cache=use_cache)
    if star:
        star.support_webp = support_webp
    return build_component_drop(star)


@timer
@build_collection_count()
@deco_cache(prefix='component_star_embde', recycle=HOUR)
def build_embed_star_by_star_id(star_id, lite_action, support_webp=0, use_cache=True):
    star = get_star_by_star_id(star_id, use_cache=use_cache)
    if star:
        star.lite_action = lite_action
        star.support_webp = support_webp
    return build_component_embde_star(star)


@timer
@build_collection_count()
@deco_cache(prefix='component_sku', recycle=HALF_MINUTE)
def build_sku_by_sku_id(sku_id, cps_type, lite_action=0, support_webp=0, support_ec=1, use_cache=True):
    sku = get_sku_by_id(sku_id, use_cache=use_cache)
    if sku:
        sku['support_webp'] = support_webp
        sku['support_ec'] = support_ec
        sku['cps_type'] = cps_type
        sku['lite_action'] = lite_action
    return build_component_sku(sku)


@timer
@deco_cache(prefix='sku_detail', recycle=TEN_MINUTES)
def build_sku_detail_by_sku_id(sku_id, cps_type, support_webp=0, use_cache=True):
    sku = get_sku_by_id(sku_id, use_cache=use_cache)
    data = {}
    if sku:
        # if sku['review'] < 0:
        #    return {}
        sku['support_webp'] = support_webp
        sku['cps_type'] = cps_type
        data['price'] = sku.get_component_price()
        data['originLink'] = sku.get_component_orig_link()
        data['link'] = sku.get_taobaoke_url()
        data['id'] = sku.get_component_id()
        data['normalPicUrl'] = sku.get_origin_pic_url()
        data['source'] = sku.get_channel_name()
        data['source_id'] = sku.get_source_id()
        data['channel'] = sku.get_component_channel()
        data['titleStyle'] = sku.get_component_title_style()
        data['trackValue'] = 'sku_detail_{0}'.format(data['id'])
        data['shareAction'] = sku.get_share_action()
        data['unixtime'] = sku.get_unixtime()
        data['width'] = sku.get_component_width()
        data['height'] = sku.get_component_height()
        if sku.is_brand():
            data['brandPicUrl'] = sku.get_brand_img_url()
            data['description'] = sku.get_component_intro()
        else:
            data['description'] = sku.get_component_title()
    return data


@timer
@deco_cache(prefix='worthy_sku_detail', recycle=TEN_MINUTES)
def build_worthy_sku_detail_by_sku_id(sku_id, cps_type, support_webp=0, use_cache=True):
    sku = get_old_sku_by_id(sku_id, use_cache=use_cache)
    data = {}
    if sku:
        if sku['review'] < 0:
            return {}
        sku['support_webp'] = support_webp
        sku.cps_type = cps_type
        data['price'] = sku.get_component_price()
        data['priceOrig'] = sku.get_component_orig_price()
        data['originLink'] = sku.get_component_orig_link()
        data['link'] = sku.get_taobaoke_url()
        data['titleStyle'] = sku.get_component_title_style()
        data['discount'] = sku.get_component_discount()
        data['sourceId'] = sku.get_source_id()
        data['source'] = sku.get_channel_name()
        data['picUrl'] = sku.get_origin_pic_url()
        data['id'] = sku.get_component_id()
        data['channel'] = sku.get_component_channel()
        data['shareAction'] = sku.get_share_action()
        data['trackValue'] = 'worthy_sku_detail_{0}'.format(data['id'])
        data['peopleCount'] = sku.get_component_uv()
        data['width'] = sku.get_component_width()
        data['height'] = sku.get_component_height()
        if sku.is_brand():
            data['brandPicUrl'] = sku.get_brand_img_url()
            data['description'] = sku.get_component_intro()
        else:
            data['description'] = sku.get_component_title()
    return data


@timer
@deco_cache(prefix='component_android_push', recycle=HOUR)
def build_android_push_by_id(push_id, use_cache=True):
    android_push = get_last_android_push(use_cache=use_cache)
    return build_component_android_push(android_push)


@timer
@build_collection_count()
@build_view_count()
@build_comment_count(comment_type=COMMENT_TYPE_TOPIC_STR)
@deco_cache(prefix='component_topic', recycle=TEN_MINUTES)
def build_topic_list_item_by_id(topic_id, support_webp=0, support_pic=0, use_cache=True):
    topic = get_topic_by_id(topic_id, use_cache=use_cache)
    if topic:
        topic.support_webp = support_webp
    com = build_component_topic_list_item(topic)
    if topic:
        if support_pic:
            img = topic.get_component_pic_image()
            com['component']['picUrl'] = img.filename
            com['width'] = str(img.width)
            com['height'] = str(img.height)
        else:
            com['component']['picUrl'] = topic.get_component_pic_url()
    return com

@timer
@build_collection_count()
@build_view_count()
@build_comment_count(comment_type=COMMENT_TYPE_THEME_STR)
@deco_cache(prefix='component_topic_theme', recycle=TEN_MINUTES)
def build_topic_list_item_by_theme_id(theme_id,support_pic = 0, use_cache=True):
    theme = get_theme_by_id(theme_id, use_cache=use_cache)
    com = build_component_topic_list_item(theme)
    if theme:
        if support_pic:
            img = theme.get_component_pic_image()
            com['component']['picUrl'] = img.filename
            com['width'] = str(img.width)
            com['height'] = str(img.height)
        else:
            com['component']['picUrl'] = theme.get_component_pic_url()
    return com
@timer
@deco_cache(prefix='component_theme', recycle=TEN_MINUTES)
def build_theme_list_item_by_id(theme_id, use_cache=True):
    theme = get_theme_by_id(theme_id)
    return build_component_theme_list_item(theme)


@timer
@check_user_info
def build_topic_detail_by_id(topic_id, user_id, width, txt_with_margin, lite_thread, lite_action, support_webp=0, support_ec=1, use_cache=True):
    topic_detail =  get_topic_detail(topic_id, width, txt_with_margin, lite_thread, lite_action, support_webp, support_ec, use_cache=use_cache)
    topic = get_topic_by_id(topic_id, use_cache=use_cache)
    topic_detail['items'] = topic.to_ui_detail(width, txt_with_margin, lite_thread, lite_action, support_webp, support_ec)
    return topic_detail


@timer
def build_comment_with_user_id(_type, comment_id, user_id, support_webp=0):
    comment = get_comment_by_id(_type, comment_id)
    if int(comment.from_uid) == int(user_id):
        visible = 1
    else:
        visible = -1
    return build_comment_by_id(_type, comment_id, visible, support_webp)


@timer
@deco_cache(prefix='component_comment', recycle=TEN_MINUTES)
def build_comment_by_id(_type, comment_id, visible, support_webp=0, use_cache=True):
    comment = get_comment_by_id(_type, comment_id, use_cache=use_cache)
    if comment:
        comment.visible = visible
        comment.support_webp = support_webp
    return build_component_comment(comment)


@timer
@deco_cache(prefix='component_rtf_comment', recycle=TEN_MINUTES)
def build_rtf_comment_by_id(_type, comment_id, with_img=0, lite_user_action=0, visible=1, support_webp=0, use_cache=True):
    comment = get_comment_by_id(_type, comment_id, use_cache=use_cache)
    if comment_id:
        comment.content_with_img = with_img
        comment.lite_user_action = lite_user_action
        comment.visible = visible
        comment.support_webp = support_webp
    com = build_component_rtf_comment(comment)
    com['flag'] = comment.floor
    return com


@timer
@deco_cache(prefix='star_skus', recycle=TEN_MINUTES)
def build_star_skus_by_star_id(star_id, cps_type, lite_action=0, support_webp=0, support_ec=1, use_cache=True):
    tabs = get_tabs_index_by_star_id(star_id, use_cache=use_cache)
    items = []
    for tab in tabs:
        item_list = {}
        item_list['itemList'] = []
        star_skus = get_skus_by_star_tab(star_id, tab)
        for star_sku in star_skus:
            sku = get_sku_by_id(star_sku.sku_id)
            # if sku['review'] != 1: continue
            if sku is None: continue
            if sku['review'] == 1 or sku['review'] == 0 or sku['review'] == -10:
                com = build_sku_by_sku_id(star_sku.sku_id, cps_type, lite_action, support_webp, support_ec, use_cache=use_cache)
                if com:
                    item_list['itemList'].append(com)
        items.append(item_list)
    return items


@timer
@build_collection_count_detail()
@build_comment_count(comment_type=COMMENT_TYPE_TOPIC_DETAIL_STR)
@build_view_topic_detail_count()
@deco_cache(prefix='topic_detail1', recycle=FIVE_MINUTES)
def get_topic_detail(topic_id, width, txt_with_margin, lite_thread, lite_action, support_webp=0, support_ec=1, use_cache=True):
    topic = get_topic_by_id(topic_id, use_cache=use_cache)
    if not topic:
        return {}
    topic_detail = {}
    if topic.review == 1:
        topic_detail['dateTime'] = datetime.datetime.fromtimestamp(float(topic.publish_date)).strftime('%Y-%m-%d %H:%M')
    else:
        topic_detail['dateTime'] = ''
    topic_detail['is_activity'] = topic.is_activity()
    topic_detail['shareAction'] = topic.get_share_image()
    navigator_type = topic.get_component_navigator_type()
    if not navigator_type:
        navigator_type = 'topic'
    pre_topic = get_pre_topic(topic.publish_date, navigator_type)
    if pre_topic:
        topic_detail['prevId'] = str(pre_topic.id)
        topic_detail['prevTitle'] = pre_topic.get_component_title()
    next_topic = get_next_topic(topic.publish_date, navigator_type)
    if next_topic:
        topic_detail['nextId'] = str(next_topic.id)
        topic_detail['nextTitle'] = next_topic.get_component_title()
    topic_detail['title'] = topic.get_component_title()
    #topic_detail['items'] = topic.to_ui_detail(width, txt_with_margin, lite_thread, lite_action, support_webp, support_ec)
    topic_detail['id'] = topic.get_component_id()
    if topic.get_component_navigator_type() == 'news':
        topic_detail['newsSource'] = topic.get_component_image_source()
    #count = topic_user_count(topic_detail['id'], topic.get_unixtime())
    #if not count: count = 0
    #topic_detail['collectionCount'] = str(count)
    topic_detail['unixtime'] = topic.get_unixtime()
    topic_detail['v'] = topic.get_component_pv()
    return topic_detail


@timer
@deco_cache(prefix='theme_detail', recycle=FIVE_MINUTES)
def build_theme_detail_by_id(theme_id):
    theme = get_theme_by_id(theme_id)
    if not theme:
        return {}
    return theme.to_ui_detail()


@timer
@build_comment_count(comment_type=COMMENT_TYPE_THREAD_STR, more_actions=True)
@build_collection_count(more_actions=True)
@deco_cache(prefix='component_thread', recycle=FIVE_MINUTES)
def build_thread_by_id(thread_id, crop=0, more_img='', support_webp=0, use_cache=True):
    thread = check_thread(thread_id, use_cache=use_cache)
    if not thread:
        return None
    thread.support_webp = support_webp
    thread.more_img = more_img
    com = build_component_thread(thread, crop)
    com['uts'] = str(thread.update_ts)
    return com


@timer
@deco_cache(prefix='component_topic_as_drop', recycle=TEN_MINUTES)
def build_topic_as_drop_by_topic_id(topic_id, support_webp=0, use_cache=True):
    topic = get_topic_by_id(topic_id, use_cache=use_cache)
    if topic:
        topic.support_webp = support_webp
    return build_component_topic_drop(topic)


@timer
@deco_cache(prefix='sku_imgs', recycle=HOUR)
def build_imgs_by_sku(source, source_id, width, support_webp=0, use_cache=True):
    sku = get_sku_imgs(source, source_id)
    if not sku:
        return []
    return build_component_sku_imgs(sku, width, support_webp)


@timer
@deco_cache(prefix='sub_threads', recycle=HOUR)
def build_sub_threads_by_id(thread_id, use_cache=True):
    threads = get_sub_threads_by_id(thread_id, support_webp=0, use_cache=use_cache)
    items = []
    for thread in threads:
        thread.support_webp = support_webp
        items.append(build_component_sub_thread(thread))
    return items


@timer
def build_subthread_with_user_id(subthread_id, lite_user_action, user_id, support_webp=0):
    sub = get_subthread_by_id(subthread_id)
    if int(sub.from_uid) == int(user_id):
        visible = 1
    else:
        visible = -1
    return build_subthread_by_id(subthread_id, visible, lite_user_action, support_webp)


@timer
@deco_cache(prefix='compnent_subthread', recycle=FIVE_MINUTES)
def build_subthread_by_id(subthread_id, visible, lite_user_action=0, support_webp=0, use_cache=True):
    subthread = get_subthread_by_id(subthread_id, use_cache=use_cache)
    subthread.lite_user_action = lite_user_action
    subthread.visible = visible
    subthread.support_webp = support_webp
    com = build_component_sub_thread(subthread)
    com['flag'] = subthread.floor
    return com


@timer
@build_collection_count(more_actions=True)
@build_view_count()
@build_comment_count(comment_type=COMMENT_TYPE_THREAD_STR, more_actions=True)
@deco_cache(prefix='component_lite_thread', recycle=FIVE_MINUTES)
def build_lite_thread_by_id(thread_id, with_top_icon=0, without_icon=0, support_webp=0, use_cache=True):
    thread = check_thread(thread_id, use_cache=use_cache)
    if not thread:
        return None
    thread.with_top_icon = with_top_icon
    thread.without_icon = without_icon
    thread.support_webp = support_webp
    com = build_component_lite_thread(thread)
    com['uts'] = str(thread.update_ts)
    return com

# 新版6.4.0以上的组装帖子的数据


@timer
#@deco_cache(prefix = 'component_lite_post', recycle = FIVE_MINUTES)
def build_lite_post_by_id(post_id, user_id='', with_top_icon=0, without_icon=0, support_webp=0, use_cache=True):
    post = get_post_by_id(post_id)
    if not post:
        return None
    post.with_top_icon = with_top_icon
    post.without_icon = without_icon
    post.support_webp = support_webp
    com = build_component_lite_post(post, user_id)
    return com

@timer
@build_comment_count(comment_type=COMMENT_TYPE_THREAD_STR, more_actions=True)
@deco_cache(prefix='component_choiceness_thread', recycle=MINUTE)
def build_choiceness_thread_by_item(item_id, use_cache=True):
    ''' 生成 每日精选 的 component '''
    item = get_choiceness_thread_by_id(item_id, use_cache=use_cache)
    if not item:
        return {}
    thread = check_thread(item.thread_id, use_cache=use_cache)
    if not thread:
        return None
    com = build_component_choiceness_thread(thread)
    if com:
        com['component']['title'] = item.thread_title
        com['component']['content'] = item.thread_desc
        com['component']['flag'] = str(item.ts)
        img_url = get_image_by_id(item.thread_img_id)
        if img_url:
            if not img_url.namespace:
                com['component']['picUrl'] = img_url.url
            else:
                com['component']['picUrl'] = build_choiceness_thread_image_url(img_url.url, img_url.namespace)
        roleIcons = get_star_user_icon_by_user_id(com['component']['userId'])
        if roleIcons:
            com['component']['roleIcons'] = roleIcons
        else:
            del(com['component']['roleIcons'])
    return com


@timer
@deco_cache(prefix='component_lite_top_thread', recycle=FIVE_MINUTES)
def build_lite_top_thread_by_id(thread_id, with_top_icon=0, support_webp=0, use_cache=True):
    thread = check_thread(thread_id, use_cache=use_cache)
    if not thread:
        return None
    thread.with_top_icon = with_top_icon
    thread.support_webp = support_webp
    com = build_component_lite_top_thread(thread)
    com['uts'] = str(thread.update_ts)
    return com


@timer
def check_thread(thread_id, use_cache=True):
    thread = get_thread_by_id(thread_id, use_cache=use_cache)
    if not thread:
        return None
    if thread.is_deleted():
        return None
    return thread


@timer
def build_lite_subthread_with_user_id(subthread_id, split_items, user_id, inner_redirect, support_webp=0, support_brandstore=0):
    sub = get_subthread_by_id(subthread_id)
    if int(sub.from_uid) == int(user_id):
        visible = 1
    else:
        visible = -1
    return build_lite_subthread_by_id(subthread_id, visible, split_items, inner_redirect, support_webp, support_brandstore)


@timer
@deco_cache(prefix='component_lite_subthread', recycle=FIVE_MINUTES)
def build_lite_subthread_by_id(subthread_id, visible, split_items, inner_redirect, support_webp, support_brandstore=0, use_cache=True):
    sub = get_subthread_by_id(subthread_id, use_cache=use_cache)
    if not sub:
        return {}
    sub.visible = visible
    sub.split_items = split_items
    sub.inner_redirect = inner_redirect
    sub.support_webp = support_webp
    sub.support_brandstore = support_brandstore
    com = build_component_lite_subthread(sub)
    com['flag'] = sub.floor
    return com


@timer
@deco_cache(prefix='component_comment_as_subthread', recycle=FIVE_MINUTES)
def build_comment_as_subthread_by_id(_type, comment_id, support_webp=0, use_cache=True):
    comment = get_comment_by_id(_type, comment_id, use_cache=use_cache)
    comment.visible = 1
    comment.split_items = 1
    comment.support_webp = support_webp
    return build_component_lite_subthread(comment)


@deco_cache(prefix='component_flow', recycle=TEN_MINUTES)
def build_flow_by_id(flow_id, support_webp=0, use_cache=True):
    flow = get_flow_by_id(flow_id)
    com = {}
    if flow:
        flow.support_webp = support_webp
        if flow.get_component_type() == 'thread':
            com = build_component_search_thread(flow)
            cnt = get_comment_count(COMMENT_TYPE_THREAD, flow.get_component_type_id())
            if not cnt:
                cnt = 0
            com['component']['commentCount'] = str(cnt)
            com['component']['icon'] = FALL_THREAD_ICON
            com['component']['action']['commentCount'] = str(cnt)
    return com


@timer
@build_comment_count(comment_type=COMMENT_TYPE_THREAD_STR, more_actions=False)
@deco_cache(prefix='component_search_thread', recycle=FIVE_MINUTES)
def build_search_thread_by_thread_id(thread_id, support_webp=0, use_cache=True):
    thread = check_thread(thread_id, use_cache=use_cache)
    if not thread:
        return {}
    thread.support_webp = support_webp
    return build_component_search_thread(thread)


@timer
@build_collection_count()
@deco_cache(prefix='component_search_topic', recycle=FIVE_MINUTES)
def build_search_topic_by_topic_id(topic_id, support_webp=0, support_ec=1, use_cache=True):
    topic = get_topic_by_id(topic_id, use_cache=use_cache)
    if not topic:
        return {}
    topic.support_webp = support_webp
    if topic.has_drop():
        return build_component_topic_drop(topic)
    else:
        return build_component_search_topic(topic)


@timer
@deco_cache(prefix='compnent_main_subthread', recycle=FIVE_MINUTES)
def build_main_subthread_by_id(thread_id, split_items, inner_redirect, support_webp=0, support_brandstore=0, use_cache=True):
    thread = check_thread(thread_id, use_cache=use_cache)
    if not thread:
        return {}
    thread.split_items = split_items
    thread.inner_redirect = inner_redirect
    thread.support_webp = support_webp
    thread.support_brandstore = support_brandstore
    return build_component_lite_subthread(thread)


@timer
@deco_cache(prefix='component_staruser', recycle=FIVE_MINUTES)
def build_staruser_by_id(staruser_id, use_cache=True):
    staruser = get_staruser_by_id(staruser_id, use_cache=True)
    return build_component_staruser(staruser)


@timer
@deco_cache(prefix='staruser_list_by_id', recycle=FIVE_MINUTES)
def build_hot_staruser_list_by_id(hot_staruser_id, use_cache=True):
    hot_staruser = get_hot_staruser_by_id(hot_staruser_id, use_cache=True)
    return build_component_hot_staruser(hot_staruser)


@timer
@deco_cache(prefix='component_threaduser', recycle=FIVE_MINUTES)
def build_staruser_by_user_id(staruser_id, use_cache=True):
    ''' 通过user_id 获得 购范儿 热门达人 的 component'''
    staruser = get_staruser_by_user_id(staruser_id, use_cache=True)
    return build_component_threaduser(staruser)


@timer
@deco_cache(prefix='component_threaduser', recycle=FIVE_MINUTES)
def build_user_by_user_id(user_id, use_cache=True):
    ''' 关注和收藏用户 的 component'''
    staruser = get_user_by_id(user_id, use_cache=True)
    return build_component_user(staruser)


@timer
@deco_cache(prefix='component_tangzhu', recycle=TEN_MINUTES)
def build_tangzhu_by_id(tangzhu_id, use_cache=True):
    tangzhu = get_tangzhu_by_id(tangzhu_id, use_cache=use_cache)
    return build_component_tangzhu(tangzhu)


@timer
def build_forum_status_by_ids(forum_ids, with_all=0, forum_4=0, support_webp=0):
    forums = []
    if not forum_ids:
        forums = get_all_forums()
    else:
        for id in forum_ids:
            forum = get_forum_by_id(id)
            if forum:
                forums.append(forum)
    if forum_4:
        count = len(forums)
        m = count % 4
        if m > 0:
            forums = forums[:-m]
    items = []
    for forum in forums:
        name, url, forum_id = forum
        item = {}
        pic_url = ''
        if url:
            pic_url = CDN_PREFIX() + url
            if not str(url).startswith('/images/images'):
                pic_url = 'http://s.pimg.cn/' + str(url)
            else: 
                if str(url).startswith('/'):
                    url = str(url)[1:]
                pic_url = CDN_PREFIX() + url
        else:
            pic_url = ''
        online_count = online_user_count(forum_id)
        item['name'] = name
        item['picUrl'] = pic_url
        item['id'] = str(forum_id)
        item['online'] = str(online_count)
        num_times = 1
        if int(forum_id) in [3, 110, 104, 106]:
            num_times = 9
        elif int(forum_id) in [112, 111, 113]:
            num_times = 3
        item['threadCount'] = str(get_forum_thread_count(forum_id) * num_times)
        item['commentCount'] = str(get_forum_comment_count(forum_id) * num_times)
        items.append(item)
    if with_all:
        items.insert(0, FORUM_ALL)
    return items


@timer
@deco_cache(prefix='component_worth_sku', recycle=TEN_MINUTES)
def build_worthy_sku_by_id(sku_id, ecshop_action=0, support_webp=0, support_ec=1, use_cache=True):
    sku = get_old_sku_by_id(sku_id, use_cache=use_cache)
    if sku:
        if sku['review'] != 1:
            return {}
        sku['ecshop_action'] = ecshop_action
        sku['support_webp'] = support_webp
        sku['support_ec'] = support_ec
    return build_component_worthy_sku(sku)


@timer
@deco_cache(prefix='component_group_sku', recycle=HOUR)
def build_group_sku_by_id(sku_id, support_webp=0, use_cache=True):
    sku = get_sku_by_id(sku_id, use_cache=use_cache)
    if sku:
        if sku['review'] != 1:
            return {}
        sku.support_webp = support_webp
    return build_component_group_sku(sku)


@timer
@deco_cache(prefix='component_nv_shen_entry', recycle=MINUTE)
def build_nv_shen_entry(use_cache=True):
    entry = get_nv_shen_entry()
    ui = {}
    if entry:
        ui['width'] = entry.get_component_width()
        ui['height'] = entry.get_component_height()
        com = {}
        com['componentType'] = 'cell'
        com['picUrl'] = entry.get_component_pic_url()
        com['action'] = entry.to_ui_action()
        ui['component'] = com
    return ui


@timer
def build_item_component_by_sku_id(sku_id, more_items=0, lite_action=0, cps_type=CpsType.IPHONE, support_webp=0, support_ec=1, support_xiajia=1, has_color=False):
    com = build_item_by_sku_id_with_sku(sku_id, more_items, lite_action, has_color, cps_type, support_webp, support_ec, support_xiajia)
    if com:
        collection_count = sku_collect_counter(com['component']['id'], com['component']['publish_date'])
        if not collection_count:
            collection_count = 0
        com['component']['collectionCount'] = str(collection_count)
        if com['component'].has_key('actions'):
            com['component']['actions'][0]['collectionCount'] = str(collection_count)
        else:
            com['component']['action']['collectionCount'] = str(collection_count)
    return com


@timer
@deco_cache(prefix='component_item', recycle=HALF_MINUTE)
def build_item_by_sku_id_with_sku(sku_id, more_items, lite_action, has_color=False, cps_type=CpsType.IPHONE, support_webp=0, support_ec=1, support_xiajia=1, crop=0):
    sku = get_sku_by_id(sku_id)
    if not sku:
        return {}
    if support_xiajia == 1 and sku['review'] not in [1, 2]:
        return {}
    if support_xiajia == 2 and sku['review'] < 0:
        return {}
    return build_component_item_with_sku(rebuild_sku(sku, more_items, lite_action, support_webp, support_ec), crop, cps_type, has_color)


@timer
@build_comment_count(comment_type=COMMENT_TYPE_NEWS_STR)
@deco_cache(prefix='component_news', recycle=MINUTE)
def build_news_list_item_by_id(news_id, use_cache=True):
    topic = get_topic_by_id(news_id, use_cache=use_cache)
    return build_component_news_list_item(topic)


@timer
@deco_cache(prefix='component_collect_brand', recycle=MINUTE)
def build_brand_collect_list_item_by_id(brand_id, use_cache=True):
    brand = BrandClient().get_brand_info_by_brand_id(brand_id)
    return build_component_brand_collect(brand)


@timer
#@deco_cache(prefix='component_collect_brand_with_action_type', recycle=MINUTE)
def build_brand_collect_list_item_by_id_with_action_type(brand_id, act_type='ecshopSearch', use_cache=True):
    brand = BrandClient().get_brand_info_by_brand_id(brand_id)
    return build_component_brand_collect_with_action_type(brand, act_type)


@timer
@deco_cache(prefix='build_brand_action', recycle=MINUTE)
def build_brand_action_by_brand_id(brand_id, use_cache=True):
    brand_info = BrandClient().get_brand_info_by_brand_id(brand_id)
    action = {}
    if brand_info:
        action = build_component_brand_action(brand_info)
    return action


@timer
@deco_cache(prefix='component_post', recycle=MINUTE)
def build_post_by_post_id(post_id, use_cache=True):
    post = get_post_by_id(post_id)
    return build_component_post(post)


@timer
@deco_cache(prefix = 'component_post_comment', recycle = FIVE_MINUTES)
def build_post_comment_by_obj(obj_id, _type, obj=None, use_cache=True):
    if not obj:
        if type == 'post':
            obj = get_post_by_id(obj_id)
        elif type == 'comment':
            obj = get_post_comment_by_id(obj_id)
    return build_component_post_comment(obj)


@timer
@deco_cache(prefix='component_tag', recycle=MINUTE)
def build_forum_tag_by_tag_id(tag_id, use_cache=True):
    tag = get_tag_by_id(tag_id)
    if tag:
        return tag.get_component_forum_tag()
