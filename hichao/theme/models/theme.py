# -*- coding:utf-8 -*-
from hichao.util.statsd_client import timeit
from sqlalchemy import (
    func,
    Column,
    INTEGER,
    VARCHAR,
    DateTime,
)
from sqlalchemy.dialects.mysql import TINYINT
from hichao.theme.models.db import (
    rdbsession_generator,
    Base,
)
from hichao.util.image_url import (
    build_theme_drop_image_url,
    build_banner_theme_image_url,
    )
from icehole_client.files_client import get_image_filename, get_filename as get_img_file
from hichao.base.models.base_component import BaseComponent
from hichao.theme.models.theme_img import get_imgs_by_theme_id
from hichao.theme.models import zuixintag
from hichao.theme.models.theme_anchor import get_anchors_by_theme_id
from hichao.theme.models.tag import get_tag_by_id
from hichao.theme.models.theme_tag import (
    ThemeTag,
    get_tag_ids_by_theme_id,
    )
from hichao.theme.config import THEME_PV_PREFIX
from hichao.cache.cache import deco_cache
from hichao.util.date_util import (
    MINUTE,
    TEN_SECONDS,
    format_digital,
    ZHOU_DICT,
    FIVE_MINUTES
    )
from hichao.app.models.db import DBSession
from hichao.base.config import THEME_SHARE_URL
from hichao.base.lib.redis import redis
from hc.redis.count import Counter, SetCounter
import datetime
import time
import json
from hichao.collect.models.fake import collect_count_new 
from hichao.util.files_image_info import get_image_filename_new

timer = timeit('hichao_backend.m_theme')
DROP_IMAGE_FILENAME_SPACE = 'navigate_images'

class Theme(Base, BaseComponent):
    __tablename__ = 'news_themes'
    id = Column(INTEGER, primary_key=True)
    title = Column('name', VARCHAR(255))
    description = Column(VARCHAR(1024))
    review = Column('status', TINYINT)
    add_datetime = Column(DateTime)
    publish_date = Column(DateTime)
    drop_image = Column(VARCHAR(255))
    width = Column(INTEGER)
    height = Column(INTEGER)
    banner_image = Column(VARCHAR(255))
    reject_new = Column(INTEGER)

    def get_component_id(self):
        return str(self.id)

    def get_component_drop_pic_url(self):
        str_url = get_img_file(DROP_IMAGE_FILENAME_SPACE, self.drop_image)
        return build_theme_drop_image_url(str_url)

    def get_component_pic_url(self):
        str_url = get_img_file(DROP_IMAGE_FILENAME_SPACE, self.banner_image)
        return build_banner_theme_image_url(str_url)
    
    def get_component_pic_image(self):
        img = get_image_filename_new(DROP_IMAGE_FILENAME_SPACE, self.banner_image) 
        img.filename = build_banner_theme_image_url(img.filename)
        return img

    def get_component_width_and_height(self):
        image_size = get_image_filename(DROP_IMAGE_FILENAME_SPACE, self.drop_image)
        return image_size

    def get_component_drop_width(self):
        image_size = self.get_component_width_and_height()
        if str(image_size.width) != '0':
            return str(image_size.width)
        else:
            return '100'

    def get_component_drop_height(self):
        image_size = self.get_component_width_and_height()
        if str(image_size.height) != '0':
            return str(image_size.height)
        else:
            return '150'

    def get_component_width(self):
        return '320'

    def get_component_height(self):
        return '140'

    def get_component_title(self):
        if self.title:
            return str(self.title)
        else:
            return ''

    def get_category(self):
        #tag = self.get_one_tag()
        #if tag: return tag.get_component_tag()
        return '穿搭志'

    def get_component_top_pic_url(self):
        return ''

    def get_component_description(self):
        if self.description:
            return str(self.description)
        else:
            return ''
    
    def get_component_flag(self):
        return self.publish_date.strftime('%Y-%m-%d %H:%M:%S')

    def get_unixtime(self):
        return int(time.mktime(self.publish_date.timetuple()))

    def get_bind_imgs(self):
        imgs = []
        img_objs = get_imgs_by_theme_id(self.id)
        for img_obj in img_objs:
            imgs.append({'url': img_obj.get_component_pic_url()})
        return imgs

    def get_bind_anchors(self):
        anchors = []
        anchor_objs = get_anchors_by_theme_id(self.id)
        for anchor in anchor_objs:
            anchors.append(anchor.to_ui_detail(self.width, self.height))
        return anchors

    def get_bind_tags(self):
        tags = []
        tag_ids = get_tag_ids_by_theme_id(self.id)
        for tag_id in tag_ids:
            tag = get_tag_by_id(tag_id)
            if tag:
                com = {}
                com['tag'] = tag.get_component_tag()
                com['action'] = json.dumps(tag.to_ui_action())
                tags.append(com)
        return tags

    def get_component_year(self):
        return format_digital(getattr(self.publish_date, 'year'))

    #def get_component_month(self):
    #   return '{0}/{1}'.format(format_digital(getattr(self.publish_date, 'month')), int(self.get_component_year()) % 100)
    
    def get_component_month(self):
        return format_digital(getattr(self.publish_date, 'month'))    

    def get_component_day(self):
        return format_digital(getattr(self.publish_date, 'day'))

    def get_component_week_day(self):
        weekday = getattr(self.publish_date, 'weekday')()
        return ZHOU_DICT[weekday]

    def get_component_pv(self):
        item = self.get_bind_item()
        return item.get_component_pv()

    def get_one_tag_id(self):
        tag_ids = get_tag_ids_by_theme_id(self.id)
        if tag_ids: return tag_ids[0]
        return 0

    def get_one_tag(self):
        tag_id = self.get_one_tag_id()
        if tag_id: return get_tag_by_id(tag_id)
        return None

    def get_tag_action(self):
        #tag = self.get_one_tag()
        #if tag: return tag.to_ui_action()
        return {'actionType':'tag', 'tag':'', 'id':'', 'type':'theme'}

    def get_collect_type(self):
        return 'theme'

    def get_component_pv(self):
        pv_key = THEME_PV_PREFIX.format(self.get_component_id())
        pv_counter = Counter(redis)
        cnt = pv_counter._byID(pv_key)
        if not cnt: cnt = 0
        cnt = int(cnt) + int(collect_count_new(self.id,300,float(self.get_unixtime())))
        return str(cnt)

    def to_ui_action(self):
        action = {}
        action['actionType'] = 'detail'
        action['id'] = self.get_component_id()
        action['type'] = 'theme'        
        return action

    def to_ui_detail(self):
        data = {}
        data['title'] = self.get_component_title()
        data['images'] = self.get_bind_imgs()
        data['anchors'] = self.get_bind_anchors()
        data['tags'] = self.get_bind_tags()
        data['share'] = self.get_share_action()
        return data

    def get_share_action(self):
        share = {}
        share['actionType'] = 'share'
        action = {}
        action['shareType'] = 'webpage'
        action['title'] = self.get_component_title()
        action['description'] = self.get_component_description()
        action['picUrl'] = self.get_component_drop_pic_url()
        action['detailUrl'] = THEME_SHARE_URL.format(self.get_component_id())
        share['share'] = action
        return share


