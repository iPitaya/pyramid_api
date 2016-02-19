# -*- coding:utf-8 -*-
"""
Edited by lenson in 2013.08.21.
 Inorde to support 'category' in the topic list.
 changes:
 1. add "get_category()" method in class "Topic";
 2. define a function named "build_component_topic_new" with decorator named "build_collection_count";
 3. change related code in method named "get_topic_list";
"""
from hichao.util.statsd_client import timeit
from sqlalchemy import (
    func,
    or_,
    Column,
    INTEGER,
    VARCHAR,
    TEXT,
)
from hichao.topic.models.db import (
    rdbsession_generator,
    Base,
)
from hichao.base.models.base_component import BaseComponent
from hichao.base.config.ui_action_type import TOPIC_DETAIL
from hichao.base.config.ui_component_type import TOPIC_CELL
from hichao.base.config import (
    TOPIC_CATEGORY,
    COMMENT_TYPE_THREAD,
    FAKE_ACTION,
    COUPON_URL,
    BONUS_URL,
    WEB_URL_DOMAIN,
)
from hichao.comment.models.comment import get_comment_count
from hichao.util.image_url import (
    build_default_url,
    build_topic_image_url,
    build_topic_cell_image_url,
    build_topic_drop_image_url,
    remove_image_url_domain,
    build_search_star_list_image_url,
    build_topic_show_big_pic_url,
    build_news_image_url,
    build_topic_image_url_new,
    build_topic_cell_image_url_from_dfs,
)
from hichao.util.date_util import (
    get_date_attr,
    format_digital,
    WEEK_DICT,
    MONTH,
    DAY,
    MINUTE,
    FIVE_MINUTES,
)
from hichao.sku.models.sku import (
    get_old_sku_by_id,
    get_topic_sku_by_id,
    get_sku_by_id,
    Sku,
    sku2dict,
    )
from hichao.star.models.star import get_star_by_star_id
from hichao.forum.models.thread import get_thread_by_id
from hichao.cache.cache import deco_cache
from hichao.collect.models.collect import Collect
from hichao.collect.models.thread import thread_user_count
from hichao.util.collect_util import build_collection_count
from hichao.util.cps_util import get_title_style_by_link
from hichao.topic.config import TOPIC_PV_PREFIX, TOPIC_UV_PREFIX
from hichao.base.lib.redis import redis
from hc.redis.count import Counter, SetCounter
import time
import urllib
import copy
from icehole_client.files_client import get_filename
from hichao.collect.models.fake import collect_count_new
from hichao.util.files_image_info import get_image_filename_new

timer = timeit('hichao_backend.m_topic')
timer_mysql = timeit('hichao_backend.m_topic.mysql')


