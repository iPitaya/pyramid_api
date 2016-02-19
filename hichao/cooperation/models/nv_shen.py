# -*- coding:utf-8 -*-
from sqlalchemy import (
        func,
        Column,
        INTEGER,
        VARCHAR,
        TIMESTAMP,
        )
from hichao.cooperation.models.db import (
        dbsession_generator,
        Base,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.base.models.base_component import BaseComponent
from hichao.util.date_util import MINUTE
from hichao.util.image_url import build_cooperation_image_url
from hichao.topic.models.topic import get_topic_by_id
from hichao.star.models.star import get_star_by_star_id
from icehole_client.files_client import get_filename
from hichao.util.statsd_client import timeit
from hichao.forum.models.thread import get_thread_by_id


class NvShenEntry(Base, BaseComponent):
    __tablename__ = 'event_show'
    id = Column(INTEGER, primary_key = True)
    type = Column(VARCHAR(128))
    type_id = Column(INTEGER)
    link = Column(VARCHAR(2048))
    img_url = Column(VARCHAR(1024))
    height = Column(INTEGER)
    width = Column(INTEGER)
    review = Column(TINYINT)
    ts = Column(TIMESTAMP)

    def get_component_width(self):
        return str(self.width)

    def get_component_height(self):
        return str(self.height)

    def get_component_id(self):
        return str(self.type_id)

    def get_component_pic_url(self):
        return build_cooperation_image_url(get_filename('backend_images', self.img_url))

    def to_ui_action(self):
        action = {}
        if self.type == 'topic':
            topic = get_topic_by_id(self.type_id)
            action = topic.to_ui_action()
        elif self.type == 'thread':
            thread = get_thread_by_id(self.type_id)
            action = thread.to_lite_ui_action()
        elif self.type == 'star':
            star = get_star_by_star_id(self.type_id)
            action = star.to_lite_ui_action()
        elif self.type == 'webview':
            action['actionType'] = 'webview'
            action['titleStyle'] = {'text':'链接详情', 'fontColor':'255,255,255,255', 'picUrl':'http://img1.hichao.com/images/images/20131024/40b08de1-cd5c-466e-a4bf-8c236c90475c.png'}
            action['means'] = 'push'
            action['webUrl'] = self.link
        elif self.type == 'tuanlist':
            action['type'] = 'item'
            action['actionType'] = 'jump'
            action['child'] = 'tuanlist'
        elif self.type == 'worthylist':
            action['type'] = 'item'
            action['actionType'] = 'jump'
            action['child'] = 'worthylist'
        elif self.type == 'threadlist':
            action['type'] = 'thread'
            action['actionType'] = 'jump'
            action['id'] = self.get_component_id()
        elif self.type == 'topiclist':
            action['type'] = 'thread'
            action['actionType'] = 'jump'
            action['child'] = 'topiclist'
        return action

@timeit('hichao_backend.m_coop_nvshen')
def get_nv_shen_entry():
    DBSession = dbsession_generator()
    nv_shen = DBSession.query(NvShenEntry).filter(NvShenEntry.review == 1).order_by(NvShenEntry.id.desc()).first()
    DBSession.close()
    return nv_shen

