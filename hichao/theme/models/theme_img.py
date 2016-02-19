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
from hichao.base.models.base_component import BaseComponent
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MINUTE
from hichao.util.image_url import build_theme_image_url
from icehole_client.files_client import get_filename as get_img_file

IMAGE_FILENAME_SPACE = 'navigate_images'

timer = timeit('hichao_backend.m_theme_img')

class ThemeImg(Base, BaseComponent):
    __tablename__ = 'news_image_small'
    id = Column(INTEGER, primary_key = True)
    image = Column(VARCHAR(512))
    sub_id = Column(INTEGER)
    add_datetime = Column(DateTime)
    is_original_img = Column(TINYINT)
    review = Column('status', TINYINT)

    def get_component_pic_url(self, width = 640):
        str_url = get_img_file(IMAGE_FILENAME_SPACE, self.image)
        return build_theme_image_url(str_url, width)

@timer
@deco_cache(prefix = 'theme_imgs', recycle = MINUTE)
def get_imgs_by_theme_id(theme_id):
    DBSession = rdbsession_generator()
    imgs = DBSession.query(ThemeImg).filter(ThemeImg.sub_id == theme_id).filter(ThemeImg.review == 1).filter(ThemeImg.is_original_img == 0).order_by(ThemeImg.id).all()
    DBSession.close()
    return imgs

