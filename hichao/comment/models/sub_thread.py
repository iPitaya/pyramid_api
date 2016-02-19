# -*- coding: utf-8 -*-

from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
    BIGINT,
    func,
    TIMESTAMP,
)
from sqlalchemy.dialects.mysql import (
    TINYINT,
    INTEGER,
)
from hichao.comment.models.db import (
    dbsession_generator,
    rdbsession_generator,
    Base,
    engine,
)
from hichao.base.models.base_component import BaseComponent
from hichao.user.models.user import get_user_by_id
from hichao.util.date_util import (
    get_date_attr,
    format_digital,
    get_rough_time,
)
from hichao.util.content_util import (
    rebuild_content,
    rebuild_content_by_split_item,
)
from hichao.cache.cache import (
    deco_cache,
    deco_cache_m,
)
from hichao.util.date_util import (
    MINUTE,
    DAY,
)
from hichao.util.user_util import get_user_level, user_is_custom
from hichao.base.config import (
    MYSQL_MAX_INT,
    COMMENT_TYPE_THREAD,
    COMMENT_NUM_PER_PAGE,
    ROLE_THREAD_STARUSER_ICON,
    ROLE_THREAD_ADMIN_ICON,
    ROLE_THREAD_CUSTOM_ICON,
)
from hichao.forum.models.thread import get_thread_by_id
from hichao.forum.models.star_user import user_is_staruser, get_staruser_by_user_id
from hichao.comment import COMMENT_STATUS, FLOOR
from hichao.comment.models.sub_thread_img import get_img_ids_by_id
from hichao.upload.models.image import get_image_by_id
from hichao.util.cps_util import get_cps_key, cps_title_styles_dict
from hichao.util.statsd_client import timeit
from hichao.event.models.nv_shen.user_new import is_nv_shen_user
from random import randint
import time

timer = timeit('hichao_backend.m_comment_subthread')


