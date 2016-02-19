# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        TIMESTAMP,
        VARCHAR,
        )
from sqlalchemy.dialects.mysql import (
        TINYINT,
        INTEGER,
        )
from hichao.forum.models.db import (
        Base,
        dbsession_generator,
        )
from hichao.user.models.user import get_user_by_id
from hichao.util.date_util import TEN_MINUTES, DAY
from hichao.cache.cache import deco_cache
from hichao.forum.models.forum import get_forum_name_by_cat_id
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_forum_banwu_tangzhu')

class BanWuTangZhu(Base):
    __tablename__ = 'classuser'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    category_id = Column(INTEGER, nullable = False)
    user_id = Column(INTEGER, nullable = False)
    msg = Column(VARCHAR(255), default = '')
    is_top = Column(TINYINT, nullable = False, default = 0)
    editor_id = Column(INTEGER, nullable = False)
    review = Column(TINYINT, nullable = False, default = 0)
    create_ts = Column(TIMESTAMP, nullable = False)
    last_update_ts = Column(TIMESTAMP)
    user_desc = Column(VARCHAR(255), default = '')

    def __init__(self, category_id, user_id, msg, is_top, editor_id, review, create_ts, last_update_ts, user_desc):
        self.category_id = category_id
        self.user_id = user_id
        self.msg = msg
        self.is_top = is_top
        self.editor_id = editor_id
        self.review = review
        self.create_ts = create_ts
        self.last_update_ts = last_update_ts
        self.user_desc = user_desc

    def get_bind_user(self):
        return get_user_by_id(self.user_id)

    def get_component_user_id(self):
        return str(self.user_id)

    def get_component_user_avatar(self):
        usr = self.get_bind_user()
        if not usr: return ''
        else: return usr.get_component_user_avatar()

    def get_component_user_name(self):
        usr = self.get_bind_user()
        if not usr: return ''
        else: return usr.get_component_user_name()

    def get_component_category(self):
        return get_forum_name_by_cat_id(self.category_id)

    def get_component_user_description(self):
        return self.user_desc

    def to_ui_action(self):
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'user'
        action['id'] = self.get_component_user_id()
        return action

    def to_lite_ui_action(self):
        return self.to_ui_action()

@timer
@deco_cache(prefix = 'tangzhu_ids', recycle = TEN_MINUTES)
def get_tangzhu_ids(category_id, use_cache = True):
    DBSession = dbsession_generator()
    ids = DBSession.query(BanWuTangZhu.id).filter(BanWuTangZhu.review ==
            1).filter(BanWuTangZhu.category_id == category_id).order_by(BanWuTangZhu.id).all()
    ids = [id[0] for id in ids]
    DBSession.close()
    return ids

@timer
@deco_cache(prefix = 'tangzhu', recycle = TEN_MINUTES)
def get_tangzhu_by_id(tangzhu_id, use_cache = True):
    DBSession = dbsession_generator()
    tangzhu = DBSession.query(BanWuTangZhu).filter(BanWuTangZhu.id == tangzhu_id).first()
    DBSession.close()
    return tangzhu

@timer
@deco_cache(prefix = 'user_is_tangzhu', recycle = DAY)
def user_is_tangzhu(user_id):
    res = 0
    DBSession = dbsession_generator()
    usr = DBSession.query(BanWuTangZhu.id).filter(BanWuTangZhu.user_id == int(user_id)).filter(BanWuTangZhu.review == 1).first()
    if usr: res = 1
    DBSession.close()
    return res