class Topic(Base, BaseComponent):
    __tablename__ = 'navigator'
    id = Column('navigator_id', INTEGER, primary_key=True)
    navigator = Column(TEXT)
    title = Column(VARCHAR(1024))
    review = Column(INTEGER)
    publish_date = Column(VARCHAR(20))
    locator = Column(TEXT)
    navigator_type = Column(VARCHAR(32))
    url = Column(VARCHAR(256))
    description = Column(VARCHAR(1024))
    cover = Column(VARCHAR(256))
    channel = Column(VARCHAR(32))
    ispublish = Column(INTEGER)
    drop_image = Column(VARCHAR(256))
    image_source = Column(VARCHAR(128))
    star_user_id = Column(INTEGER)

    def get_category(self):
        return TOPIC_CATEGORY.TYPE_2_STR_DICT.get(self.channel, '其它')

    def get_category_id(self):
        return TOPIC_CATEGORY.TYPE_2_INT.get(self.channel, TOPIC_CATEGORY.TYPE_2_INT[TOPIC_CATEGORY.TYPE.DEFAULT])

    def get_navigator(self):
        return eval(self.navigator)

    def is_activity(self):
        if self.channel == u'活动' or self.channel == '活动':
            return True
        else:
            return False

    def has_drop(self):
        if self.drop_image:
            return 1
        else:
            return 0

    def get_locator(self):
        return eval(self.locator)

    def to_ui_action(self):
        action = {}
        action['actionType'] = TOPIC_DETAIL
        action['id'] = self.get_component_id()
        action['unixtime'] = self.get_unixtime()
        action['title'] = self.title
        return action

    def get_collect_type(self):
        return 'topic'

    def to_news_action(self):
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'news'
        action['id'] = self.get_component_id()
        return action

    def get_component_news_pic_url(self):
        return build_news_image_url(self.url)

    def get_component_image_source(self):
        return self.image_source

    def get_component_navigator_type(self):
        return self.navigator_type

    def to_lite_ui_action(self):
        return self.to_ui_action()

    def get_share_image(self):
        obj = {}
        action = {}
        action['shareType'] = 'webpage'
        action['id'] = self.get_component_id()
        action['title'] = self.get_component_title()
        action['description'] = self.get_component_description()
        action['type'] = 'topic'
        if self.cover:
            action['picUrl'] = build_topic_image_url_new(self.cover, 'navigate_images')
        elif self.drop_image:
            action['picUrl'] = build_default_url(remove_image_url_domain(self.drop_image))
        elif self.url:
            action['picUrl'] = build_topic_image_url_new(self.url, 'navigate_images')
        action['detailUrl'] = WEB_URL_DOMAIN + '/share/topic?id=' + self.get_component_id()
        obj['actionType'] = 'share'
        obj['type'] = 'topic'
        obj['typeId'] = self.get_component_id()
        obj['trackValue'] = '{0}_{1}'.format(obj['type'], obj['typeId'])
        obj['share'] = action
        return obj

    def get_component_id(self):
        return str(self.id)

    def get_component_pic_url(self):
        support_webp = getattr(self, 'support_webp', 0)
        str_url = get_filename('navigate_images', self.url)
        return build_topic_image_url(str_url, support_webp)

    def get_component_pic_image(self):
        support_webp = getattr(self, 'support_webp', 0)
        img = get_image_filename_new('navigate_images', self.url) 
        img.filename = build_topic_image_url(img.filename, support_webp)
        return img

    def get_share_pic_url(self):
        return build_topic_image_url(self.url)

    def get_component_flag(self):
        return str(self.publish_date)

    def get_component_title(self):
        return self.title

    def get_component_description(self):
        return self.description

    def get_component_width(self):
        return self.drop_image and '100' or '320'

    def get_component_height(self):
        return self.drop_image and '150' or '140'

    def get_component_drop_pic_url(self):
        support_webp = getattr(self, 'support_webp', 0)
        if self.drop_image:
            return build_topic_drop_image_url(self.drop_image, support_webp)
        else:
            return build_topic_image_url(self.url, support_webp)

    def get_component_common_pic_url(self):
        return self.get_component_drop_pic_url()

    def get_component_top_pic_url(self):
        '''
        预留，暂时没有字段可以指定置顶。
        '''
        return ''

    def get_component_year(self):
        return format_digital(get_date_attr(self.publish_date, 'tm_year'))

    def get_component_month(self):
        return format_digital(get_date_attr(self.publish_date, 'tm_mon'))

    def get_component_day(self):
        return format_digital(get_date_attr(self.publish_date, 'tm_mday'))

    def get_component_week_day(self):
        weekday = get_date_attr(self.publish_date, 'tm_wday')
        return WEEK_DICT[weekday]

    def get_bind_user_id(self):
        return 0

    def get_unixtime(self):
        return int(float(self.publish_date))

    def get_component_pv(self):
        pv_key = TOPIC_PV_PREFIX.format(self.id)
        pv_counter = Counter(redis)
        cnt = pv_counter._byID(pv_key)
        if not cnt:
            cnt = 0
        cnt = int(cnt) + int(collect_count_new(self.id, 350, float(self.publish_date)))
        return str(cnt)

    def get_component_uv(self):
        uv_key = TOPIC_UV_PREFIX.format(self.id)
        uv_counter = SetCounter(redis)
        cnt = uv_counter.count
        if not cnt:
            cnt = 0
        return str(cnt)

    def get_tag_action(self):
        action = {}
        action['actionType'] = 'tag'
        action['type'] = 'topic'
        action['tag'] = self.get_category()
        action['id'] = ''
        return action

    def get_sorted_locators(self):
        '''
        对cell排序，按y值从小到大排，如果y值一样，则y值相同的再按x值排序。
        '''
        return sorted(list(self.get_locator().items()), lambda x, y: x['y'] == y['y'] and int(x['x']) - int(y['x']) or int(x['y']) - int(y['y']),
                      key=lambda x: x[1])

    def get_row_list(self):
        '''
        将cell按行分组。
        '''
        sorted_locators = self.get_sorted_locators()
        total_height = sorted_locators[0][1]['y']           # 记录瀑布流高度（最上为0,往下为正）。为防止出现空行，初始高度置为第一行开始的y值。
        rows = []                                           # 行的数组，每一行为一个列表。每行至少有一个元素。
        row = []                                            # 记录单个行。
        margin_y = 4                                        # 行距
        for cell in sorted_locators:
            # 如果当前cell的y值超过了瀑布流的最大值，则说明已经另起一行了。
            if cell[1]['y'] > total_height:
                rows.append(row)                            # 当前行加到行列表里然后新建一个空的行。
                row = []
                total_height = cell[1]['y'] + cell[1]['height']  # 另起一行后y值加上cell高度当作瀑布流的最大值。

            # 如果当前cell的y值并没有超过瀑布流的最大值，但y值加cell高度超过了，
            # 则说明当前瀑布流并没有达到该行的最下边，修改瀑布流高度。
            elif cell[1]['y'] + cell[1]['height'] > total_height:
                total_height = cell[1]['y'] + cell[1]['height']

            # 没起新行，则把该cell添加到该行列表内。
            row.append(cell)
        rows.append(row)
        return rows

    def to_ui_detail(self, width, txt_with_margin, lite_thread, lite_action=0, support_webp=0, support_ec=0):
        rows = self.get_row_list()
        cells = self.get_navigator()
        cell_rows = []
        cell_builder = topic_cell_builder()
        cell_builder.support_lite_thread = lite_thread
        cell_builder.support_lite_action = lite_action
        cell_builder.support_webp = support_webp
        cell_builder.support_ec = support_ec
        prop = float(width) / 320
        margin_y = 4 * prop

        for row in rows:
            cell_row = {}
            cell_row['cells'] = []
            start_y = row[0][1]['y']
            end_y = row[-1][1]['y'] + row[-1][1]['height']
            row_height = end_y - start_y

            for cell in row:
                idx = cell[0]
                tmp = cells.get(idx, '')
                if not tmp:
                    continue
                cell_dict = tmp[0]
                built_cell = cell_builder.build_topic_cell(cell[1], cell_dict, start_y, prop, txt_with_margin)
                cell_row['cells'].append(built_cell)

            cell_row['height'] = str(row_height * prop + margin_y)              # 每行之间有一个间距
            cell_rows.append(cell_row)
        return cell_rows