class SubThread(Base, BaseComponent):
    __tablename__ = 'thread_comment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column('thread_id', Integer)
    content = Column(VARCHAR(5000))
    from_uid = Column(Integer)
    to_uid = Column(Integer)
    comment_id = Column(Integer)
    floor = Column(Integer)
    review = Column(TINYINT)
    ts = Column(TIMESTAMP)
    ip = Column(Integer)
    has_img = Column(TINYINT)
    category_id = Column(Integer)
    platform = Column(Integer)
    skus = Column(VARCHAR(255))
    repost = Column(TINYINT, nullable=False, default=0)

    def __init__(self, thread_id, content, from_uid, to_uid, comment_id, floor, ts, ip, has_img, category_id, review=1, platform=0, skus='', repost=0):
        self.item_id = thread_id
        self.content = content
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.comment_id = comment_id
        self.floor = floor
        self.ts = ts
        self.ip = ip
        self.has_img = has_img
        self.category_id = category_id
        self.review = review
        self.platform = platform
        self.skus = skus
        self.repost = repost

    def get_bind_user(self):
        return get_user_by_id(self.from_uid)

    def get_to_user(self):
        return get_user_by_id(self.to_uid)

    def get_bind_user_id(self):
        return str(self.from_uid)

    def get_bind_img_ids(self):
        ids = []
        if self.has_img:
            ids = get_img_ids_by_id(self.id)
        return ids

    def get_bind_imgs(self):
        ids = self.get_bind_img_ids()
        imgs = []
        for id in ids:
            img = get_image_by_id(id)
            imgs.append(img)
        return imgs

    def get_main_thread(self):
        return get_thread_by_id(self.item_id)

    def is_visible(self):
        visible = getattr(self, 'visible', -1)
        if visible == -1:
            thread = self.get_main_thread()
            if not thread:
                return 1
            visible = thread.is_visible()
        return visible

    def get_component_imgs(self):
        re = []
        if self.review != 1:
            return re
        if not self.is_visible():
            return re
        imgs = self.get_bind_imgs()
        support_webp = getattr(self, 'support_webp', 0)
        for img in imgs:
            if img:
                img.support_webp = support_webp
                ui = {}
                com = {}
                ui['width'] = img.get_component_width()
                ui['height'] = img.get_component_height()
                com['componentType'] = 'cell'
                com['picUrl'] = img.get_component_pic_detail_url()
                act = {}
                act['actionType'] = 'showBigPic'
                act['picUrl'] = com['picUrl']
                act['noSaveButton'] = '0'
                com['action'] = act
                ui['component'] = com
                re.append(ui)
        return re

    def get_self_imgs(self):
        imgs = self.get_bind_imgs()
        re = []
        support_webp = getattr(self, 'support_webp', 0)
        for img in imgs:
            if img:
                img.support_webp = support_webp
                re.append(img.get_component_pic_detail_url())
        return re

    def get_component_description(self):
        if len(self.get_content()) < 20:
            res = self.get_content()
        else:
            res = self.get_content()[:randint(30, 35)] + '...'
        return res

    def get_component_detail_imgs(self):
        return self.get_component_imgs()

    def get_component_user_name(self):
        user = self.get_bind_user()
        if not user:
            return ''
        else:
            return user.get_component_user_name()

    def get_component_user_type_name(self):
        staruser = get_staruser_by_user_id(self.from_uid)
        if staruser:
            user_type = staruser.get_staruser_type()
        else:
            return ''
        if user_type:
            return user_type['userTypeName']
        else:
            return ''

    def get_component_user_avatar(self):
        user = self.get_bind_user()
        if not user:
            return ''
        else:
            return user.get_component_user_avatar()

    def get_component_user_id(self):
        return self.get_bind_user_id()

    def get_component_user_level(self):
        return str(get_user_level(self.from_uid))

    def get_component_publish_date(self):
        ts = time.mktime(self.ts.timetuple())
        return get_rough_time(ts)

    def get_component_origin_publish_date(self):
        return self.get_component_publish_date()

    def get_component_floor(self):
        floor = FLOOR.get(self.floor, '')
        if not floor:
            floor = '{0}楼'.format(self.floor)
        return floor

    def get_component_id(self):
        return str(self.id)

    def get_status(self):
        return self.review

    def get_role_icons(self):
        role_icons = []
        if user_is_staruser(self.from_uid) and user_is_custom(self.from_uid):
            role_icons.append(ROLE_THREAD_CUSTOM_ICON)
        else:
            if user_is_staruser(self.from_uid):
                role_icons.append(ROLE_THREAD_STARUSER_ICON)
            elif user_is_custom(self.from_uid):
                role_icons.append(ROLE_THREAD_CUSTOM_ICON)
        # if user_is_admin(self.from_uid):
        #    role_icons.append(ROLE_THREAD_ADMIN_ICON)
        return role_icons

    def get_content(self):
        content = COMMENT_STATUS.MSG.get(self.get_status(), '')
        if not content:
            if not self.is_visible():
                content = u'该楼层暂时被隐藏。'
            else:
                content = self.content
        return content

    def get_component_content(self):
        return rebuild_content(self.get_content(), self.from_uid, support_embed=0)

    def get_component_content_with_sku(self):
        _split_items = getattr(self, 'split_items', 0)
        if _split_items:
            inner_redirect = getattr(self, 'inner_redirect', 0)
            return rebuild_content_by_split_item(self.get_content(), self.from_uid, support_embed=1, inner_redirect=inner_redirect, support_brandstore=self.support_brandstore)
        else:
            return rebuild_content(self.get_content(), self.from_uid, support_embed=1)

    def get_bind_comment(self):
        return get_subthread_by_id(self.comment_id)

    def get_component_reply(self):
        com = {}
        replied_comment = self.get_bind_comment()
        if replied_comment:
            com['userName'] = replied_comment.get_component_user_name()
            com['publishDate'] = replied_comment.get_component_publish_date()
            com['floor'] = replied_comment.get_component_floor()
            com['description'] = replied_comment.get_component_description()
        return com

    def to_rtf_content(self):
        if self.review != 1:
            return [{'component': {'text': self.get_content(), 'color': '136,136,136,255',
                                   'componentType': 'msgText', }}, ]
        content = []
        if self.comment_id > 0:
            replied_comment = self.get_bind_comment()
            con_reply = {'component': {'text': u'回复', 'color': '136,136,136,255', 'componentType': 'msgText', }}
            con_user = {'component': {'text': u' #{0} "{1}"：'.format(replied_comment.get_component_floor(),
                                                                     replied_comment.get_component_user_name()), 'color': '255,87,154,255', 'componentType': 'msgText'}, }
            content.append(con_reply)
            content.append(con_user)
        con_list = rebuild_content(self.get_content(), user_id=self.from_uid, support_embed=0)
        content_with_img = getattr(self, 'content_with_img', 0)
        if content_with_img:
            imgs = self.get_bind_imgs()
            #title_style = cps_title_styles_dict[get_cps_key('', '')]
            for img in imgs:
                img_comp = {
                    'component': {
                        'text': u' 点击查看图片 ',
                        'color': '255,87,154,255',
                        'componentType': 'msgText',
                        'action': {
                            'actionType': 'webview',
                            'webUrl': img.get_component_pic_detail_url(),
                            'means': 'push',
                            #'titleStyle':title_style,
                        },
                    },
                }
                con_list.append(img_comp)
        content.extend(con_list)
        return content

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

    def to_sub_detail(self):
        ui = {}
        com = {}
        com['componentType'] = 'subSubjectCell'
        com['description'] = self.get_component_content()
        com['imgs'] = self.get_component_detail_imgs()
        com['userName'] = self.get_component_user_name()
        com['userPicUrl'] = self.get_component_user_avatar()
        com['userLevel'] = self.get_component_user_level()
        com['dateTime'] = self.get_component_publish_date()
        usr = self.get_bind_user()
        if usr:
            action = usr.to_ui_action()
        else:
            action = {}
        com['action'] = action
        ui['component'] = com
        return ui

    def get_component_user_action(self):
        user = self.get_bind_user()
        if not user:
            return {}
        action = user.to_lite_ui_action()
        action['userId'] = user.get_component_id()
        action['userName'] = user.get_component_user_name()
        action['userAvatar'] = user.get_component_user_avatar()
        return action