@timer
@deco_cache(prefix='theme', recycle=FIVE_MINUTES)
def get_theme_by_id(theme_id, use_cache=True):
    DBSession = rdbsession_generator()
    theme = DBSession.query(Theme).filter(Theme.id == theme_id).first()
    DBSession.close()
    return theme


@timer
@deco_cache(prefix='theme_ids', recycle=TEN_SECONDS)
def get_latest_theme_ids(flag, num=20, use_cache=True):
    #time_now = datetime.datetime.now()
    DBSession = rdbsession_generator()
    theme_ids = DBSession.query(
        Theme.id).filter(
        Theme.publish_date < flag).filter(Theme.review == 1).filter(Theme.reject_new == 0).order_by(Theme.publish_date.desc()).limit(num).all()
    DBSession.close()
    theme_ids = [id[0] for id in theme_ids]
    return theme_ids


@timer
@deco_cache(prefix='themes', recycle=MINUTE)
def get_latest_themes(flag, num, use_cache=True):
    DBSession = rdbsession_generator()
    themes = DBSession.query(
        Theme).filter(
        Theme.publish_date < flag).filter(Theme.review == 1).order_by(Theme.publish_date.desc()).limit(num).all()
    DBSession.close()
    return themes

@timer
@deco_cache(prefix='themes_tag_id', recycle=MINUTE)
def get_theme_ids_by_tag_id(flag , tag_id=0, num=20 , use_cache=True):
    if not tag_id:
        res = get_latest_theme_ids(flag, num, use_cache=True)
    elif int(tag_id) == int(zuixintag):
        res = get_latest_theme_ids(flag, num, use_cache=True)
    else:
        DBSession = rdbsession_generator()
        theme_ids = DBSession.query(Theme.id).join(ThemeTag, ThemeTag.sub_id == Theme.id).filter(Theme.publish_date < flag).filter(
            ThemeTag.tag_id == int(tag_id)).filter(Theme.review == 1).order_by(ThemeTag.order_num.desc()).order_by(
                Theme.publish_date.desc()).limit(num).all()
        DBSession.close()
        res = [id[0] for id in theme_ids]
    return res

def main():
    flag = datetime.datetime.now()
    print flag
    num = 20
    tag = 3
    print tag
   
    res = get_theme_ids_by_tag_id(flag,tag)
    print res 
    return  res

if __name__ == "__main__":
    main()