class topic_cell_builder(object):

    def __init__(self):
        self.support_lite_thread = 0
        self.support_lite_action = 0
        self.support_webp = 0
        self.support_ec = 0

    def build_topic_cell(self, cell_data, cell_dict, start_y, prop, txt_with_margin):
        cell = {}
        cell['height'] = str(cell_data['height'] * prop)
        cell['y'] = str((cell_data['y'] - start_y) * prop)
        if cell_dict['cell_type'] == 'word' and txt_with_margin:
            cell['width'] = str((cell_data['width'] - 12) * prop)
            cell['x'] = str((cell_data['x'] + 6) * prop)
        else:
            cell['width'] = str(cell_data['width'] * prop)
            cell['x'] = str(cell_data['x'] * prop)
        cell_dict['width'] = int(float(cell['width'])) * 2
        cell['component'] = getattr(self, 'build_topic_%s_cell' % cell_dict['cell_type'], self.build_topic_default_cell)(cell_dict, prop,cell_data)
        return cell

    def build_topic_default_cell(self, *args, **kw):
        return {}

    def build_topic_region_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'cell'
        pic_url = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['picUrl'] = pic_url
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'region'
        action['id'] = cell_dict['star_id']
        cell['action'] = action
        return cell

    def build_topic_map_topic_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'cell'
        pic_url = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['picUrl'] = pic_url
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'theme'
        action['id'] = cell_dict['star_id']
        cell['action'] = action
        return cell

    def build_topic_coupon_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'cell'
        pic_url = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['picUrl'] = pic_url
        action = {}
        title_style = copy.deepcopy(get_title_style_by_link(cell_dict['tag']))
        title_style['text'] = u'领取优惠券'
        action['actionType'] = 'webview'
        action['webUrl'] = COUPON_URL.format(cell_dict['star_id'])
        action['means'] = 'push'
        action['titleStyle'] = title_style
        cell['action'] = action
        return cell

    def build_topic_bonus_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'cell'
        pic_url = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['picUrl'] = pic_url
        action = {}
        title_style = copy.deepcopy(get_title_style_by_link(cell_dict['tag']))
        title_style['text'] = u'领取红包'
        action['actionType'] = 'webview'
        action['webUrl'] = BONUS_URL.format(cell_dict['star_id'])
        action['means'] = 'push'
        action['titleStyle'] = title_style
        cell['action'] = action
        return cell

    def build_topic_ecshop_search_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'cell'
        pic_url = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['picUrl'] = pic_url
        action = {}
        action['actionType'] = 'ecshopSearch'
        action['query'] = cell_dict['title']
        action['id'] = str(cell_dict['star_id'])
        action['title'] = cell_dict['title']
        cell['action'] = action
        return cell

    def build_topic_platform_service_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'cell'
        pic_url = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['picUrl'] = pic_url
        action = {}
        action['actionType'] = 'customer'
        action['id'] = '1'
        cell['action'] = action
        return cell

    def build_topic_thread_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'linkDecoratedCell'
        cell['picUrl'] = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        thread_id = cell_dict['star_id']
        thread = get_thread_by_id(thread_id)
        if thread:
            thread.support_webp = self.support_webp
            if self.support_lite_thread or self.support_lite_action:
                action = thread.to_lite_ui_action()
            else:
                action = thread.to_ui_action(both_img=1)
                coll_count = thread_user_count(thread_id)
                if not coll_count:
                    coll_count = 0
                action['collectionCount'] = str(coll_count)
                comm_count = get_comment_count(COMMENT_TYPE_THREAD, thread_id)
                if not comm_count:
                    comm_count = 0
                action['commentCount'] = str(comm_count)
            cell['action'] = action
        else:
            cell['action'] = {}
        return cell

    def build_topic_word_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'word'
        cell['content'] = cell_dict['tag']
        cell['align'] = cell_dict.get('star_id', 'left')
        cell['fontSize'] = not cell_dict.get('star_name', '') and 'normal' or cell_dict['star_name']
        cell['style'] = cell_dict.get('title', '')
        cell['border'] = cell_dict.get('style')
        cell['action'] = {}
        return cell

    def build_topic_item_cell(self, cell_dict, prop, cell_data):
        sku_id = cell_dict['star_id']               # sku_id 存到了star_id字段里。
        sku = get_topic_sku_by_id(sku_id)
        sku_old = get_sku_by_id(sku_id)
        cell = {}
        cell['componentType'] = 'priceDecoratedCell'
        cell['picUrl'] = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        sku_id = cell_dict['star_id']               # sku_id 存到了star_id字段里。
        if isinstance(sku, Sku):
            sku = sku2dict(sku)
            sku['support_webp'] = self.support_webp
            sku['support_ec'] = self.support_ec
            cell['stateMessage'] = sku.get_sku_state_msg()
            cell['title'] = cell_dict['title']
            if 'show_price' in cell_dict.keys() and int(self.support_lite_thread) == 2:
                if cell_dict['show_price']:
                    cell['componentType'] = 'priceCombinationCell'
                    if cell_dict['activate_logo']:
                        cell['activeIcon'] = build_topic_cell_image_url_from_dfs(cell_dict['activate_logo'], 'navigate_images')
                    else:
                        cell['activeIcon'] = ''
                    if 'foot_pic' in cell_dict.keys() and cell_dict['foot_pic']:
                        cell['foot_pic'] = build_topic_cell_image_url_from_dfs(cell_dict['foot_pic'], 'navigate_images')
                    else:
                        cell['foot_pic'] = ''
                    cell['img_width'] = str(cell_data['width'])
                    cell['img_height'] = str(cell_data['height'])
                    cell['isSaleOver'] = ''
                    if 'is_sale_over' in sku.keys():
                        cell['isSaleOver'] = str(sku.get('is_sale_over'))
                    cell['isEnd'] = ''
                    if 'is_end' in sku.keys():
                        cell['isEnd'] = str(sku.get('is_end'))
                    if cell_dict['show_price'] == u'售价':
                        cell['salePrice'] = sku.get_component_price()
                        if cell['salePrice']:
                            cell['salePrice'] = str(int(float(cell['salePrice'])))
                    elif cell_dict['show_price'] == u'原价':
                        cell['originalPrice'] = sku.get_component_orig_price()
                        if cell['originalPrice']:
                            cell['originalPrice'] = str(int(float(cell['originalPrice'])))
                    elif cell_dict['show_price'] == u'活动价':
                        if 'active_price' in sku.keys():
                            cell['activePrice'] = sku.get_component_active_price()
                            if cell['activePrice']:
                                cell['activePrice'] = str(int(float(cell['activePrice'])))
                        else:
                            cell['activePrice'] = ''
                    elif cell_dict['show_price'] == u'售价＋原价':
                        cell['salePrice'] = sku.get_component_price()
                        if cell['salePrice']:
                            cell['salePrice'] = str(int(float(cell['salePrice'])))
                        cell['originalPrice'] = sku.get_component_orig_price()
                        if cell['originalPrice']:
                            cell['originalPrice'] = str(int(float(cell['originalPrice'])))
                    elif cell_dict['show_price'] == u'活动价＋原价':
                        if 'active_price' in sku.keys():
                            cell['activePrice'] = sku.get_component_active_price()
                            if cell['activePrice']:
                                cell['activePrice'] = str(int(float(cell['activePrice'])))
                        else:
                            cell['activePrice'] = ''
                        cell['originalPrice'] = sku.get_component_orig_price()
                        if cell['originalPrice']:
                            cell['originalPrice'] = str(int(float(cell['originalPrice'])))
                    elif cell_dict['show_price'] == u'售价＋活动价':
                        cell['salePrice'] = sku.get_component_price()
                        if cell['salePrice']:
                            cell['salePrice'] = str(int(float(cell['salePrice'])))
                        if 'active_price' in sku.keys():
                            cell['activePrice'] = sku.get_component_active_price()
                            if cell['activePrice']:
                                cell['activePrice'] = str(int(float(cell['activePrice'])))
                        else:
                            cell['activePrice'] = ''
                else:
                    if sku_old.get('active_price',''):
                        cell['price'] = sku_old.get_component_active_price()
                    else:
                        cell['price'] = sku_old.get_component_price()
                    if cell['price']:
                        cell['price'] = str(int(float(cell['price'])))
            else:
                if sku_old.get('active_price',''):
                    cell['price'] = sku_old.get_component_active_price()
                else:
                    cell['price'] = sku_old.get_component_price()
                if cell['price']:
                    cell['price'] = str(int(float(cell['price'])))
            if sku['source'] == 'ecshop' and not self.support_ec:
                cell['action'] = FAKE_ACTION
            else:
                if self.support_lite_action:
                    cell['action'] = sku.to_lite_ui_action()
                else:
                    cell['action'] = sku.to_ui_action()
            collector = Collect('sku')
            if cell['action']:
                count = collector.user_count_by_item(sku.sku_id, sku.get_unixtime())
                if not count:
                    count = 0
                cell['action']['collectionCount'] = str(count)
            else:
                action = {}
                action['actionType'] = 'toast'
                action['message'] = u'该商品已下架！'
                cell['action'] = action
        else:
            action = {}
            action['actionType'] = 'toast'
            action['message'] = u'该商品已下架！'
            cell['action'] = action
        if cell.has_key('action'):
            cell['action']['main_image'] = 0
        return cell

    def build_topic_item_noprice_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'cell'
        cell['picUrl'] = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        sku = get_sku_by_id(cell_dict['star_id'])
        if isinstance(sku, Sku):
            sku = sku2dict(sku)
            sku['support_webp'] = self.support_webp
            sku['support_ec'] = self.support_ec
            sku['lite_action'] = self.support_lite_action
            cell['action'] = sku.to_ui_action()
        else:
            action = {}
            action['actionType'] = 'toast'
            action['message'] = u'该商品已下架！'
            cell['action'] = action
        return cell

    def build_topic_star_cell(self, cell_dict, prop, cell_data):
        star_id = cell_dict['star_id']
        star = get_star_by_star_id(star_id)
        cell = {}
        cell['componentType'] = 'linkDecoratedCell'
        cell['picUrl'] = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        if star:
            star.support_webp = self.support_webp
            if self.support_lite_action:
                cell['action'] = star.to_lite_ui_action()
            else:
                cell['action'] = star.to_ui_action()
            collector = Collect('star')
            count = collector.user_count_by_item(star_id)
            if not count:
                count = 0
            cell['action']['collectionCount'] = str(count)
        else:
            cell['action'] = {}
        return cell

    def build_topic_image_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'cell'
        pic_url = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['picUrl'] = pic_url
        action = {}
        action['actionType'] = 'showBigPic'
        action['picUrl'] = build_topic_show_big_pic_url(cell_dict['url'], self.support_webp)
        action['noSaveButton'] = '0'
        cell['action'] = action
        return cell

    # 未定
    def build_topic_linkimage_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'linkDecoratedCell'
        cell['picUrl'] = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['action'] = {}
        cell['action']['titleStyle'] = get_title_style_by_link(cell_dict['tag'])
        cell['action']['actionType'] = 'webview'
        cell['action']['webUrl'] = cell_dict['tag']
        if cell_dict['star_id']:
            cell['action']['title'] = cell_dict['star_id']
            cell['action']['titleStyle']['text'] = cell_dict['star_id']
        else:
            cell['action']['title'] = cell['action']['titleStyle']['text']
        cell['action']['means'] = cell_dict['title']
        return cell

    def build_topic_action_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'cell'
        cell['picUrl'] = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        if cell_dict['tag'] == 'trial':
            cell['tag'] = 'trial'
        else:
            cell['action'] = {}
        return cell

    def build_topic_video_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'cell'
        cell['picUrl'] = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['action'] = {}
        cell['action']['actionType'] = 'video'
        cell['action']['videoUrl'] = cell_dict['tag']
        return cell

    # 暂时未定
    def build_topic_webview_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'webview'
        cell['webUrl'] = cell_dict['tag']
        cell['action'] = {}
        return cell

    def build_topic_threadlist_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'linkDecoratedCell'
        cell['picUrl'] = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['action'] = {}
        cell['action']['actionType'] = 'jump'
        cell['action']['type'] = 'thread'
        cell['action']['id'] = cell_dict['star_id']
        cell['action']['child'] = cell_dict['tag']
        return cell

    def build_topic_searchresult_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'linkDecoratedCell'
        cell['picUrl'] = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['action'] = {}
        cell['action']['query'] = cell_dict['tag']
        cell['action']['actionType'] = 'query'
        cell['action']['type'] = cell_dict['style']
        return cell

    def build_topic_topic_cell(self, cell_dict, prop, cell_data):
        cell = {}
        cell['componentType'] = 'cell'
        cell['picUrl'] = build_topic_cell_image_url(cell_dict['url'], cell_dict['width'], self.support_webp)
        cell['action'] = {}
        cell['action']['actionType'] = 'topicDetail'
        cell['action']['id'] = cell_dict['star_id']
        cell['action']['title'] = cell_dict.get('title', '')
        return cell