@timer
def add_subthread(thread_id, content, from_uid, to_uid, comment_id, ts, ip, has_img, floor, category_id, platform=0, skus='', repost=0):
    review = 1
    sub_thread = (thread_id, content, from_uid, to_uid, comment_id, floor, ts, ip, has_img, category_id, review, platform, skus, repost)
    try:
        conn = engine.connect()
        res = conn.execute("insert into thread_comment (thread_id, content, from_uid, to_uid, comment_id, floor, ts,\
        ip, has_img, category_id, review, platform, skus, repost) values (%s, %s, %s, %s, %s, %s, %s,inet_aton(%s), %s, %s, %s, %s, %s, %s);", sub_thread)
        last_id = res.lastrowid
    except Exception, ex:
        print Exception, ex
        return 0
    finally:
        conn.close()
    return last_id


@timer
@deco_cache(prefix='sub_thread', recycle=MINUTE)
def get_subthread_by_id(subthread_id, use_cache=True):
    DBSession = dbsession_generator()
    sub_thread = DBSession.query(SubThread).filter(SubThread.id == int(subthread_id)).first()
    DBSession.close()
    return sub_thread


@timer
@deco_cache_m(prefix='sub_thread', recycle=MINUTE)
def get_subthreads_by_id(subthread_ids, use_cache=True):
    subthread_ids = [int(subthread_id) for subthread_id in subthread_ids]
    DBSession = rdbsession_generator()
    subthreads = DBSession.query(SubThread.id, SubThread).filter(SubThread.id.in_(subthread_ids)).all()
    subthreads = dict(subthreads)
    DBSession.close()
    return subthreads


