# -*- coding:utf-8 -*-
from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        TEXT,
        BIGINT,
        TIMESTAMP,
        func,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.upload.models.db import (
        Base,
        rdbsession_generator,
        engine,
        )
from hichao.base.models.base_component import BaseComponent
from hichao.util.image_url import (
        build_upload_image_url,
        build_upload_image_fall_url,
        build_upload_user_avatar_url,
        )
from hichao.util.date_util import HALF_MONTH
from hichao.cache.cache import deco_cache, deco_cache_m
from hichao.util.statsd_client import timeit
import time
import transaction

from hichao.base.lib.timetool import today_days

timer = timeit('hichao_backend.m_upload_image')

class Image(Base, BaseComponent):
    __tablename__ = "image"
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    user_id = Column(INTEGER, nullable = False)
    url = Column(VARCHAR(128), nullable = False) # 相对
    height = Column(INTEGER, nullable = False)
    width= Column(INTEGER, nullable = False)
    days = Column(INTEGER, nullable = False)
    rotate = Column(INTEGER, nullable = False, default = 0)
    ts = Column(TIMESTAMP, nullable = False)
    namespace = Column(VARCHAR(32), nullable = False, default = '')
    src = Column(VARCHAR(16), nullable = False, default = '')
    review = Column(TINYINT, nullable = False, default = 1)

    def __init__(self, user_id, url, height, width):
        self.user_id = user_id
        self.url = url
        self.height = height
        self.width = width
        if not Base.metadata.bind.has_table(self.__tablename__):
            self.metadata.create_all()

    def uploaded_from_mxyc(self):
        if self.src:
            return 1
        return 0

    def get_url(self):
        if self.uploaded_from_mxyc():
            return '{0}/{1}'.format(self.namespace, self.url)
        return self.url

    def get_component_pic_fall_url(self, crop = False):
        support_webp = getattr(self, 'support_webp', 0)
        if crop:
            if self.height > self.width:
                x = 0
                y = 0
                w = self.width
                return build_upload_image_fall_url(self.get_url(), self.rotate, w, x, y, crop, self.uploaded_from_mxyc(), support_webp)
            else:
                x = (self.width - self.height)/2
                y = 0
                w = self.height
                return build_upload_image_fall_url(self.get_url(), self.rotate, w, x, y, crop, self.uploaded_from_mxyc(), support_webp)
        return build_upload_image_fall_url(self.get_url(), self.rotate, 0, 0, 0, crop, self.uploaded_from_mxyc(), support_webp)

    def get_component_pic_detail_url(self):
        support_webp = getattr(self, 'support_webp', 0)
        return build_upload_image_url(self.get_url(), self.rotate, self.uploaded_from_mxyc(), support_webp)

    def get_component_user_avatar(self):
        return build_upload_user_avatar_url(self.get_url(), self.uploaded_from_mxyc())

    def get_component_width(self):
        return str(self.width)

    def get_component_height(self):
        return str(self.height)

@timer
#image = Image(1, 'http://imtime.qiniudn.com/2013-07-09-0a8c67cb939043ce027726faf7e07364', 300, 400)
def add_image(user_id, url, height, width, rotate, days = '', ts = ''):
    # image = Image(user_id, url, height, width, days, ts)
    # try:
    #     DBSession = dbsession_generator()
    #     DBSession.add(image)
    #     transaction.commit()
    # except Exception, ex:
    #     transaction.abort()
    #     print Exception, ex
    #     return 0
    # finally:
    #     DBSession.close()
    # return 1
    if not days: days = today_days()
    if not ts: ts = time.time()
    image = (user_id, url, height, width, rotate, days, ts)
    try:
        connection = engine.connect()
        result = connection.execute("INSERT INTO image (user_id, url, height, width, rotate, days, ts) VALUES \
                                                    (%s,%s,%s,%s,%s,%s, FROM_UNIXTIME(%s))", image)
        last_id = result.lastrowid
    except Exception, e:
        print Exception, e
        return 0
    finally:
        connection.close()
    return last_id

@timer
@deco_cache(prefix = 'upload_img', recycle = HALF_MONTH)
def get_image_by_id(img_id, use_cache = True):
    DBSession = rdbsession_generator()
    image = DBSession.query(Image).filter(Image.id == img_id).first()
    DBSession.close()
    return image

@timer
@deco_cache_m(prefix = 'upload_img', recycle = HALF_MONTH)
def get_images_by_id(img_ids, use_cache = False):
    img_ids = [int(_id) for _id in img_ids]
    if not img_ids: return []
    DBSession = rdbsession_generator()
    images = DBSession.query(Image.id, Image).filter(Image.id.in_(img_ids)).all()
    images = dict(images)
    DBSession.close()
    return images

