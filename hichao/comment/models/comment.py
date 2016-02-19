# -*- coding: utf-8 -*-
from hichao.util.statsd_client import timeit
from sqlalchemy import (
        Column,
        Integer,
        VARCHAR,
        BIGINT,
        func,
        )
from hichao.comment.models.db import (
        dbsession_generator,
        rdbsession_generator,
        Base,
        )
from hichao.base.lib.redis import redis, redis_key
from hichao.base.models.base_component import BaseComponent
from hichao.user.models.user import get_user_by_id
from hichao.util.image_url import build_user_avatar_url
from hichao.util.date_util import (
        get_date_attr,
        format_digital,
        )
from hichao.util.content_util import (
        rebuild_content,
        rebuild_content_by_split_item,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import (
        FIVE_MINUTES,
        TEN_MINUTES,
        MINUTE,
        DAY,
        )
from hichao.base.config import (
        MYSQL_MAX_INT,
        COMMENT_NUM_PER_PAGE,
        COMMENT_TYPE_STAR,
        COMMENT_TYPE_TOPIC,
        COMMENT_TYPE_THREAD,
        COMMENT_TYPE_THEME,
        COMMENT_TYPE_NEWS,
        )
from hichao.forum.models.thread import get_thread_by_id
from hichao.star.models.star import get_star_by_star_id
from hichao.comment import COMMENT_STATUS, FLOOR
from hichao.comment.models.sub_thread import SubThread
from hc.utils.ip import ip2long
from random import randint
import datetime
import transaction

timer = timeit('hichao_backend.m_comment')
timer_mysql = timeit('hichao_backend.m_comment.mysql')

class ItemFakeUser():
    def get_bind_user_id(self):
        return 0

@timer
def get_item_fake_user(*ars, **kw):
    return ItemFakeUser()

get_item_method_dict = {
        COMMENT_TYPE_STAR:get_star_by_star_id,
        COMMENT_TYPE_TOPIC:get_item_fake_user,
        COMMENT_TYPE_THREAD:get_item_fake_user,
        COMMENT_TYPE_THEME:get_item_fake_user,
        COMMENT_TYPE_NEWS:get_item_fake_user,
        }

class Comment(BaseComponent):
    id = Column(Integer, primary_key=True, autoincrement = True)
    item_id = Column(Integer)
    from_uid = Column(Integer)
    to_uid = Column(Integer)
    comment_id = Column(Integer)
    content = Column(VARCHAR(256))
    floor = Column(Integer)
    review = Column(Integer)
    ts = Column(BIGINT)
    ip = Column(Integer)
    platform =  Column(Integer)

    def __init__(self, item_id, from_uid, to_uid, comment_id, content, floor, review, ip = 0, platform = 0):
        self.item_id = item_id
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.comment_id = comment_id
        self.content = content
        self.floor = floor
        self.review = review
        self.ip = ip
        self.platform = platform
        self.ts = datetime.datetime.now()

    def get_component_id(self):
        return str(self.id)

    def get_comment_user(self):
        return get_user_by_id(self.from_uid)

    def get_bind_user(self):
        return self.get_comment_user()

    def get_component_user_avatar(self):
        user = self.get_comment_user()
        if not user:
            return ''
        else:
            return user.get_component_user_avatar()

    def get_component_user_name(self):
        user = self.get_comment_user()
        if not user:
            return ''
        else:
            return user.get_component_user_name()

    def get_component_user_id(self):
        return str(self.from_uid)

    def get_status(self):
        return self.review

    def get_component_content(self):
        content = COMMENT_STATUS.MSG.get(self.get_status(), '')
        if not content:
            if self.comment_id > 0:
                replied_comment = self.get_bind_comment()
                content = u"回复 {0}# {1}：{2}".format(replied_comment.get_component_floor(),
                    replied_comment.get_component_user_name(), self.content)
            else:
                content = self.content
        return content

    def get_component_description(self):
        if len(self.get_content()) < 20: res = self.get_content()
        else: res = self.get_content()[:randint(30,35)] + '...'
        return res

    def get_component_publish_date(self):
        #return '{0}-{1} {2}:{3}'.format(self.ts.month, self.ts.day, self.ts.hour, self.ts.minute)
        return '%02d-%02d %02d:%02d' % (self.ts.month, self.ts.day, self.ts.hour, self.ts.minute)

    def get_component_origin_publish_date(self):
        return self.get_component_publish_date()

    #def get_bind_comment(self):
    #    return get_comment_by_id(self.comment_id)

    def get_component_floor(self):
        floor = FLOOR.get(self.floor, '')
        if not floor:
            floor = '{0}楼'.format(self.floor)
        return floor

    def get_content(self):
        content = COMMENT_STATUS.MSG.get(self.get_status(), '')
        if not content:
            content = self.content
        return content

    def get_role_icons(self):
        role_icons = []
        #if user_is_staruser(self.from_uid):
        #    role_icons.append(ROLE_THREAD_STARUSER_ICON)
        #if user_is_admin(self.from_uid):
        #    role_icons.append(ROLE_THREAD_ADMIN_ICON)
        return role_icons

    def get_component_detail_imgs(self):
        return []

    def get_component_user_action(self):
        user = self.get_bind_user()
        if not user: return {}
        return user.to_lite_ui_action()

    def get_component_reply(self):
        com = {}
        replied_comment = self.get_bind_comment()
        if replied_comment:
            com['userName'] = replied_comment.get_component_user_name()
            com['publishDate'] = replied_comment.get_component_publish_date()
            com['floor'] = replied_comment.get_component_floor()
            com['description'] = replied_comment.get_component_description()
        return com

    def get_component_content_with_sku(self):
        _split_items = getattr(self, 'split_items', 0)
        if _split_items:
            return rebuild_content_by_split_item(self.get_content(), self.from_uid, support_embed = 1)
        else:
            return rebuild_content(self.get_content(), self.from_uid, support_embed = 1)

    def to_ui_action(self):
        action = {}
        lite_action = getattr(self, 'lite_user_action', 0)
        if lite_action:
            action['actionType'] = 'detail'
            action['type'] = 'user'
            action['id'] = self.get_component_user_id()
        else:
            action['actionType'] = 'space'
            action['userId'] = self.get_component_user_id()
            action['userName'] = self.get_component_user_name()
            action['userAvatar'] = self.get_component_user_avatar()
        return action

    def to_rtf_content(self):
        content = COMMENT_STATUS.MSG.get(self.get_status(), '')
        if content:
            return [{'component':{'text':content, 'color':'136,136,136,255',
            'componentType':'msgText',}},]
        content = []
        if self.comment_id > 0:
            replied_comment = self.get_bind_comment()
            con_reply = {'component':{'text':u'回复', 'color':'136,136,136,255', 'componentType':'msgText',}}
            con_user = {'component':{'text':u' #{0} "{1}"：'.format(replied_comment.get_component_floor(),
                replied_comment.get_component_user_name()),'color':'255,87,154,255', 'componentType':'msgText'},}
            content.append(con_reply)
            content.append(con_user)
        con_list = rebuild_content(self.content)
        content.extend(con_list)
        return content

class TopicComment(Comment, Base):
    __tablename__ = 'topic_comment'
    item_id = Column('topic_id', Integer)

    def get_bind_comment(self):
        return get_comment_by_id(COMMENT_TYPE_TOPIC, self.comment_id)

class StarComment(Comment, Base):
    __tablename__ = 'star_comment'
    item_id = Column('star_id', Integer)

    def get_bind_comment(self):
        return get_comment_by_id(COMMENT_TYPE_STAR, self.comment_id)

class ThemeComment(Comment, Base):
    __tablename__ = 'theme_comment'
    item_id = Column('theme_id', Integer)

    def get_bind_comment(self):
        return get_comment_by_id(COMMENT_TYPE_THEME, self.comment_id)

#class ThreadComment(Comment, Base):
#    __tablename__ = 'thread_comment'
#    item_id = Column('thread_id', Integer)
#
#    def get_bind_comment(self):
#        return get_comment_by_id(COMMENT_TYPE_THREAD, self.comment_id)

@timer
def get_comment_ids(_type, item_id, last_id, limit, asc):
    cls = get_cls_by_comment_type(_type)
    RDBSession = rdbsession_generator()
    _list = RDBSession.query(cls.id).filter(cls.item_id == item_id).filter(cls.review == 1)
    if asc == 1:
        _list = _list.filter(cls.id >= last_id).order_by(cls.id).limit(limit).all()
    else:
        _list = _list.filter(cls.id <= last_id).order_by(cls.id.desc()).limit(limit).all()
    RDBSession.close()
    _list = [id[0] for id in _list]
    return _list

@timer
def add_comment(_type, item_id, from_uid, comment_id, content, review = 1, ip = '',platform= 0 ):
    cls = get_cls_by_comment_type(_type)
    last_floor = get_comment_count(_type, item_id) + 1
    to_uid = 0
    if comment_id > 0:
        to_uid = get_comment_by_id(_type, comment_id).get_component_user_id()
    else:
        method = get_item_method_dict[_type]
        to_uid = int(method(item_id).get_bind_user_id())
    if not ip: ip = 0
    else: ip = ip2long(ip)
    comment = cls(item_id, from_uid, to_uid, comment_id, content, last_floor, review, ip, platform)
    try:
        DBSession = dbsession_generator()
        DBSession.add(comment)
        DBSession.flush()
        curr_id = comment.id
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        return 0
    finally:
        DBSession.close()
        get_comment_count(_type, item_id, use_cache = False)
    return curr_id

@timer
@deco_cache(prefix = 'comment', recycle = FIVE_MINUTES)
@timer_mysql
def get_comment_by_id(_type, item_id, use_cache = True):
    cls = get_cls_by_comment_type(_type)
    RDBSession = rdbsession_generator()
    comment = RDBSession.query(cls).filter(cls.id == item_id).first()
    RDBSession.close()
    return comment

@timer
@deco_cache(prefix = 'comment_count', recycle = TEN_MINUTES)
@timer_mysql
def get_comment_count(_type, item_id, use_cache = True):
    if _type == COMMENT_TYPE_STAR: return 0
    cls = get_cls_by_comment_type(_type)
    RDBSession = rdbsession_generator()
    count = RDBSession.query(func.count(cls.id)).filter(cls.item_id ==
            item_id).first()[0]
    RDBSession.close()
    return count

@timer
@deco_cache(prefix = 'comment_count_for_thread', recycle = FIVE_MINUTES)
@timer_mysql
def get_comment_count_for_thread(_type, item_id, use_cache = True):
    if _type == COMMENT_TYPE_STAR: return 0
    cls = get_cls_by_comment_type(_type)
    RDBSession = rdbsession_generator()
    count = RDBSession.query(func.count(cls.id)).filter(cls.item_id ==
            item_id).filter(cls.review==1).first()[0]
    RDBSession.close()
    return count


@timer
def get_cls_by_comment_type(_type):
    if _type == COMMENT_TYPE_STAR:
        return StarComment
    elif _type == COMMENT_TYPE_TOPIC:
        return TopicComment
    elif _type == COMMENT_TYPE_THREAD:
        return SubThread
    elif _type == COMMENT_TYPE_THEME:
        return ThemeComment
    elif _type == COMMENT_TYPE_NEWS:
        return TopicComment

@timer
def delete_comment(_type, user_id, comment_id):
    comment = get_comment_by_id(_type, comment_id)
    item_id = comment.item_id
    if str(user_id) == comment.get_component_user_id():
        try:
            cls = get_cls_by_comment_type(_type)
            DBSession = dbsession_generator()
            DBSession.query(cls).filter(cls.id == comment_id).update({cls.review:0,})
            transaction.commit()
        except Exception, ex:
            print Exception, ex
            transaction.abort()
            return 0
        finally:
            DBSession.close()
        return 1
    return 0