@timer
@deco_cache(prefix='topic', recycle=FIVE_MINUTES)
@timer_mysql
def get_topic_by_id(topic_id, use_cache=True):
    DBSession = rdbsession_generator()
    topic = DBSession.query(Topic).filter(Topic.id == topic_id).first()
    DBSession.close()
    return topic


@timer
def get_next_topic(publish_date, navigator_type='topic'):
    DBSession = rdbsession_generator()
    topic = DBSession.query(Topic).order_by(Topic.publish_date.desc()).filter(Topic.publish_date <
                                                                              publish_date).filter(Topic.review == 1).filter(Topic.navigator_type == navigator_type).first()
    DBSession.close()
    return topic


@timer
def get_pre_topic(publish_date, navigator_type='topic'):
    DBSession = rdbsession_generator()
    topic = DBSession.query(Topic).order_by(Topic.publish_date).filter(Topic.publish_date >
                                                                       publish_date).filter(Topic.publish_date < time.time()).filter(Topic.review == 1).filter(Topic.navigator_type == navigator_type).first()
    DBSession.close()
    return topic


@timer
def get_topics(publish_date, num, category):
    DBSession = rdbsession_generator()
    topics = DBSession.query(Topic).order_by(Topic.publish_date.desc()).filter(Topic.navigator_type ==
                                                                               'topic')
    if category:
        topics = topics.filter(Topic.channel == category)
    topics = topics.filter(Topic.publish_date < publish_date).filter(Topic.review == 1).limit(num)
    DBSession.close()
    return topics.all()


