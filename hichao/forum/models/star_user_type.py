# -*- coding:utf-8 -*-

from sqlalchemy import (
    Column,
    VARCHAR,
    TIMESTAMP,
)
from sqlalchemy.dialects.mysql import (
    INTEGER,
    TINYINT,
)
from hichao.forum.models.db import (
    Base,
    new_session,
)
from hichao.util.date_util import TEN_MINUTES, DAY
from hichao.cache.cache import deco_cache
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_forum_star_user_type')


class StarUserType(Base):
    __tablename__ = 'star_user_type'
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255))
    follow_type = Column(VARCHAR(64))
    img_url = Column(VARCHAR(255))
    description = Column(VARCHAR(255))
    review = Column(TINYINT, nullable=False, default=0)
    ts = Column(TIMESTAMP)


@timer
@deco_cache(prefix='get_star_user_category_id', recycle=TEN_MINUTES)
def get_user_type_name(category_id):
    DBSession = new_session()
    star_user = DBSession.query(StarUserType).filter(StarUserType.id == category_id).first()
    DBSession.close()
    return star_user


@timer
@deco_cache(prefix='get_star_user_type_name', recycle=TEN_MINUTES)
def get_star_user_type_name(id):
    rv = ''
    sess = new_session()
    try:
        res = sess.query(StarUserType)\
                  .filter(StarUserType.id == id)\
                  .first()
        if res and res.name:
            rv = rv + res.name
    except Exception, e:
        print Exception, ':', e
        sess.rollback()
    finally:
        sess.close()
    return rv


@timer
@deco_cache(prefix='get_star_user_type_img_url', recycle=TEN_MINUTES)
def get_star_user_type_img_url(id):
    rv = ''
    sess = new_session()
    try:
        res = sess.query(StarUserType)\
                  .filter(StarUserType.id == id)\
                  .first()
        if res and res.img_url:
            rv = rv + res.img_url
    except Exception, e:
        print Exception, ':', e
        sess.rollback()
    finally:
        sess.close()
    return rv
