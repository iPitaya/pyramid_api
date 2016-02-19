# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        BIGINT,
        TEXT,
        func,
        )
from hichao.drop.models.db import (
        rdbsession_generator,
        Base,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.base.models.base_component import BaseComponent
from hichao.util.image_url import build_drop_image_url
from hichao.star.models.star import get_star_by_star_id
from hichao.topic.models.topic import get_topic_by_id
from hichao.forum.models.thread import get_thread_by_id
from hichao.util.statsd_client import timeit
from hichao.util.cms_action_builder import build_action
from icehole_client.files_client import get_filename as get_img_file

method_dict = {
    'topic':get_topic_by_id,
    'star':get_star_by_star_id,
    'thread':get_thread_by_id,
    }

class Drop(Base, BaseComponent):
    __tablename__ = 'droplist'
    _id = Column('id', INTEGER, autoincrement = True, primary_key = True)
    _type = Column('type', VARCHAR(64), nullable = False)
    type_id = Column(INTEGER, nullable = True)
    editor_id = Column(INTEGER, nullable = True)
    url = Column(VARCHAR(512), nullable = False)
    publish_date = Column(BIGINT, nullable = False)
    _object = Column('object', TEXT, nullable = True)
    height = Column(INTEGER, nullable = False, default = 150)
    width = Column(INTEGER, nullable = False, default = 100)
    title = Column(VARCHAR(255), nullable = False, default = '')
    review = Column(TINYINT, nullable = False, default = 0)

    def __init__(self, _id, _type, type_id, editor_id, url, publish_date, _object, height, width, title = '', review = 0):
        self._id = _id
        self._type = _type
        self.type_id = type_id
        self.editor_id = editor_id
        self.url = url
        self.publish_date = publish_date
        self._object = _object
        self.height = height
        self.width = width
        self.title = title
        self.review = review

    def get_component_publish_date(self):
        return self.publish_date

    def get_component_pic_url(self):
        str_url = self.url.replace('/images/images/', '')
        if not 'group' in str_url:
            str_url = get_img_file('navigate_images',str_url)
        return build_drop_image_url(str_url)

    def get_component_height(self):
        return str(self.height)

    def get_component_width(self):
        return str(self.width)

    def get_component_type(self):
        return self._type

    def get_component_type_id(self):
        return str(self._object) if self._object else str(self.type_id)

    def to_ui_action(self):
        if self._type in method_dict.keys():
            method = method_dict[self._type]
            obj = method(self.get_component_type_id())
            if obj:
                if self._type == 'thread':
                    return obj.to_lite_ui_action()
                return obj.to_ui_action()
            else: return {}
        else:
            return build_action(self.get_component_type(), self.get_component_type_id())

@timeit('hichao_backend.m_drop')
def get_drop_by_id(_id):
    DBSession = rdbsession_generator()
    drop = DBSession.query(Drop).filter(Drop._id == _id).first()
    DBSession.close()
    return drop