@timer
@deco_cache(prefix='topic_ids', recycle=MINUTE)
@timer_mysql
def get_topic_ids(publish_date, num, category, use_cache=True):
    DBSession = rdbsession_generator()
    topic_ids = DBSession.query(Topic.id).order_by(Topic.publish_date.desc()).filter(Topic.navigator_type == 'topic')
    if not category:
        topic_ids = topic_ids.filter(Topic.channel != u'服搭专场').filter(Topic.channel != u'美妆专场').filter(Topic.channel != u'达人店铺')
    if category:
        topic_ids = topic_ids.filter(Topic.channel == category)
    topic_ids = topic_ids.filter(Topic.publish_date < publish_date).filter(Topic.review == 1).limit(num).all()
    topic_ids = [topic[0] for topic in topic_ids]
    DBSession.close()
    return topic_ids


@timer
@deco_cache(prefix='news_ids', recycle=MINUTE)
@timer_mysql
def get_news_ids(publish_date, num, category, use_cache=True):
    DBSession = rdbsession_generator()
    news_ids = DBSession.query(Topic.id).order_by(Topic.publish_date.desc()).filter(Topic.navigator_type == 'news')
    news_ids = news_ids.filter(Topic.publish_date < publish_date).filter(Topic.review == 1).limit(num).all()
    news_ids = [topic[0] for topic in news_ids]
    DBSession.close()
    return news_ids


