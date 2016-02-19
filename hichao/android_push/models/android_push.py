# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        func,
        )
from hichao.android_push.models.db import (
        dbsession_generator,
        Base,
        )
from hichao.base.models.base_component import BaseComponent
from hichao.cache.cache import deco_cache
from hichao.util.date_util import (
        FIVE_MINUTES,
        HOUR,
        DAY,
        )
from hichao.topic.models.topic import get_topic_by_id
from hichao.forum.models.thread import get_thread_by_id
from hichao.util.statsd_client import timeit
import time
import datetime
import json

timer = timeit('hichao_backend.m_android_push')

class AndroidPush(Base, BaseComponent):
    __tablename__ = 'android_push'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    ticker = Column(VARCHAR(64))
    title = Column(VARCHAR(64))
    content = Column(VARCHAR(1024))
    review = Column(INTEGER)
    publish_date = Column(VARCHAR(20))
    _type = Column('type', VARCHAR(64), nullable = True)
    type_id = Column(INTEGER, nullable = True)

    def __init__(self, ticker = '', title = '', content = '', review = 0, publish_date = '', _type = '', type_id = 0):
        self.ticker = ticker
        self.title = title
        self.content = content
        self.review = review
        if not publish_date: publish_date = time.time()
        self.publish_date = publish_date
        self._type = _type
        self.type_id = type_id

    def __repr__(self):
        return 'android_push_' + str(self.id)

    def get_ticker(self):
        return self.ticker

    def get_title(self):
        return self.title

    def get_content(self):
        return self.content

    def get_version(self):
        return str(self.id)

    def to_ui_action(self):
        method = None
        if self._type == 'topic': method = get_topic_by_id
        elif self._type == 'thread': method = get_thread_by_id
        elif self._type == 'tuanlist': return {'actionType':'jump', 'type':'item', 'child':'tuanlist'}
        elif self._type == 'topiclist': return {'actionType':'jump', 'type':'thread', 'child':'topiclist'}
        elif self._type == 'threadlist': return {'actionType':'jump', 'type':'thread', 'child':''}
        if not method:
            return {}
        else:
            obj = method(self.type_id)
            if obj:
                return obj.to_ui_action()
            return {}

@timer
@deco_cache(prefix = 'android_push', recycle = HOUR)
def get_last_android_push(use_cache = True):
    now = time.localtime()
    #if now.tm_wday != 1 and now.tm_wday != 3 and now.tm_wday != 5:
    #    return None
    if now.tm_hour <= 12:
        hour = 14
    else:
        hour = 23
    publish_date = int(time.mktime(datetime.datetime(now.tm_year, now.tm_mon, now.tm_mday, hour, 0, 0).timetuple()))
    DBSession = dbsession_generator()
    android_push = DBSession.query(AndroidPush).filter(AndroidPush.publish_date ==
            publish_date).filter(AndroidPush.review == 1).first()
    DBSession.close()
    return android_push

@timer
@deco_cache(prefix = 'android_push_last_id', recycle = FIVE_MINUTES)
def get_last_android_push_id(use_cache = True):
    push = get_last_android_push(use_cache = True)
    if push:
        return push.id
    else:
        return -1