@timer
@deco_cache(prefix='filter_sub_thread_ids', recycle=MINUTE)
def get_filter_subthread_ids(thread_id, offset, limit, user_id=0, only_img=0, asc=1, use_cache=True):
    DBSession = dbsession_generator()
    ids = DBSession.query(SubThread.id).filter(SubThread.item_id == thread_id).filter(SubThread.review == 1)
    if user_id:
        ids = ids.filter(SubThread.from_uid == int(user_id))
    if only_img:
        ids = ids.filter(SubThread.has_img == 1)
    if asc:
        ids = ids.order_by(SubThread.floor, SubThread.id).offset(offset).limit(limit).all()
    else:
        ids = ids.order_by(SubThread.floor.desc(), SubThread.id.desc()).offset(offset).limit(limit).all()
    ids = [id[0] for id in ids]
    DBSession.close()
    return ids


@timer
@deco_cache(prefix='subthread_ids', recycle=MINUTE)
def get_subthread_ids(thread_id, sfloor, bfloor, asc=1, use_cache=True):
    DBSession = dbsession_generator()
    ids = DBSession.query(SubThread.id).filter(SubThread.item_id == thread_id).filter(SubThread.review == 1).filter(SubThread.floor <=
                                                                                                                    bfloor).filter(SubThread.floor >= sfloor)
    if asc:
        ids = ids.order_by(SubThread.floor).all()
    else:
        ids = ids.order_by(SubThread.floor.desc()).all()
    ids = [id[0] for id in ids]
    DBSession.close()
    return ids


@timer
@deco_cache(prefix='subthread_ids_for_thread', recycle=MINUTE)
def get_subthread_ids_for_thread(thread_id, offset, limit, asc=1, use_cache=True):
    DBSession = dbsession_generator()
    ids_floors = DBSession.query(SubThread.id, SubThread.floor).filter(SubThread.item_id == thread_id).filter(SubThread.review == 1).offset(offset).limit(limit).all()
    if asc:
        ids = sorted(ids_floors, key=lambda ids_floors: ids_floors[1])
    else:
        ids = sorted(ids_floors, key=lambda ids_floors: ids_floors[1], reverse=True)
    ids = [id[0] for id in ids]
    DBSession.close()
    return ids


@timer
@deco_cache(prefix='latest_subids_for_thread', recycle=MINUTE)
def get_latest_subthread_ids_by_thread_id(thread_id, limit, use_cache=True):
    DBSession = dbsession_generator()
    ids = DBSession.query(SubThread.id).filter(SubThread.item_id == thread_id).filter(SubThread.review == 1).filter(SubThread.repost == 0).order_by(SubThread.id.desc()).limit(limit).all()
    if ids:
        ids = [id[0] for id in ids]
    DBSession.close()
    return ids


@timer
@deco_cache(prefix='forum_comment_count', recycle=MINUTE)
def get_forum_comment_count(forum_id, use_cache=True):
    DBSession = rdbsession_generator()
    count = DBSession.query(func.count(SubThread.id)).filter(SubThread.category_id == int(forum_id)).first()
    if count:
        count = count[0]
    else:
        count = 0
    DBSession.close()
    return count


@timer
@deco_cache(prefix='thread_comment_count_by_floor', recycle=MINUTE)
def get_forum_comment_count_by_floor(thread_id, floor, use_cache=True):
    DBSession = rdbsession_generator()
    count = DBSession.query(func.count(SubThread.id)).filter(SubThread.item_id == thread_id).filter(SubThread.review == 1).filter(SubThread.floor < floor).first()
    if count:
        count = count[0]
    else:
        count = 0
    DBSession.close()
    return count