@timer
@deco_cache(prefix='starspace_news_ids', recycle=MINUTE)
@timer_mysql
def get_starspace_news_ids(publish_date, num, star_user_id, use_cache=True):
    DBSession = rdbsession_generator()
    news_ids = DBSession.query(Topic.id).order_by(Topic.publish_date.desc()).filter(Topic.navigator_type == 'news')
    news_ids = news_ids.filter(Topic.star_user_id == int(star_user_id)).filter(Topic.publish_date < publish_date).filter(Topic.review == 1).limit(num).all()
    news_ids = [topic[0] for topic in news_ids]
    DBSession.close()
    return news_ids


@timer
def get_topic_detail_without_cache(topic_id, width, lite_action, support_ec=0):
    DBSession = rdbsession_generator()
    topic = DBSession.query(Topic).filter(Topic.id == topic_id).first()
    DBSession.close()
    topic_detail = {}
    topic_detail['is_activity'] = topic.is_activity()
    topic_detail['shareAction'] = topic.get_share_image()
    topic_detail['title'] = topic.get_component_title()
    topic_detail['items'] = topic.to_ui_detail(width, False, lite_thread=lite_action, lite_action=lite_action, support_ec=support_ec)
    topic_detail['id'] = topic.get_component_id()
    topic_detail['dropImg'] = topic.get_component_drop_pic_url()
    topic_detail['listImg'] = topic.get_component_pic_url()
    return topic_detail


