# -*- coding:utf-8 -*-
from sqlalchemy import (
    Column,
    VARCHAR,
    TEXT,
    BIGINT,
    func,
    Float,
    DateTime,
)
from sqlalchemy.dialects.mysql import INTEGER
from hichao.forum.models.db import (
    Base,
    rdbsession_generator,
    thread_img_dbsession_generator,
)
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MONTH, FIVE_MINUTES
from hichao.util.statsd_client import timeit
import transaction
import traceback

timer = timeit('hichao_backend.m_forum_threadimg')


class ThreadImg(Base):
    __tablename__ = "thread_imgs"
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    thread_id = Column(INTEGER(unsigned=True), nullable=False)
    img_id = Column(INTEGER(unsigned=True), nullable=False)
    review = Column(INTEGER, nullable=False, default=1)

    def __init__(self, thread_id, img_id):
        self.thread_id = thread_id
        self.img_id = img_id


@timer
def add_thread_imgs(thread_id, img_ids):
    DBSession = thread_img_dbsession_generator()
    try:
        for img_id in img_ids:
            new_thread_img = ThreadImg(thread_id=thread_id, img_id=img_id)
            DBSession.add(new_thread_img)
        DBSession.commit()
    except Exception, ex:
        DBSession.rollback()
        print Exception, ex
        print traceback.format_exc()
        return 0
    finally:
        DBSession.close()
    return 1


@timer
@deco_cache(prefix='img_ids_by_thread_id', recycle=FIVE_MINUTES)
def get_img_ids_by_id(thread_id, use_cache=True):
    DBSession = rdbsession_generator()
    ids = DBSession.query(
        ThreadImg.img_id).filter(
        ThreadImg.thread_id == thread_id).filter(
            ThreadImg.review == 1).order_by(
                ThreadImg.img_id).all()
    ids = [id[0] for id in ids]
    DBSession.close()
    return ids


@timer
@deco_cache(prefix='img_ids_by_thread_ids', recycle=FIVE_MINUTES)
def get_img_ids_by_thread_ids(thread_ids, use_cache=True):
    DBSession = rdbsession_generator()
    ids = DBSession.query(
        ThreadImg.img_id).filter(
        ThreadImg.thread_id.in_(thread_ids)).filter(
            ThreadImg.review == 1).all()
    ids = [id[0] for id in ids]
    DBSession.close()
    return ids


@timer
@deco_cache(prefix='thread_img_by_thread_id', recycle=FIVE_MINUTES)
def get_thread_img_by_thread_id(thread_id):
    DBSession = rdbsession_generator()
    res = DBSession.query(
        ThreadImg.img_id).filter(
        ThreadImg.thread_id == int(thread_id)).filter(
            ThreadImg.review == 1).first()
    DBSession.close()
    return res


def main():
    #122549,120997,120256
    res = get_thread_img_by_thread_id(122549)
    print res

if __name__ == "__main__":
    main()
