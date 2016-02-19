# -*- coding:utf-8 -*-

from sqlalchemy import(
        Column,
        INTEGER,
        VARCHAR,
        SMALLINT,
        BIGINT,
        func,
        )
from hichao.config.models.db import (
        dbsession_generator,
        Base,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import FIVE_MINUTES
from hichao.util.image_url import (
        remove_image_url_domain,
        build_default_url,
        )
from hichao.util.statsd_client import timeit
import time

timer = timeit('hichao_backend.m_config_splash')

class Splash(Base):
    __tablename__ = 'splash'
    id = Column(INTEGER, primary_key = True)
    url = Column(VARCHAR(256), nullable = False)
    comment = Column(VARCHAR(256), nullable = True)
    width = Column(INTEGER, nullable = False)
    height = Column(INTEGER, nullable = False)
    review = Column(SMALLINT, nullable = False, default = 0)
    publish_date = Column(BIGINT, nullable = False)
    version = Column(INTEGER, nullable = False)

    def __init__(url, width, height, publish_date, version, review = 0, comment = ''):
        self.url = url
        self.width = width
        self.height = height
        self.publish_date = publish_date
        self.version = version
        self.review = review
        self.comment = comment
        self.aspect_ratio = self.getAspectRatio(width, height)

    def get_aspect_ratio(self):
        return float(self.width)/self.height

    def get_match_aspect_ratio(self, width, height):
        return float(self.width + width)/(self.height + height)

    def get_dict(self):
        res = {}
        res['version'] = str(self.version)
        res['url'] = self.get_component_pic_url()
        return res

    def get_component_pic_url(self):
        return build_default_url(remove_image_url_domain(self.url))

    def __repr__(self):
        return 'id:%s\nversion:%s\nurl:%s\ncomment:%s' % (self.id, self.version, self.url, self.comment)

@timer
@deco_cache(prefix = 'last_splash_version', recycle = FIVE_MINUTES)
def get_last_splash_version(use_cache = True):
    DBSession = dbsession_generator()
    last_version = DBSession.query(Splash.version).filter(Splash.publish_date <= time.time()).filter(Splash.review == 1).order_by(Splash.id.desc()).first()
    DBSession.close()
    if not last_version:
        last_version = 0
    else:
        last_version = last_version[0]
    return last_version

@timer
@deco_cache(prefix = 'last_splashs', recycle = FIVE_MINUTES)
def get_last_splashs(use_cache = True):
    DBSession = dbsession_generator()
    splash = DBSession.query(Splash).filter(Splash.version == get_last_splash_version()).filter(Splash.review == 1).all()
    DBSession.close()
    return splash

@timer
def get_match_splash(width, height):
    splashs = get_last_splashs()
    matched_splash = None
    min_diff = -1
    for _splash in splashs:
        diff = abs(_splash.get_match_aspect_ratio(width, height) - _splash.get_aspect_ratio())
        if min_diff == -1:
            min_diff = diff
            matched_splash = _splash
        if diff < min_diff:
            matched_splash = _splash
    return matched_splash

if __name__ == '__main__':
    Base.metadata.create_all()