@timer
def get_last_topic_ids():
    tm = int(time.time()) - 7200  # banner中最新专题出现时间推迟两个小时。
    DBSession = rdbsession_generator()
    ids = DBSession.query(Topic.id).filter(Topic.review == 1).filter(
        Topic.publish_date <= tm).filter(func.from_unixtime(Topic.publish_date, '%H:%i').in_(['08:00', '14:00',
                                                                                              '18:00'])).order_by(Topic.publish_date.desc()).limit(6).all()
    DBSession.close()
    ids = [id[0] for id in ids]
    return ids


@timer
def get_setting_more_apps(platform='iphone'):
    # 获取设置页面里的更多应用。
    id = platform == 'iphone' and 4 or 96
    topic = get_topic_by_id(id)
    data = eval(topic.navigator)
    apps = []
    if data:
        apps = data[1]
    items = []
    for app in apps:
        component = {}
        position = "{0}_lite_setting".format(platform)
        component['component'] = build_component_more_app_form_unit(app, position)
        items.append(component)
    return items


@timer
def get_more_app_list(platform='iphone', type='search'):
    # 获取更多应用列表，默认为找一找里的更多女生应用
    # type 取值可以为search和setting。分别返回不同类型的component。
    id = platform == 'iphone' and 9 or 97
    topic = get_topic_by_id(id)
    apps = eval(topic.navigator)[1]
    items = []
    method = type == 'search' and build_component_more_app_form_unit or build_component_more_app_list_unit
    for app in apps:
        component = {}
        position = "{0}_lite_more".format(platform)
        component['component'] = method(app, position)
        items.append(component)
    return items


