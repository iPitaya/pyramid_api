#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, Text, String, VARCHAR, FLOAT, func
from hichao.publish.models.db import dbsession_generator, Base
from hichao.publish.models.const import  SUFFIX
from sqlalchemy.dialects.mysql import TINYINT

class EditorStar(Base):
    __tablename__ = 'star'

    id = Column('star_id', Integer, primary_key = True, autoincrement = True)
    url = Column(VARCHAR(256))
    title = Column(VARCHAR(512))
    description = Column(VARCHAR(2048))
    item_count = Column(Integer)
    tags_waitao = Column(VARCHAR(1048))
    tags_shangyi = Column(VARCHAR(1048))
    tags_qun = Column(VARCHAR(1048))
    tags_lianyiqun = Column(VARCHAR(1048))
    tags_ku = Column(VARCHAR(1048))
    tags_lianyiku = Column(VARCHAR(1048))
    tags_xie = Column(VARCHAR(1048))
    tags_bao = Column(VARCHAR(1048))
    tags_peishi = Column(VARCHAR(1048))
    tags_taozhuang = Column(VARCHAR(1024))
    review = Column(Integer)
    username = Column(VARCHAR(32))
    user_url = Column(VARCHAR(256))
    publish_date = Column(VARCHAR(20))
    recommend_waitao = Column(Text)
    recommend_shangyi = Column(Text)
    recommend_qun = Column(Text)
    recommend_lianyiqun = Column(Text)
    recommend_ku = Column(Text)
    recommend_lianyiku = Column(Text)
    recommend_xie =  Column(Text)
    recommend_bao = Column(Text)
    recommend_peishi = Column(Text)
    recommend_taozhuang = Column(Text)
    style = Column(VARCHAR(64))
    star_name = Column(VARCHAR(20))
    height = Column(Integer)
    width = Column(Integer)
    ispublish = Column(Integer)
    fpublish_date = Column(FLOAT)
    video_url = Column(VARCHAR(1024))
    score = Column(FLOAT)
    nstyle = Column(VARCHAR(255))
    scene = Column(VARCHAR(255))
    shape = Column(VARCHAR(255))
    is_selfie = Column(TINYINT, nullable = False, default = 0)

def editor_publish_star_count(publish_date, review=1, ispublish=1):
    DBSession = dbsession_generator()
    star_count = DBSession.query(func.count(EditorStar.id)).filter\
            (EditorStar.review==review, EditorStar.ispublish==ispublish, EditorStar.publish_date > publish_date).first()
    DBSession.close()
    if star_count:
        return star_count[0]
    return 0

def editor_publish_star_list(publish_date, review=1, ispublish=1, limit=100, offset=0):
    """
    review=1, ispublish=1 时取到已发布的明星图。
    review=2, ispublish=0 时取到专题里的明星图。"""
    DBSession = dbsession_generator()
    star_list = DBSession.query(EditorStar).order_by(EditorStar.publish_date).filter\
            (EditorStar.review==review, EditorStar.ispublish==ispublish, EditorStar.publish_date > publish_date).offset(offset).limit(limit).all()
    DBSession.close()
    return star_list

def get_editor_star_by_star_id(star_id):
    DBSession = dbsession_generator()
    star = DBSession.query(EditorStar).filter(EditorStar.id==star_id).first()
    DBSession.close()
    return star
if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

