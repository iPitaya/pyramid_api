# -*- coding:utf-8 -*-

from hichao.util.formatter import format_price
from hichao.util.statsd_client import timeit
from hichao.util.image_url import (
    build_image_url,
    get_item_normal_path,
    build_sku_items_image_url,
    build_sku_detail_image_url,
    build_sku_detail_big_image_url,
    build_category_and_brand_image_url,
    build_brand_designer_pic_url,
)
from hichao.util.cps_util import (
    cps_title_styles_dict,
    get_cps_url,
    get_cps_source_name,
    get_cps_source_img,
    get_cps_key,
    CpsType,
)
from hichao.follow.models.follow import (
    get_user_follow_status,
    forum_followed_count,
)
from hichao.forum.models.star_user import(
    user_is_staruser,
    get_staruser_by_user_id,
)
from hichao.base.config.ui_action_type import SKU_DETAIL
from hichao.collect.models.thread import (
    get_thread_collect_status,
    thread_user_count,
)
from hichao.comment.models.comment import get_comment_count
from hichao.base.config.ui_component_type import (
    FALL_STAR_CELL,
    TOPIC_CELL,
    SKU_CELL,
    SEARCH_TOPIC_CELL,
)
from hichao.base.config import (
    CHANNEL_DICT,
    CDN_PREFIX,
    FAKE_ACTION,
    CDN_FAST_DFS_IMAGE_PREFIX,
    COMMENT_TYPE_THREAD,
)
from hichao.base.models.base_component import BaseComponent
from hichao.sku.models.sku_size import get_size_by_sku_id
from hichao.star.models.star_sku import (
    get_star_id_by_sku_id,
    get_star_ids_by_sku_id,
)
from hichao.star.models.star import (
    get_star_by_star_id,
    get_star_action_by_star_id,
)
from hichao.sku.models.sku import (
    get_sku_action_by_sku_id,
    get_sku_id_by_source_sourceid,
    get_sku_event_icon,
)

from hichao.forum.models.forum import get_forum_name_by_cat_id
from hichao.user.models.user import get_user_by_id
from icehole_client.files_client import get_filename as get_img_file
import json
import time
from icehole_client.files_client import get_image_filename
from hichao.collect.models.fake import collect_count
from icehole_client.coflex_agent_client import CoflexAgentClient
from hichao.base.config.sku_part import PART_NAME, PART_PICURL
from hichao.star.models.star_sku import get_tabs_index_by_star_id
from hichao.util.files_image_info import get_filename_new, get_image_filename_new
from hichao.util.sku_info import get_sku_country_info_new
from hichao.forum.models.star_user import get_staruser_by_user_id
from hichao.upload.models.image import get_image_by_id
from hichao.util.date_util import get_rough_time

IMAGE_FILENAME_SPACE = 'backend_images'
LIKE_USER_NUM = 6
DEFAULT_FORUM_ID = 110
timer = timeit('hichao_backend.util_component_builder')


@timer
def build_component_star(obj, crop=False):
    ui = {}
    if obj:
        ui['width'] = obj.get_component_width(crop)
        ui['height'] = obj.get_component_height(crop)
        ui['timestamp'] = obj.get_component_publish_date()
        com = {}
        com['componentType'] = FALL_STAR_CELL
        com['picUrl'] = obj.get_component_pic_url(crop)
        com['description'] = obj.get_component_description()
        com['id'] = obj.get_component_id()
        com['unixtime'] = obj.get_unixtime()
        com['hasVideo'] = obj.get_video_url() != '' and '1' or '0'
        com['action'] = obj.to_ui_action()
        com['itemsCount'] = obj.get_component_item_count()
        ui['component'] = com
    return ui


@timer
def build_component_search_thread(obj):
    ui = {}
    if obj:
        ui['width'] = obj.get_component_width()
        ui['height'] = obj.get_component_height()
        com = {}
        com['componentType'] = 'searchThreadCell'
        com['picUrl'] = obj.get_component_common_pic_url()
        com['description'] = obj.get_component_title()
        com['id'] = obj.get_component_id()
        com['forumId'] = obj.get_component_forum_id()
        com['itemsCount'] = obj.get_component_sku_num()
        com['action'] = obj.to_lite_ui_action()
        com['v'] = str(obj.get_component_pv())
        ui['component'] = com
    return ui


@timer
def build_component_search_topic(obj):
    ui = {}
    if obj:
        ui['width'] = obj.get_component_width()
        ui['height'] = obj.get_component_height()
        com = {}
        com['componentType'] = SEARCH_TOPIC_CELL
        com['id'] = obj.get_component_id()
        com['picUrl'] = obj.get_component_drop_pic_url()
        if not obj.has_drop():
            com['description'] = obj.get_component_title()
        com['unixtime'] = obj.get_unixtime()
        com['action'] = obj.to_ui_action()
        ui['component'] = com
    return ui


