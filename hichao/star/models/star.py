# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        TEXT,
        DECIMAL,
        func,
        )
from hichao.star.models.db import(
        dbsession_generator,
        rdbsession_generator,
        Base
        )
from hichao.star.models.star_sku import (
        get_tabs_index_by_star_id,
        get_skus_by_star_tab,
        )
from hichao.sku.models.sku import (
        get_sku_by_id,
        )
from hichao.util.image_url import (
        build_video_url,
        build_star_fall_image_url,
        build_star_detail_image_url,
        build_re_crop_image_url,
        build_fake_user_avatar_url,
        get_normal_image_path,
        get_fall_image_path,
        )
from hichao.util.date_util import (
        format_star_publish_date,
        FOREVER,
        MINUTE,
        FIVE_MINUTES,
        TEN_MINUTES,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.util.pack_data import pack_data
from hichao.user.models.user import get_user_by_id
from hichao.base.config.ui_component_type import FALL_STAR_CELL
from hichao.base.config.ui_action_type import STAR_DETAIL
from hichao.base.config.sku_part import PART_NAME
from hichao.base.models.base_component import BaseComponent
from hichao.base.config import FALL_PER_PAGE_NUM, MYSQL_MAX_INT
from hichao.publish.models.old_user import fake_user_dict
from hichao.cache.cache import deco_cache
from hichao.collect.models.collect import Collect
from hichao.util.statsd_client import timeit
from icehole_client.files_client import get_filename as get_img_file
from random import randint
import transaction

IMAGE_FILENAME_SPACE = 'backend_images'
fake_users = fake_user_dict()

timer = timeit('hichao_backend.m_star')
timer_mysql = timeit('hichao_backend.m_star.mysql')

class Star(Base, BaseComponent):
    __tablename__ = 'star'
    iid = Column('id', INTEGER, primary_key = True, autoincrement = True)
    star_id = Column(INTEGER, unique = True, index = True)
    url = Column(VARCHAR(256), nullable = False)
    title = Column(VARCHAR(256), nullable = True)
    description = Column(TEXT, nullable = True)
    style = Column(VARCHAR(60), nullable = True)
    star_name = Column(VARCHAR(60), nullable = True)
    user_id = Column(INTEGER, nullable = False)
    height = Column(INTEGER, nullable = False)
    width = Column(INTEGER, nullable= False)
    video_url = Column(VARCHAR(1024), nullable = True)
    publish_date = Column(DECIMAL(20,2), nullable = False)
    score = Column(DECIMAL(10, 2), nullable = False, default = 0)
    review = Column(INTEGER, nullable = False, default = 0)
    nstyle = Column(VARCHAR(255), nullable = False, default = '')
    scene = Column(VARCHAR(255), nullable = False, default = '')
    shape = Column(VARCHAR(255), nullable = False, default = '')
    sku_count = Column(INTEGER, nullable = False, default = 0)
    is_selfie = Column(TINYINT, nullable = False, default = 0)

    def __init__(self, star_id, url, user_id, width, height, publish_date, score = 0, description = '', video_url = '', title
            = '', style = '', star_name = '', review = 0, nstyle = '', scene = '', shape = '', sku_count = 0, is_selfie = 0):
        self.star_id = star_id
        self.url = url
        self.user_id = user_id
        self.width = width
        self.height = height
        self.publish_date = publish_date
        self.score = score
        self.description = description
        self.video_url = video_url
        self.title = title
        self.style = style
        self.star_name = star_name
        self.review = review
        self.nstyle = nstyle
        self.scene = scene
        self.shape = shape
        self.sku_count = sku_count
        self.is_selfie = is_selfie

    def __getitem__(self, key):
        return getattr(self, key)

    def get_component_id(self):
        return str(self.star_id)
    
    def get_component_tag(self):
        com_list = []
        nstyle_list = []
        scene_list = []
        shape_list = []
        if self.nstyle:
            nstyle_list = self.nstyle.split(';')
        if self.scene:
            scene_list = self.scene.split(';')
        if self.shape:
            shape_list = self.shape.split(';')
        tag_list = nstyle_list+scene_list+shape_list
        for tag in tag_list:
            item_list = {}
            item_list['tag'] = '#'+tag
            item_list['componentType'] = 'starTag'
            action = {}
            action['actionType'] = 'query'
            action['type'] = 'star'
            action['query'] = tag
            item_list['action'] = action
            com_list.append(item_list)
        return com_list
              
    def get_component_pic_url(self, crop = False):
        support_webp = getattr(self, 'support_webp', 0)
        if crop:
            width = self.get_component_width(crop)
            height = self.get_component_height(crop)
            return build_re_crop_image_url(get_img_file(IMAGE_FILENAME_SPACE, self.url), width, height, (self.width - float(width))/2, 0, support_webp)
        else:
            #return build_star_image_url(get_img_file(IMAGE_FILENAME_SPACE, get_fall_image_path(self.url)), type_flag = 'wfall')
            return build_star_fall_image_url(get_img_file(IMAGE_FILENAME_SPACE, self.url), support_webp)

    def get_component_common_pic_url(self):
        return self.get_component_pic_url(crop = False)

    # 如果crop为True，则把图片宽高定为4：3.
    def get_component_width(self, crop = False):
        if crop:
            if float(self.width) / self.height < 0.75:
                return str(int(self.width))
            else:
                return str(int(self.height * 0.75))
        else:
            return str(int(self.width))

    # 如果crop为True，则把图片宽高定为4：3.
    def get_component_height(self, crop = False):
        if crop:
            if float(self.width) / self.height < 0.75:
                return str(int(self.width / 0.75))
            else:
                return str(int(self.height))
        else:
            return str(int(self.height))

    def get_component_description(self):
        desc = unicode(self.description)
        if len(desc) > 25:
            return desc[0:randint(25, 30)] + '...'
        else:
            return desc

    def get_component_publish_date(self):
        return str(self.publish_date)

    def get_collection_id(self):
        return self.star_id

    def get_collection_type(self):
        return 'star'

    def get_normal_pic_url(self):
        support_webp = getattr(self, 'support_webp', 0)
        return build_star_detail_image_url(get_img_file(IMAGE_FILENAME_SPACE, self.url), support_webp)

    def get_video_url(self):
        if self.video_url:
            return build_video_url(self.video_url)
        else:
            return ''

    def get_tabs_info(self):
        support_webp = getattr(self, 'support_webp', 0)
        tabs = self.get_tabs_index()
        tabs_info = []
        for idx in tabs:
            skus = get_skus_by_star_tab(self.star_id, idx)
            sku_id = skus[0].sku_id
            sku = get_sku_by_id(sku_id)
            tab = {}
            if sku:
                sku['support_webp'] = support_webp
                tab['picUrl'] = sku.get_small_pic_url()
                tab['part'] = PART_NAME[idx[1]]
            tabs_info.append(tab)
        return tabs_info

    def get_fake_user(self):
        global fake_users
        return fake_users[self.user_id]

    def get_bind_user_id(self):
        return get_user_by_id(self.user_id).id

    def get_tabs_index(self):
        return get_tabs_index_by_star_id(self.star_id)

    def get_date(self):
        return format_star_publish_date(self.publish_date)

    def get_unixtime(self):
        return int(self.publish_date)

    def get_component_content(self):
        return self.description

    def get_component_user_name(self):
        return self.get_fake_user().username

    def get_component_user_avatar(self):
        support_webp = getattr(self, 'support_webp', 0)
        return build_fake_user_avatar_url(self.get_fake_user().url, support_webp)

    def get_component_item_count(self):
        return str(self.sku_count)

    def to_ui_action(self):
        lite_action = getattr(self, 'lite_action', '')
        if lite_action: return self.to_lite_ui_action()
        action = {}
        action['id'] = self.get_component_id()
        action['unixtime'] = self.get_unixtime()
        action['actionType'] = STAR_DETAIL
        action['userName'] = self.get_fake_user().username
        action['userId'] = str(self.user_id)
        action['userPicUrl'] = self.get_component_user_avatar()
        action['description'] = self.description
        action['width'] = str(self.width)
        action['height'] = str(self.height)
        action['videoUrl'] = self.get_video_url()
        action['title'] = self.title
        action['dateTime'] = self.get_date()
        action['normalPicUrl'] = self.get_normal_pic_url()
        action['itemPicUrlList'] = self.get_tabs_info()
        return action

    def to_lite_ui_action(self):
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'star'
        action['id'] = self.get_component_id()
        action['width'] = self.get_component_width()
        action['height'] = self.get_component_height()
        action['normalPicUrl'] = self.get_normal_pic_url()
        return action


@timer
def add_star(star_id, url, user_id, width, height, publish_date, score = 0, description = '', video_url = '', title =
        '', style = '', star_name = '', review = 0, nstyle = '', scene = '', shape = '', sku_count = 0, is_selfie = 0):
    star = Star(star_id, url, user_id, width, height, publish_date, score, description, video_url, title, style,
            star_name, review, nstyle, scene, shape, sku_count, is_selfie)
    try:
        DBSession = dbsession_generator()
        DBSession.add(star)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ':', ex
        return 0
    finally:
        DBSession.close()
    return 1

@timer
def update_star(star):
    try:
        star_id = star.star_id
        DBSession = dbsession_generator()
        DBSession.add(star)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ':', ex
        return 0
    finally:
        DBSession.close()
        get_star_by_star_id(star_id, use_cache = False)
    return 1

@timer
@deco_cache(prefix = 'star_by_star_id', recycle = FOREVER)
@timer_mysql
def get_star_by_star_id(star_id, use_cache = True):
    assert star_id
    DBSession = rdbsession_generator()
    star = DBSession.query(Star).filter(Star.star_id == star_id).filter(Star.review == 1).first()
    DBSession.close()
    return star

@timer
def get_star_by_iid(iid):
    star_id = get_starid_by_id(iid)
    if not star_id:
        return None
    return get_star_by_star_id(star_id)

@timer
@deco_cache(prefix = 'star_id_by_iid', recycle = FOREVER)
@timer_mysql
def get_star_id_by_iid(iid, use_cache = True):
    assert iid
    DBSession = rdbsession_generator()
    star_id = DBSession.query(Star.star_id).filter(Star.iid == iid).filter(Star.review == 1).first()
    if star_id:
        star_id = star_id[0]
    DBSession.close()
    return star_id

@timer
def get_all_stars():
    DBSession = rdbsession_generator()
    star_ids = DBSession.query(Star.star_id).filter(Star.review == 1).all()
    DBSession.close()
    return star_ids

@timer
def get_last_publish_date(review=1):
    DBSession = rdbsession_generator()
    last_date = DBSession.query(func.max(Star.publish_date)).filter(review==review).first()
    DBSession.close()
    if not last_date:
        return 0
    else:
        return last_date[0]

@timer
def get_stars_by_star_name(star_name, offset, num):
    DBSession = rdbsession_generator()
    star = DBSession.query(Star).filter(Star.star_name == star_name).order_by(Star.publish_date.desc()).offset(offset).limit(num).all()
    DBSession.close()
    return star

@timer
@deco_cache(prefix = 'stars_selfie', recycle = MINUTE)
def get_selfie_star_ids(offset = MYSQL_MAX_INT, num = FALL_PER_PAGE_NUM):
    DBSession = rdbsession_generator()
    stars = DBSession.query(Star.star_id).filter(Star.is_selfie == 1).filter(Star.publish_date < offset).order_by(Star.publish_date.desc()).limit(num).all()
    if stars: stars = [star[0] for star in stars]
    DBSession.close()
    return stars

@timer
@deco_cache(prefix = 'star_action', recycle = FIVE_MINUTES)
@timer_mysql
def get_star_action_by_star_id(star_id, use_cache = True):
    star = get_star_by_star_id(star_id)
    if not star:
        return {}
    action = star.to_ui_action()
    count = Collect('star').user_count_by_item(star_id, star.get_unixtime())
    action['collectionCount'] = str(count)
    return action

if __name__ == '__main__':
    print build_star_component('star', 36169)