@timer
def build_component_more_app_form_unit(dct, position):
    com = {}
    com['componentType'] = 'search'
    com['picUrl'] = build_search_star_list_image_url(dct['url'])
    com['word'] = dct['title']
    action = {}
    action['actionType'] = 'openApp'
    action['uri'] = generateMoreAppURL(dct, position)
    action['name'] = dct['title']
    com['action'] = action
    return com


@timer
def build_component_more_app_list_unit(dct, position):
    com = {}
    com['componentType'] = 'appDetail'
    com['picUrl'] = build_search_star_list_image_url(dct['url'])
    com['name'] = dct['title']
    com['description'] = dct['tag']
    action = {}
    action['actionType'] = 'openApp'
    action['uri'] = generateMoreAppURL(dct, position)
    action['name'] = dct['title']
    com['action'] = action
    return com


@timer
def generateMoreAppURL(item, position):
    suffixObj = {}
    suffixObj['link'] = item['star_id'].replace('ifan.me', 'haobao.com')
    suffixObj['name'] = item['title']
    suffixObj['position'] = position
    suffix = urllib.urlencode(suffixObj)
    return u"{0}{1}{2}".format(u"http://haobao.com", u"/statistic/jump?", suffix)

if __name__ == '__main__':
    print get_setting_more_apps(platform='ios')