@timer
def build_component_item(obj):
    ui = {}
    if obj:
        ui['width'] = obj.get_component_width()
        ui['height'] = obj.get_component_height()
        com = {}
        com['componentType'] = 'item'
        com['id'] = obj.get_component_id()
        com['picUrl'] = obj.get_component_pic_url()
        com['price'] = obj.get_component_price()
        com['description'] = obj.get_component_description()
        com['actions'] = []
        sku_action = get_sku_action_by_sku_id(obj.get_component_id())
        com['collectionCount'] = sku_action['collectionCount']
        com['actions'].append(sku_action)
        star_id = get_star_id_by_sku_id(obj.get_component_id())
        star_action = get_star_action_by_star_id(star_id)
        if star_action:
            com['actions'].append(star_action)
        ui['component'] = com
    return ui


@timer
def build_component_topic_list_item(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = TOPIC_CELL
        com['title'] = obj.get_component_title()
        com['description'] = obj.get_component_description()
        com['topPicUrl'] = obj.get_component_top_pic_url()
        com['year'] = obj.get_component_year()
        com['month'] = obj.get_component_month()
        com['day'] = obj.get_component_day()
        com['weekDay'] = obj.get_component_week_day()
        com['action'] = obj.to_ui_action()
        com['id'] = obj.get_component_id()
        com['category'] = obj.get_category()
        com['flag'] = obj.get_component_flag()
        com['v'] = obj.get_component_pv()
        com['unixtime'] = obj.get_unixtime()
        com['tagAction'] = obj.get_tag_action()
        com['collectionType'] = obj.get_collect_type()
        ui['component'] = com
    return ui


@timer
def build_component_news_list_item(obj):
    ui = {}
    if obj:
        com = {}
        com['picUrl'] = obj.get_component_news_pic_url()
        com['source'] = obj.image_source
        com['componentType'] = 'newsCell'
        com['title'] = obj.get_component_title()
        com['commentCount'] = '100'
        com['flag'] = obj.get_component_flag()
        com['id'] = obj.get_component_id()
        com['action'] = obj.to_news_action()
        ui['component'] = com
    return ui


@timer
def build_component_theme_list_item(obj):
    ui = {}
    if obj:
        ui['width'] = obj.get_component_drop_width()
        ui['height'] = obj.get_component_drop_height()
        com = {}
        com['componentType'] = 'cell'
        com['picUrl'] = obj.get_component_drop_pic_url()
        com['title'] = obj.get_component_title()
        com['action'] = obj.to_ui_action()
        com['flag'] = obj.get_component_flag()
        ui['component'] = com
    return ui


@timer
def build_component_banner_item(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'cell'
        com['picUrl'] = obj.get_component_pic_url()
        com['action'] = obj.to_ui_action()
        ui['component'] = com
    return ui


@timer
def build_component_calendar(obj):
    ui = {}
    if obj:
        com = calendar_builder(obj)
        com['componentType'] = 'calendar'
        com['width'] = obj.get_component_width()
        com['height'] = obj.get_component_height()
        com['action'] = {}
        ui['component'] = com
    return ui


@timer
def calendar_builder(obj):
    com = {}
    if obj:
        com['year'] = obj.get_component_year()
        com['month'] = obj.get_component_month()
        com['monthOnly'] = obj.get_component_month_only()
        com['day'] = obj.get_component_day()
        com['weekDay'] = obj.get_component_week_day()
        com['xingQi'] = obj.get_component_xingqi()
        com['showTime'] = obj.get_component_show_time()
        com['backgroundUrl'] = ''                           # 日期牌的背景图
        com['monthColor'] = '129,129,129,255'               # 月分颜色，比如“10月”
        com['dayColor'] = '85,85,85,255'                    # 日期颜色，比如“20”
        com['weekDayColor'] = '129,129,129,255'             # 星期颜色，比如“周六”
        com['weekDayBgUrl'] = CDN_PREFIX() + 'images/images/20130518/301d624c-cfc2-4467-956b-c9f7951de662.png'                            # 星期的背景图，即周六下边的图
        com['showTimeColor'] = '255,56,141,255'             # 时间颜色，几点几分，比如“11:00”
        com['publishColor'] = '129,129,129,255'             # 发布两个字的颜色
    return com


@timer
def build_component_hangtag(obj):
    ui = {}
    if obj:
        ui['width'] = obj.get_component_width()
        ui['height'] = obj.get_component_height()
        com = calendar_builder(obj)
        com['componentType'] = 'hangtag'
        com['picUrl'] = obj.get_component_pic_url()
        com['actions'] = []
        com['actions'].append({})
        com['actions'].append(obj.to_ui_action())
        ui['component'] = com
    return ui


@timer
def build_component_drop(obj):
    ui = {}
    if obj:
        ui['width'] = obj.get_component_drop_width()
        ui['height'] = obj.get_component_drop_height()
        com = {}
        com['componentType'] = 'cell'
        com['picUrl'] = obj.get_component_pic_url()
        com['action'] = obj.to_ui_action()
        ui['component'] = com
    return ui


@timer
def build_component_sku(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = SKU_CELL
        com['stateMessage'] = obj.get_sku_state_msg()
        com['id'] = obj.get_component_id()
        com['width'] = obj.get_component_width()
        com['height'] = obj.get_component_height()
        com['picUrl'] = obj.get_component_pic_url()
        com['price'] = obj.get_component_price()
        com['sourceTitle'] = obj.get_channel_name()
        com['sourcePicUrl'] = obj.get_channel_url()
        com['unixtime'] = obj.get_unixtime()
        com['action'] = obj.to_ui_action()
        if obj.is_brand():
            com['isBrand'] = '1'
        ui['component'] = com
    return ui


@timer
def build_component_search_words(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'searchStar'
        com['picUrl'] = obj.get_component_pic_url()
        com['name'] = obj.get_component_name()
        com['starCount'] = obj.get_component_star_count()
        com['action'] = obj.to_ui_action()
        ui['component'] = com
    return ui


@timer
def build_component_newsStar_list(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'newsStarCell'
        com['picUrl'] = obj.get_component_pic_url()
        com['name'] = obj.get_component_name()
        com['englishName'] = obj.get_component_english_name()
        com['starCount'] = obj.get_component_star_count()
        com['newsCount'] = obj.get_component_news_count()
        com['action'] = obj.to_ui_action()
        ui['component'] = com
    return ui


@timer
def build_component_android_push(obj):
    ui = {}
    if obj:
        ui['ticker'] = obj.get_ticker()
        ui['title'] = obj.get_title()
        ui['content'] = obj.get_content()
        ui['version'] = obj.get_version()
        params = json.dumps(obj.to_ui_action())
        ui['params'] = params
    return ui


@timer
def build_component_comment(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'comment'
        com['userAvatar'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['action'] = obj.to_ui_action()
        com['floor'] = ''
        com['content'] = obj.get_component_content()
        com['publishDate'] = obj.get_component_publish_date()
        ui['component'] = com
    return ui


@timer
def build_component_rtf_comment(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'comment'
        com['userAvatar'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['floor'] = obj.get_component_floor()
        com['publishDate'] = obj.get_component_publish_date()
        com['userId'] = obj.get_component_user_id()
        com['commentId'] = obj.get_component_id()
        com['action'] = obj.to_ui_action()
        com['content'] = obj.to_rtf_content()
        ui['component'] = com
    return ui


@timer
def build_component_thread(obj, crop=False):
    ui = {}
    if obj:
        com = {}
        width = obj.get_component_width()
        height = obj.get_component_height()
        if crop:
            if int(width) > int(height):
                ui['width'] = height
                ui['height'] = height
            else:
                ui['width'] = width
                ui['height'] = width
        else:
            ui['width'] = width
            ui['height'] = height
        com['componentType'] = 'waterfallSubjectCell'
        com['picUrl'] = obj.get_component_pic_fall_url(crop)
        com['userId'] = obj.get_component_user_id()
        com['userLevel'] = obj.get_component_user_level()
        com['forum'] = obj.get_component_forum()
        com['id'] = obj.get_component_id()
        com['unixtime'] = obj.get_unixtime()
        com['userAvatar'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['description'] = obj.get_component_description()
        com['category'] = obj.get_component_category()
        com['dateTime'] = obj.get_component_publish_date()
        com['title'] = obj.get_component_title()
        if getattr(obj, 'more_img'):
            com['pics'] = obj.get_component_fall_imgs(crop)
            com['v'] = obj.get_component_pv()
        com['actions'] = []
        usr = obj.get_bind_user()
        if usr:
            com['actions'].append(usr.to_ui_action())
        else:
            com['actions'].append({})
        com['actions'].append(obj.to_ui_action())
        ui['component'] = com
    return ui


@timer
def build_component_topic_drop(obj):
    ui = {}
    if obj:
        com = {}
        ui['width'] = obj.get_component_width()
        ui['height'] = obj.get_component_height()
        com['componentType'] = 'cell'
        com['picUrl'] = obj.get_component_drop_pic_url()
        com['action'] = obj.to_ui_action()
        com['unixtime'] = obj.get_unixtime()
        ui['component'] = com
    return ui


@timer
def build_component_sku_imgs(obj, width, support_webp=0):
    uis = []
    width = int(width)
    for img in obj[u'img_list']:
        if img.has_key(u'url'):
            ui = {}
            img_info = get_image_filename('duotu', img[u'source_url'])
            if not img_info.filename:
                continue
            if int(img_info.width) * int(img_info.height) < 79790:
                continue
            pic_url = build_sku_detail_image_url(img_info.filename, support_webp)
            prop = width * 1.0 / int(img_info.width)
            ui['width'] = str(width)
            ui['height'] = str(int(img_info.height) * prop)
            com = {}
            com['componentType'] = 'cell'
            com['picUrl'] = pic_url
            act = {}
            act['actionType'] = 'showBigPic'
            #act['picUrl'] = build_sku_detail_image_url(img[u'source_url'])
            act['picUrl'] = pic_url
            act['noSaveButton'] = '0'
            com['action'] = act
            ui['component'] = com
            uis.append(ui)
    return uis


@timer
def build_component_sub_thread(obj):
    if obj:
        return obj.to_sub_detail()
    return {}


@timer
def build_component_lite_thread(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'fallLiteSubjectCell'
        com['userAvatar'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['userId'] = obj.get_component_user_id()
        com['id'] = obj.get_component_id()
        icons = obj.get_component_icon()
        if icons:
            com['icons'] = icons
        com['actions'] = []
        action = obj.to_lite_ui_action()
        user_action = obj.get_component_user_action()
        com['actions'].append(action)
        com['actions'].append(user_action)
        forum = obj.get_component_category()
        if forum:
            com['forum']= str(forum)
            com['forumId'] = obj.get_component_forum_id()
        else:
            com['forum']= str(get_forum_name_by_cat_id(DEFAULT_FORUM_ID))
            com['forumId'] = str(DEFAULT_FORUM_ID)
        com['publishDate'] = obj.get_component_publish_date()
        com['unixtime'] = obj.get_unixtime()
        com['title'] = obj.get_component_title()
        if obj.has_image():
            com['pics'] = obj.get_component_fall_imgs(crop=1)
        com['v'] = obj.get_component_pv()
        com['tagAction'] = obj.get_tag_action()
        ui['component'] = com
    return ui

# v6.4.0新版帖子component 接口


@timer
def build_component_lite_post(obj, user_id=''):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'fallLiteSubjectCell'
        t_unix = time.mktime(obj.update_ts.timetuple())
        com['datatime'] = str(get_rough_time(t_unix))
        com['userName'] = obj.get_component_user_name()
        type_name = obj.get_user_identify()
        if type_name:
            com['userTypeName'] = type_name.get('userTypeName')
            com['followType'] = type_name.get('followType')
        else:
            com['userTypeName'] = ''
            com['followType'] = ''
        com['userId'] = obj.get_component_user_id()
        if user_id:
            com['isfocus'] = str(get_user_follow_status(user_id, obj.get_component_user_id()))
            com['iscollect'] = str(get_thread_collect_status(obj.get_component_id(), user_id))
        else:
            com['isfocus'] = '0'
            com['iscollect'] = '0'
        com['commentCount'] = str(get_comment_count(COMMENT_TYPE_THREAD, obj.get_component_id()))
        com['focusCount'] = str(forum_followed_count(obj.get_component_user_id()))
        com['user'] = obj.get_component_user()
        com['content'] = obj.content
        com['id'] = str(obj.get_component_id())
        com['pics'] = obj.get_component_lite_imgs()
        com['tags'] = obj.get_component_tags()
        com['users'] = obj.get_component_liked_users()
        collectCount = thread_user_count(obj.get_component_id())
        if len(com['users']) >= LIKE_USER_NUM:
            if collectCount >= LIKE_USER_NUM:
                com['collectCCount'] = str(collectCount)
            else:
                com['collectCCount'] = str(LIKE_USER_NUM)
        else:
             com['collectCCount'] = str(LIKE_USER_NUM)
        com['comments'] = obj.get_component_comments()
        com['action'] = obj.to_ui_action()
        com['shareAction'] = obj.get_share_action()
        ui['component'] = com
    return ui


@timer
def build_component_choiceness_thread(obj):
    ui = {}
    if obj:
        com = {}
        com['id'] = obj.get_component_id()
        com['userId'] = obj.get_component_user_id()
        com['componentType'] = 'threadRecommend'
        com['picUrl'] = ''
        com['userAvatar'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['roleIcons'] = []
        com['title'] = obj.get_component_title()
        com['roleIcons'] = []
        com['actions'] = []
        action = obj.to_lite_ui_action()
        user_action = obj.get_component_user_action()
        com['actions'].append(action)
        com['actions'].append(user_action)
        com['content'] = obj.get_component_category()
        com['itemsCount'] = obj.get_component_sku_num()
        com['v'] = obj.get_component_pv()
        com['commentCount'] = ''
        com['publishDate'] = obj.get_component_publish_date()
        ui['component'] = com
    return ui


@timer
def build_component_lite_top_thread(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'topLiteSubjectCell'
        icons = obj.get_component_icon()
        if icons:
            com['icons'] = icons
        com['title'] = obj.get_component_title()
        com['action'] = obj.to_lite_ui_action()
        com['id'] = obj.get_component_id()
        ui['component'] = com
    return ui


@timer
def build_component_lite_subthread(obj):
    ui = {}
    if obj:
        split_items = getattr(obj, 'split_items', 0)
        com = {}
        com['componentType'] = 'liteSubSubjectCell'
        com['id'] = obj.get_component_id()
        com['userAvatar'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['userId'] = obj.get_component_user_id()
        com['publishDate'] = obj.get_component_origin_publish_date()
        com['floor'] = obj.get_component_floor()
        if split_items:
            com['description'], com['embedItems'] = obj.get_component_content_with_sku()
        else:
            com['description'] = obj.get_component_content_with_sku()
        if obj.get_role_icons():
            com['roleIcons'] = obj.get_role_icons()
        com['imgs'] = obj.get_component_detail_imgs()
        com['action'] = obj.get_component_user_action()
        reply = obj.get_component_reply()
        if reply:
            com['reply'] = reply
        ui['component'] = com
    return ui


@timer
def build_component_post_subthread(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'postSubThreadCell'
        com['id'] = obj.get_component_id()
        com['userAvatar'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['userTypeName'] = obj.get_component_user_type_name()
        com['userId'] = obj.get_component_user_id()
        com['publishDate'] = obj.get_component_origin_publish_date()
        contentHead = ''
        if obj.comment_id > 0:
            to_user = obj.get_to_user()
            contentHead = '回复 ' + to_user.get_component_user_name() + ':'
        com['contentHead'] = contentHead
        com['content'] = obj.content
        com['action'] = obj.get_component_user_action()
        ui['component'] = com
    return ui


@timer
def build_component_staruser(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'starUserCell'
        com['userAvatar'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['description'] = obj.get_component_user_description()
        com['action'] = obj.to_lite_ui_action()
        com['userId'] = obj.get_component_user_id()
        ui['component'] = com
    return ui


@timer
def build_component_threaduser(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'threadUser'
        com['picUrl'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['action'] = obj.to_lite_ui_action()
        com['roleIcons'] = obj.get_component_staruser_roleIcons()
        ui['component'] = com
    return ui


@timer
def build_component_user(obj):
    ui = {}
    if obj:
        com = {}
        com['userTypeName'] = ''
        com['followType'] = ''
        com['description'] = ''
        staruser = get_staruser_by_user_id(obj.id)
        type_dict = {}
        if staruser:
            type_dict = staruser.get_staruser_type()
            com['description'] = staruser.get_component_user_description()
        if type_dict:
            com['userTypeName'] = type_dict['userTypeName']
            com['followType'] = type_dict['followType']
        com['componentType'] = 'starUserCell'
        com['userAvatar'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['action'] = obj.to_staruser_ui_action()
        com['userId'] = obj.get_component_id()
        ui['component'] = com
    return ui


def build_component_hot_staruser(obj):
    ui = {}
    if obj:
        com = {}
        staruser = obj.get_bind_user()
        if not staruser:
            return {}
        com['userTypeName'] = ''
        com['followType'] = ''
        type_dict = staruser.get_staruser_type()
        if type_dict:
            com['userTypeName'] = type_dict['userTypeName']
            com['followType'] = type_dict['followType']
        com['componentType'] = 'threadUserDetail'
        com['userAvatar'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['action'] = obj.to_ui_action()
        com['roleIcons'] = obj.get_component_icon()
        com['description'] = obj.get_component_user_description()
        com['pics'] = obj.get_component_pic_url()
        com['flag'] = obj.get_component_flag()
        com['userId'] = obj.get_component_user_id()
        ui['component'] = com
    return ui


@timer
def build_component_tangzhu(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'tangZhuCell'
        com['userAvatar'] = obj.get_component_user_avatar()
        com['userName'] = obj.get_component_user_name()
        com['description'] = obj.get_component_user_description()
        com['action'] = obj.to_lite_ui_action()
        ui['component'] = com
    return ui


@timer
def build_component_embde_star(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'embedStarCell'
        com['picUrl'] = obj.get_component_pic_url()
        com['description'] = obj.get_component_content()
        com['action'] = obj.to_ui_action()
        ui['component'] = com
    return ui


@timer
def build_component_worthy_sku(obj):
    ui = {}
    if obj:
        ui['width'] = obj.get_component_width()
        ui['height'] = obj.get_component_height()
        com = {}
        com['componentType'] = 'worthySkuCell'
        com['picUrl'] = obj.get_component_pic_url()
        com['description'] = obj.get_component_short_description()
        com['price'] = obj.get_component_price()
        com['origPrice'] = obj.get_component_orig_price()
        com['discount'] = obj.get_component_discount()
        com['eventIcon'] = obj.get_component_event_icon()
        com['stateMessage'] = obj.get_sku_state_msg()
        if obj.get_source() == 'ecshop':
            com['peopleCount'] = collect_count(int(obj.get_source_id()), 1000, int(time.mktime(obj['publish_date'].timetuple()))) + 1000
        else:
            com['peopleCount'] = obj.get_component_uv()
        if obj['ecshop_action'] == 1 and obj.get_source() == 'ecshop':
            com['action'] = obj.to_lite_ui_action()
            com['action']['id'] = str(get_sku_id_by_source_sourceid(obj.get_source(), obj.get_source_id()))
        else:
            com['action'] = obj.to_worthy_sku_action()
        ui['component'] = com
    return ui


@timer
def build_component_group_sku(obj):
    ui = {}
    if obj:
        ui['width'] = obj.get_component_width()
        ui['height'] = obj.get_component_height()
        com = {}
        com['componentType'] = 'groupSkuCell'
        com['picUrl'] = obj.get_component_pic_url()
        com['price'] = obj.get_component_price()
        com['action'] = obj.to_lite_ui_action()
        ui['component'] = com
    return ui


@timer
def build_component_news(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'newsCell'
        com['picUrl'] = ''
        com['source'] = ''
        com['title'] = obj.get_component_title()
        com['action'] = obj.to_news_action()
    return ui


@timer
def build_component_item_with_sku(dct, crop=0, cps_type=CpsType.IPHONE, has_color=False):
    component = {}
    if not dct:
        return component
    com = {}
    com['componentType'] = 'item'

    is_mongo_sku = 0
    try:
        int(dct['sku_id'])
    except:
        is_mongo_sku = 1

    support_webp = dct.get('support_webp', 0)
    support_ec = dct.get('support_ec', 1)

    pic_url = ''
    if has_color and dct['color_url']:
        img_info = get_image_filename(IMAGE_FILENAME_SPACE, get_item_normal_path(dct['color_url']))
    else:
        if dct['url']:
            img_info = get_image_filename(IMAGE_FILENAME_SPACE, get_item_normal_path(dct['url']))
        else:
            img_info = get_image_filename(IMAGE_FILENAME_SPACE, get_item_normal_path(dct['detail_url']))
    if img_info.filename:
        pic_url = build_sku_items_image_url(img_info.filename, support_webp)
        width = img_info.width
        height = img_info.height
    else:
        pic_url = dct['url']
        width = 3
        height = 4

    if isinstance(dct['publish_date'], unicode):
        com['publish_date'] = int(float(str(dct['publish_date'])))
    elif isinstance(dct['publish_date'], int):
        com['publish_date'] = int(dct['publish_date'])
    else:
        ts = time.mktime(dct['publish_date'].timetuple())
        com['publish_date'] = int(ts)
    com['picUrl'] = pic_url
    price = format(float(format_price(dct['curr_price'])), '.2f')
    origin_price = format(float(format_price(dct['origin_price'])), '.2f')
    com['price'] = price
    com['origin_price'] = origin_price
    com['id'] = str(dct['sku_id'])
    com['description'] = dct['title']
    com['trackValue'] = 'search_sku_' + str(dct['sku_id'])
    if dct.get('eventIcon',''):
        com['eventIcon'] = dct['eventIcon']
    else:
        com['eventIcon'] = dct.get_component_event_icon()
    com['stateMessage'] = dct.get_sku_state_msg()
    sku_msg = dct.get_sku_state_info()
    com['country'] = sku_msg['country']
    com['nationalFlag'] = sku_msg['flag']
    #ecsku_info = dct.get_ecshop_sku_info()
    # if ecsku_info:
    #    com['sales'] = ecsku_info["sale_number"]
    # else:
    #    com['sales'] = '0'
    com['sales'] = str(dct['sales'])
    if isinstance(dct, dict):
        lite_action = dct.get('lite_action', 0)
    else:
        lite_action = getattr(dct, 'lite_action', 0)
    if lite_action:
        if dct['source'] == 'ecshop' and not support_ec:
            action = FAKE_ACTION
        else:
            action = {}
            action['actionType'] = 'detail'
            action['type'] = 'sku'
            action['id'] = str(dct['sku_id'])
            action['source'] = dct['source']
            action['sourceId'] = str(dct['source_id'])
            image_size = get_image_filename(IMAGE_FILENAME_SPACE, dct['url'])
            image_width = '100'
            image_height = '100'
            if str(image_size.width) == '0' or str(image_size.height) == '0':
                if str(dct['width']) != '0' and str(dct['height']) != '0':
                    image_width = str(dct['width'])
                    image_height = str(dct['height'])
            else:
                image_width = str(image_size.width)
                image_height = str(image_size.height)

            action['width'] = image_width
            action['height'] = image_height
        star_count = len(get_star_ids_by_sku_id(dct['sku_id']))
        if star_count:
            com['starCount'] = str(star_count)
        if has_color:
            action['main_image'] = 1
        else:
            action['main_image'] = 0
        com['action'] = action
    else:
        if dct['source'] == 'ecshop' and not support_ec:
            more_items = 0
            if isinstance(dct, dict):
                more_items = dct.get('more_items', '')
            else:
                more_items = getattr(dct, 'more_items', '')
            if more_items:
                com['actions'] = [FAKE_ACTION, ]
            else:
                com['action'] = FAKE_ACTION
        else:
            action = {}
            action['actionType'] = SKU_DETAIL
            action['price'] = price
            action['originLink'] = dct['link']
            cps_url = ''
            try:
                cps_url = get_cps_url(dct['source'], dct['source_id'], cps_type=cps_type).replace('&unid=default', '')
            except:
                cps_url = ''
            if cps_url:
                action['link'] = cps_url
            else:
                action['link'] = dct['link']
            action['channel'] = dct['source']
            action['source'] = CHANNEL_DICT[get_cps_key(dct['source'], dct['link'])]['CHANNEL_NAME']
            action['source_id'] = str(dct['source_id'])
            action['titleStyle'] = cps_title_styles_dict[get_cps_key(dct['source_id'], dct['link'])]
            action['id'] = str(dct['sku_id'])
            detail_url = dct['url']
            try:
                if dct['detail_url']:
                    detail_url = dct['detail_url']
            except:
                pass
            action['normalPicUrl'] = build_sku_detail_big_image_url(detail_url, support_webp)
            action['description'] = dct['title']
            action['channelPicUrl'] = get_cps_source_img(dct['source'], dct['link'])
            action['trackValue'] = 'search_sku_' + str(dct['sku_id'])
            share_action = {}
            share = {}
            share['typeId'] = dct['sku_id']
            share['description'] = dct['title']
            share['title'] = '分享个宝贝给你'
            share['shareType'] = 'webpage'
            share['detailUrl'] = action['link']
            share['picUrl'] = pic_url
            share['type'] = 'sku'
            share['trackValue'] = 'share_' + str(dct['sku_id'])
            share_action['share'] = share
            share_action['actionType'] = 'share'
            action['shareAction'] = share_action
            if isinstance(dct, dict):
                more_items = dct.get('more_items', '')
            else:
                more_items = getattr(dct, 'more_items', '')
            if more_items:
                com['actions'] = []
                com['actions'].append(action)
                if dct['f'] == 1:
                    star_id = get_star_id_by_sku_id(dct['sku_id'])
                else:
                    star_id = -1
                if star_id > 0:
                    star_action = get_star_action_by_star_id(star_id)
                    if star_action:
                        com['actions'].append(star_action)
            else:
                star_ids = get_star_ids_by_sku_id(dct['sku_id'])
                star_coms = []
                for star_id in star_ids:
                    star = get_star_by_star_id(star_id)
                    star_com = build_component_drop(star)
                    if star_com:
                        star_coms.append(star_com)
                action['bindStars'] = star_coms
                bind_star_count = len(star_coms)
                com['starCount'] = str(bind_star_count)
                com['action'] = action
    component['component'] = com
    if crop:
        component['width'] = '3'
        component['height'] = '4'
    else:
        component['width'] = str(width)
        component['height'] = str(height)
    return component


def build_component_star_tags(obj):
    tag_list = obj.get_component_tag()
    items_list = []
    for tag in tag_list:
        items = {}
        items['component'] = tag
        items_list.append(items)
    return items_list


def build_component_brand_collect(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'brandcollectCell'
        if obj.brand_type == 1 and obj.designer_pic:
            com['picUrl'] = build_brand_designer_pic_url(obj.designer_pic)
            com['title'] = obj.designer_name
            com['word'] = obj.designer_name
        else:
            com['picUrl'] = build_category_and_brand_image_url(obj.brand_logo)
            com['title'] = obj.brand_name
            com['word'] = obj.brand_name
        com['brandLogo'] = build_category_and_brand_image_url(obj.brand_logo)
        com['id'] = str(obj.business_id)
        action = {}
        action = build_component_brand_action(obj)
        com['action'] = action
        ui['component'] = com
    return ui


def build_component_brand_collect_with_action_type(obj, action_type):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'brandcollectCell'
        if obj.brand_type == 1 and obj.designer_pic:
            com['picUrl'] = build_brand_designer_pic_url(obj.designer_pic)
            com['title'] = obj.designer_name
            com['word'] = obj.designer_name
        else:
            com['picUrl'] = build_category_and_brand_image_url(obj.brand_logo)
            com['title'] = obj.brand_name
            com['word'] = obj.brand_name
            com['en_word'] = obj.brand_english_name
        com['brandLogo'] = build_category_and_brand_image_url(obj.brand_logo)
        com['id'] = str(obj.business_id)
        action = {}
        action = build_component_brand_action(obj, action_type)
        com['action'] = action
        ui['component'] = com
    return ui


def build_component_brand_action(obj, action_type='ecshopSearch'):
    action = {}
    if obj:
        action['en_title'] = obj.brand_english_name
        action['id'] = str(obj.business_id)
        if obj.brand_type == 1 and obj.designer_pic:
            action['picUrl'] = build_brand_designer_pic_url(obj.designer_pic)
            action['title'] = obj.designer_name
        else:
            action['picUrl'] = build_category_and_brand_image_url(obj.brand_logo)
            action['title'] = obj.brand_name
        action['actionType'] = action_type
    return action


def star_color_action(res):
    name = ''
    action = {}
    if res:
        for color_value in res:
            if not name:
                name = color_value['name']
            else:
                name = name + ' ' + color_value['name']
        action['query'] = name
        action['type'] = 'star'
        action['actionType'] = 'query'
    return action


def build_component_star_info(obj):
    # 获取明星图色值和部位图
    data = {}
    data['star_color'] = []
    data['star_part'] = []
    color_com = []
    part_com = []
    pic_part = []
    client = CoflexAgentClient()
    res = client.get_star_part_info(obj.description)
    if res:
        cdn = CDN_FAST_DFS_IMAGE_PREFIX()
        for index, color_value in enumerate(res['colors']):
            if not color_value['color_image_url']:
                del res['colors'][index]
        for color_value in res['colors']:
            color = {}
            color['name'] = color_value['name']
            color['url'] = cdn + color_value['color_image_url']
            color['action'] = star_color_action(res['colors'])
            color_com.append(color)
        for item_pic in res['parts']:
            pic = {}
            pic['part_icon_normal'] = cdn + item_pic['part_icon_normal']
            pic['part_icon_clicked'] = cdn + item_pic['part_icon_clicked']
            pic_tup = (int(item_pic['part_id']), pic)
            pic_part.append(pic_tup)
        part_com = build_component_star_part(obj.star_id, pic_part)
        if color_com:
            data['star_color'] = color_com
        if part_com:
            data['star_part'] = part_com
    return data


def build_component_star_part(star_id, res):
    # 根据明星图部位获取图片
    part_com = []
    tabs = get_tabs_index_by_star_id(star_id)
    for tab in tabs:
        pic = {}
        if tab[1] in [part[0] for part in res]:
            for index, part_item in enumerate(res):
                if tab[1] == part_item[0]:
                    pic['part'] = PART_NAME[tab[1]]
                    pic['part_icon_normal'] = part_item[1]['part_icon_normal']
                    pic['part_icon_clicked'] = part_item[1]['part_icon_clicked']
                    part_com.append(pic)
                    del res[index]
                    break
        else:
            pic['part'] = PART_NAME[tab[1]]
            pic['part_icon_normal'] = PART_PICURL[tab[1]]['part_icon_normal']
            pic['part_icon_clicked'] = PART_PICURL[tab[1]]['part_icon_clicked']
            part_com.append(pic)
    return part_com


def build_component_search_sku_lite(obj):
    com = {}
    com_item = {}
    if obj:
        width = '3'
        height = '4'
        main_image = 0
        sku_id = str(obj['sku_id'])
        trackValue = 'item_sku_' + str(sku_id)
        url = obj['url']
        if obj.has_key('has_color'):
            if obj['has_color']:
                main_image = 1
                if obj['color_url']:
                    url = obj['color_url']
        img = get_image_filename_new('backend_images', url)
        if img.filename:
            url = build_sku_items_image_url(img.filename, 1)
            width = str(img.width)
            height = str(img.height)
        else:
            url = get_filename_new('backend_images', url)
            url = build_sku_items_image_url(url, 1)
        com_item['width'] = width
        com_item['height'] = height
        country_msg = get_sku_country_info_new(obj['business_id'])
        if not country_msg:
            country_msg = {'country': '', 'flag': ''}
        com['stateMessage'] = ''
        com['trackValue'] = trackValue
        com['nationalFlag'] = country_msg['flag']
        com['description'] = obj['title']
        com['country'] = country_msg['country']
        com['price'] = str(obj['current_price'])
        com['origin_price'] = str(obj['market_price'])
        com['sales'] = str(obj['sales'])
        com['componentType'] = 'item'
        com['eventIcon'] = get_sku_event_icon(obj['item_id'], obj['goods_id'])
        com['publish_date'] = time.mktime(time.strptime(obj['publish_date'], '%Y-%m-%d %H:%M:%S.000'))
        com['picUrl'] = url
        com['id'] = sku_id
        com['collectionCount'] = '0'
        action = {}
        action['main_image'] = str(main_image)
        action['source'] = 'ecshop'
        action['sourceId'] = str(obj['item_id'])
        action['height'] = height
        action['width'] = width
        action['actionType'] = 'detail'
        action['collectionCount'] = '0'
        action['type'] = 'sku'
        action['id'] = sku_id
        action['trackValue'] = trackValue
        com['action'] = action
        com_item['component'] = com
    return com_item


def build_component_post(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'subjectCell'
        com['id'] = obj.get_component_id()
        com['isMain'] = '1'
        com['imgs'] = obj.get_component_imgs()
        com['publishDate'] = (obj.edit_time).strftime("%Y-%m-%d")
        com['description'] = obj.get_component_content()
        com['embedItems'] = obj.get_component_skus()
        ui['component'] = com
    return ui


def build_component_post_comment(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'subjectCell'
        com['publishDate'] = (obj.ts).strftime("%Y-%m-%d")
        com['id'] = obj.get_component_id()
        com['description'] = obj.get_component_content()
        com['embedItems'] = obj.get_component_skus()
        com['imgs'] = obj.get_component_imgs()
        com['isMain'] = '0'
        ui['component'] = com
        return ui


def build_component_serach_hongren(obj):
    ui = {}
    if obj:
        com = {}
        com['componentType'] = 'hongrenSearch'
        com['userName'] = obj['name']
        com['userTypeName'] = obj['type']
        com['description'] = obj['user_desc']
        if int(obj['avatar_img_id']) > 0:
            avater_img = get_image_by_id(int(obj['avatar_img_id']))
            com['userAvatar'] = avater_img.get_component_user_avatar()
        else:
            com['userAvatar'] = obj['avatar'].replace('http://haobao.com', 'http://m.pimg.cn')
        action = {}
        action['type'] = 'user'
        action['actionType'] = 'detail'
        action['id'] = obj['id']
        com['action'] = action
        ui['component'] = com
    return ui

def rebuild_focus_user_components_by_component(com, user_id):
    if com:
        component = com['component']
        following_id = component['action']['id']
        if component['picUrl']:
            com['component']['action']['userAvatar'] = component['picUrl']
            com['component']['action']['userName'] = component['action']['title']
            com['component']['action'].pop('title')
        else:
            following_user = get_user_by_id(following_id)
            if not following_user:
                return {}
            #com['component']['title'] = following_user.get_component_user_name()
            com['component']['picUrl'] = following_user.get_component_user_avatar()
            com['component']['action']['userAvatar'] = following_user.get_component_user_avatar()
            com['component']['action']['userName'] = following_user.get_component_user_name()
            com['component']['action'].pop('title')
        if user_id:
            com['isfocus'] = str(get_user_follow_status(user_id, following_id))
        else:
            com['isfocus'] = '0'
        com['description'] = ''
        com['userTypeName'] = ''
        com['followType'] = ''
        com['id'] = following_id
        com['focusCount'] = str(forum_followed_count(following_id))
        if user_is_staruser(following_id):
            staruser = get_staruser_by_user_id(following_id)
            com['description'] = staruser.user_desc
            _type = staruser.get_staruser_type()
            com['userTypeName'] = ''
            com['followType'] = ''
            if _type:     
                com['userTypeName'] = _type.get('userTypeName')
                com['followType'] = _type.get('followType')
        return com
    else:
        return {}
