# -*- coding:utf-8 -*-
from sqlalchemy import (
        Column,
        INTEGER,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.comment.models.db import (
        Base,
        dbsession_generator,
        subthread_img_dbsession_generator,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import (
        MONTH,
        FIVE_MINUTES,
        )
from hichao.base.models.base_component import BaseComponent
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_comment_subthreadimg')

class SubThreadImg(Base, BaseComponent):
    __tablename__ = 'thread_comment_imgs'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    thread_comment_id = Column(INTEGER, nullable = False)
    img_id = Column(INTEGER, nullable = False)
    review = Column(TINYINT, nullable = False, default = 1)

    def __init__(self, thread_comment_id, img_id, review):
        self.thread_comment_id = thread_comment_id
        self.img_id = img_id
        self.review = review

@timer
def add_subthread_imgs(subthread_id, img_ids):
    DBSession = subthread_img_dbsession_generator()
    try:
        for img_id in img_ids:
            subthread_img = SubThreadImg(subthread_id, img_id, review = 1)
            DBSession.add(subthread_img)
        DBSession.commit()
    except Exception, ex:
        print Exception, ex
        DBSession.rollback()
        return 0
    finally:
        DBSession.close()
    return 1

@timer
@deco_cache(prefix = 'img_ids_by_sub_thread_id', recycle = FIVE_MINUTES)
def get_img_ids_by_id(subthread_id, use_cache = True):
    DBSession = dbsession_generator()
    ids = DBSession.query(SubThreadImg.img_id).filter(SubThreadImg.thread_comment_id == int(subthread_id)).filter(SubThreadImg.review == 1).order_by(SubThreadImg.img_id).all()
    ids = [id[0] for id in ids]
    DBSession.close()
    return ids

