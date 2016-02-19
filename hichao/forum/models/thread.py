# -*- coding:utf-8 -*-
from hichao.util.statsd_client import statsd
from sqlalchemy import (
        Column,
        VARCHAR,
        TEXT,
        BIGINT,
        func,
        Float,
        DateTime,
        TIMESTAMP,
        or_,
        )
from sqlalchemy.dialects.mysql import (
        TINYINT,
        INTEGER,
        )
from hichao.forum.models.db import (
        Base,
        dbsession_generator,
        rdbsession_generator,
        threadlocal_dbsession_generator,
        engine,
        )
from hichao.user.models.user import get_user_by_id
from hichao.upload.models.image import get_image_by_id
from hichao.forum.models.thread_img import (
        get_img_ids_by_id,
        get_img_ids_by_thread_ids,
        )
from hichao.forum.models.uv import thread_uv_count
from hichao.forum.models.pv import thread_pv_count
from hichao.forum.models.forum import get_forum_name_by_cat_id
from hichao.forum.models.star_user import user_is_staruser
from hichao.util.image_url import build_user_avatar_url
from hichao.util.date_util import (
        DAY,
        HOUR,
        MINUTE,
        TEN_SECONDS,
        TEN_MINUTES,
        get_rough_time,
        )
from hichao.util.content_util import (
        rebuild_content,
        rebuild_content_by_split_item,
        )
from hichao.util.user_util import (
        get_user_level,
        user_is_admin,
        user_is_custom,
        )
from hichao.cache.cache import deco_cache
from hichao.base.config import (
        MYSQL_MAX_TIMESTAMP,
        FALL_PER_PAGE_NUM,
        TOP_ICON,
        FAVOR_ICON,
        HAS_IMG_ICON,
        DEFAULT_IMG,
        ROLE_THREAD_STARUSER_ICON,
        ROLE_THREAD_ADMIN_ICON,
        THREAD_OWNER_ICON,
        APP_LOGO,
        WEB_URL_DOMAIN,
        ROLE_THREAD_CUSTOM_ICON,
        )
from hichao.util.statsd_client import timeit
from hichao.event.models.nv_shen.user_new import is_nv_shen_user
from hichao.base.models.base_component import BaseComponent
from random import randint
import time
import transaction
import datetime
from hichao.collect.models.fake import collect_count_new

timer = timeit('hichao_backend.m_forum_thread')

class ThreadLocal(Base):
    __tablename__= "thread_local"
    id = Column(INTEGER,primary_key=True,autoincrement=True)
    thread_id=Column(INTEGER,nullable=False)
    lng=Column(Float,nullable=True)
    lat=Column(Float,nullable=True)
    ts=Column(DateTime,nullable=False)

    def __init__(self,thread_id,lng,lat):
        self.thread_id=thread_id
        self.lng=lng
        self.lat=lat

    def get_longitude(self):
        return str(self.lng)

    def get_latitude(self):
        return str(self.lat)

@timer
@deco_cache(prefix = 'threadlocal', recycle = HOUR)
def get_threadlocal_by_id(thread_id, use_cache = True):
    DBSession = threadlocal_dbsession_generator()
    threadlocal = DBSession.query(ThreadLocal).filter(ThreadLocal.thread_id == thread_id).first()
    DBSession.close()
    return threadlocal

class UIDMobile(Base):
    __tablename__="uid_mobile"
    id = Column(INTEGER,primary_key=True,autoincrement=True)
    uid=Column(INTEGER,nullable=False)
    mobile=Column(BIGINT,nullable=False)
    name=Column(VARCHAR(1024),nullable=False)
    addr=Column(VARCHAR(2048),nullable=False)
    review=Column(TINYINT,nullable=False)
    ts=Column(DateTime,nullable=False)

    def __init__(self,uid,mobile,name,addr):
        self.uid=uid
        self.mobile=mobile
        self.name=name
        self.addr=addr
        self.review=1

    def get_address(self):
        if self.mobile:
            return '(' + str(self.mobile) + ') ' + self.addr
        else:
            return self.addr

    def get_name(self):
        return self.name


@timer
@deco_cache(prefix = 'UID_Mobile', recycle = HOUR)
def get_uidmobile_by_uid(uid, use_cache = True):
    DBSession = threadlocal_dbsession_generator()
    uid_mobile = DBSession.query(UIDMobile).filter(UIDMobile.uid==uid).first()
    DBSession.close()
    return uid_mobile

class Thread(Base, BaseComponent):
    __tablename__ = "threads"
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    category_id = Column(TINYINT, nullable = False)
    user_id = Column(INTEGER, nullable = False)
    img_id = Column(INTEGER, nullable = False)
    content = Column(TEXT, nullable = False)
    ts = Column(BIGINT, nullable = False)
    review = Column(TINYINT)
    main_thread_id = Column(INTEGER, default = 0)
    title = Column(VARCHAR(256), default = '')
    update_ts = Column(BIGINT, nullable = False)
    ip = Column(INTEGER, nullable = False, default = 0)
    is_top = Column(TINYINT, nullable = False, default = 0)
    is_favor = Column(TINYINT, nullable = False, default = 0)
    is_forbidden = Column(TINYINT, nullable = False, default = 0)
    forbidden_end_time = Column(TIMESTAMP, nullable = True)
    is_display = Column(TINYINT, nullable = False, default = 1)
    has_img = Column(TINYINT, default = 1)
    edit_time = Column(TIMESTAMP)
    recommend = Column(INTEGER, nullable = False, default = 0)
    sku_num = Column(INTEGER, default = 0)
    platform =  Column(TINYINT, default = 0)
    img_lock = Column(TINYINT, nullable = False, default = 1)
    tags = Column(VARCHAR(255), nullable = False, default = '')
    skus = Column(VARCHAR(255), nullable = True)

    def __init__(self, user_id, img_id, content, category_id, review, main_thread_id = 0, title = '', has_img = 1,
            edit_time = '', recommend = 0, img_lock = 1, tags = '', skus = ''):
        self.category_id = category_id
        self.user_id = user_id
        self.img_id = img_id
        self.content = content
        self.review = review
        self.main_thread_id = main_thread_id
        self.title = title
        self.update_ts = datetime.datetime.now()
        self.has_img = has_img
        if not edit_time: edit_time = datetime.datetime.now()
        self.edit_time = edit_time
        self.recommend = recommend
        self.img_lock = img_lock
        self.tags = tags
        self.skus = skus

    def has_image(self):
        if not self.has_img:
            if self.img_id:
                return 1
        return self.has_img

    def img_locked(self):
        return self.img_lock

    def get_bind_user(self):
        return get_user_by_id(self.user_id)

    def get_bind_user_id(self):
        return str(self.user_id)

    def get_bind_img_ids(self):
        ids = get_img_ids_by_id(self.id)
        if not ids:
            if self.img_id: ids = [self.img_id, ]
            else: ids = []
        return ids

    def get_bind_image(self):
        img_ids = self.get_bind_img_ids()
        if img_ids:
            return get_image_by_id(self.get_bind_img_ids()[0])
        else:
            return None

    def get_bind_imgs(self):
        ids = self.get_bind_img_ids()
        imgs = []
        for id in ids:
            img = get_image_by_id(id)
            imgs.append(img)
        return imgs

    def get_bind_imgs_with_sub_threads(self):
        ids = self.get_bind_img_ids()
        #if len(ids) < 3:
        #    bind_threads = get_sub_threads_by_id(self.id)
        #    sub_thread_ids = [thread.id for thread in bind_threads]
        #    if sub_thread_ids:
        #        img_ids = get_img_ids_by_thread_ids(sub_thread_ids)
        #        ids.extend(img_ids)
        imgs = []
        for id in ids[:3]:
            img = get_image_by_id(id)
            imgs.append(img)
        return imgs

    def get_component_pic_url(self):
        return self.get_bind_image_url('detail')

    def get_component_imgs(self, tp, crop):
        if tp == 'fall':
            imgs = self.get_bind_imgs_with_sub_threads()
        else:
            imgs = self.get_bind_imgs()
        re = []
        support_webp = getattr(self, 'support_webp', 0)
        for img in imgs:
            if img:
                img.support_webp = support_webp
                if tp == 'fall':
                    re.append(img.get_component_pic_fall_url(crop))
                else:
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
        if not re and tp == 'fall':
            re.append(DEFAULT_IMG)
        return re

    def get_component_common_pic_url(self):
        return self.get_component_pic_fall_url()

    def get_self_imgs(self):
        imgs = self.get_bind_imgs()
        res = []
        for img in imgs:
            if img:
                img.support_webp = getattr(self, 'support_webp', 0)
                res.append(img.get_component_pic_detail_url())
        return res

    def get_component_icon(self):
        without_icon = getattr(self, 'without_icon', '')
        if without_icon:
            return []
        with_top_icon = getattr(self, 'with_top_icon', '')
        icons = []
        ft_icon = ''    # favor or top icon
        if self.is_favor: ft_icon = FAVOR_ICON
        if with_top_icon:
            if self.is_top: ft_icon = TOP_ICON
        if ft_icon:
            icons.append(ft_icon)
        #attr_icon = ''
        #if self.has_img: attr_icon = HAS_IMG_ICON
        #if attr_icon:
        #    icons.append(attr_icon)
        return icons

    def get_role_icons(self):
        role_icons = []
        role_icons.append(THREAD_OWNER_ICON)
        if user_is_staruser(self.user_id) and user_is_custom(self.user_id):
            role_icons.append(ROLE_THREAD_CUSTOM_ICON)
        else:
            if user_is_staruser(self.user_id):
                role_icons.append(ROLE_THREAD_STARUSER_ICON)
            elif user_is_custom(self.user_id):
                role_icons.append(ROLE_THREAD_CUSTOM_ICON)
            elif user_is_admin(self.user_id):
                role_icons.append(ROLE_THREAD_ADMIN_ICON)
        return role_icons

    def get_component_fall_imgs(self, crop = ''):
        return self.get_component_imgs('fall', crop)

    def get_component_detail_imgs(self, crop = ''):
        return self.get_component_imgs('detail', crop)

    def get_component_pic_fall_url(self, crop = False):
        return self.get_bind_image_url('fall', crop)

    def get_bind_image_url(self, _type, crop = False):
        img = self.get_bind_image()
        if not img:
            return ''
        else:
            img.support_webp = getattr(self, 'support_webp', 0)
            if _type == 'fall':
                return img.get_component_pic_fall_url(crop)
            else:
                return img.get_component_pic_detail_url()

    def get_component_title(self):
        return self.title and self.title or self.get_component_description()

    def get_component_id(self):
        return str(self.id)

    def get_component_user_avatar(self):
        user = self.get_bind_user()
        if not user:
            return ''
        else:
            return user.get_component_user_avatar()

    def get_component_user_name(self):
        user = self.get_bind_user()
        if not user:
            return ''
        else:
            return user.get_component_user_name()

    def get_component_user_level(self):
        return str(get_user_level(self.user_id))

    def get_component_reply(self):
        return {}

    def get_component_user_id(self):
        return str(self.user_id)

    def get_component_width(self):
        img = self.get_bind_image()
        if img:
            return img.get_component_width()
        else:
            return '100'

    def get_component_height(self):
        img = self.get_bind_image()
        if img:
            return img.get_component_height()
        else:
            return '100'

    def get_component_description(self):
        if len(self.content) < 20: res = self.content
        else: res = self.content[:randint(30,35)] + '...'
        return res.replace('\n', '')

    def get_component_publish_date(self):
        #return '%02d-%02d %02d:%02d' % (self.ts.month, self.ts.day, self.ts.hour, self.ts.minute)
        ts = time.mktime(self.update_ts.timetuple())
        return get_rough_time(ts)

    def get_component_origin_publish_date(self):
        ts = time.mktime(self.ts.timetuple())
        return get_rough_time(ts)

    def get_component_category(self):
        #return str(self.category_id)
        forum_name = get_forum_name_by_cat_id(self.category_id)
        if not forum_name: return ''
        return forum_name

    def forum_has_deleted(self):
        if not self.get_component_category(): return 1
        return 0

    def get_component_forum(self):
        if not get_forum_name_by_cat_id(self.category_id): return ''
        return '【' + get_forum_name_by_cat_id(self.category_id) + '】'

    def get_component_forum_id(self):
        return str(self.category_id)

    def get_component_content(self):
        return rebuild_content(self.content, self.user_id, support_embed = 0)
        #return {'component':{'componentType':'msgText', 'text':self.content, 'color':'136,136,136,255', 'action':{}}

    def get_component_content_with_sku(self):
        _split_items = getattr(self, 'split_items', 0)
        if _split_items:
            inner_redirect = getattr(self, 'inner_redirect', 0)
            return rebuild_content_by_split_item(self.content, self.user_id, support_embed = 1, inner_redirect = inner_redirect, support_brandstore = self.support_brandstore)
        else:
            return rebuild_content(self.content, self.user_id, support_embed = 1)

    def get_unixtime(self):
        return int(time.mktime(self.ts.timetuple()))

    def get_component_uv(self):
        return str(thread_uv_count(self.id))

    def get_component_pv(self):
        pv = thread_pv_count(self.id)
        if not pv: pv = 0
        cnt = int(pv) + int(collect_count_new(self.id,150,float(self.get_unixtime())))
        return str(cnt)

    def get_component_floor(self):
        return u'楼主'

    def get_component_forbid_comment(self):
        return str(self.is_set_forbidden())

    def get_component_sku_num(self):
        return str(self.sku_num)
    
    def get_share_image(self):
        obj={}
        action={}
        action['title']=self.get_component_title()
        action['shareType']='webpage'
        action['id']=self.get_component_id()
        action['description']=self.get_component_description()
        action['picUrl']=self.get_component_pic_url()
        if not action['picUrl']:
            action['picUrl'] = APP_LOGO
        action['detailUrl']='{0}/wap/thread/{1}'.format(WEB_URL_DOMAIN, self.get_component_id())
        obj['actionType']='share'
        obj['type']='webpage'
        obj['typeId']=self.get_component_id()
        obj['trackValue']='{0}_{1}'.format(obj['type'],obj['typeId'])
        obj['share']=action
        return obj

    def location_ui_action(self,threadlocal,uid_mobile):
        obj=[]
        com={}
        com['componentType']='msgText'
        com['color']='136,136,136,255'
        com['border']=''
        action={}
        action['actionType']='map'
        if uid_mobile:
            action['address']=uid_mobile.get_address()
            com['text']=uid_mobile.get_name()
            action['title']=uid_mobile.get_name()
        else:
            action['address']=''
            com['text']=''
            action['title']=''
        if threadlocal:
            action['longitude']=threadlocal.get_longitude()
            action['latitude']=threadlocal.get_latitude()
        else:
            action['longitude']=''
            action['latitude']=''
        com['action']=action
        obj.append({'component':com})
        return obj

    def to_ui_action(self, both_img = 0):
        more_img = getattr(self, 'more_img', '')
        action = {}
        action['actionType'] = 'subjectDetail'
        action['id'] = self.get_component_id()
        action['unixtime'] = self.get_unixtime()
        action['userName'] = self.get_component_user_name()
        action['userPicUrl'] = self.get_component_user_avatar()
        action['userId'] = self.get_component_user_id()
        action['userLevel'] = self.get_component_user_level()
        if not more_img:
            action['normalPicUrl'] = self.get_component_pic_url()
            action['width'] = self.get_component_width()
            action['height'] = self.get_component_height()
        else:
            action['imgs'] = self.get_component_detail_imgs()
        if both_img:
            action['normalPicUrl'] = self.get_component_pic_url()
            action['width'] = self.get_component_width()
            action['height'] = self.get_component_height()
            action['imgs'] = self.get_component_detail_imgs()
        #action['v'] = self.get_component_uv()
        action['v'] = self.get_component_pv()
        action['description'] = self.get_component_content()
        action['dateTime'] = self.get_component_publish_date()
        action['category'] = self.get_component_category()
        action['forum'] = self.get_component_forum()
        action['title'] = self.get_component_title()
        action['shareAction']=self.get_share_image()
        threadlocal =get_threadlocal_by_id(self.id) 
        if threadlocal:
            uid_mobile=get_uidmobile_by_uid(self.get_bind_user_id())
            action['location']=self.location_ui_action(threadlocal,uid_mobile)
        return action

    def is_deleted(self):
        return self.review == 0 and True or False

    def is_set_top(self):
        return self.is_top

    def is_set_favor(self):
        return self.is_favor

    def is_set_forbidden(self):
        return self.is_forbidden

    def is_visible(self):
        return self.is_display

    def get_tag_action(self):
        action = {}
        action['actionType'] = 'tag'
        action['type'] = 'forum'
        tag = self.get_component_category()
        if tag:
            action['tag'] = tag
            action['id'] = self.get_component_forum_id()
        else:
            action['tag'] = '美搭前沿'
            action['id'] = str(110)
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
        if usr: action = usr.to_ui_action()
        else: action = {}
        com['action'] = action
        ui['component'] = com
        return ui

    def to_lite_ui_action(self):
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'thread'
        action['id'] = self.get_component_id()
        action['unixtime'] = self.get_unixtime()
        return action

    def get_component_user_action(self):
        user = self.get_bind_user()
        if not user: return {}
        action = user.to_lite_ui_action()
        action['userId'] = user.get_component_id()
        action['userName'] = user.get_component_user_name()
        action['userAvatar'] = user.get_component_user_avatar()
        return action

@timer
def add_thread(user_id, img_id, content, category_id, ip, review = 1, thread_id = 0, title = '', has_img = 1, platform= 0, tags = '', skus = ''):
    edit_time = datetime.datetime.now()
    recommend = 0
    thread = (user_id, img_id, content, category_id, ip, review, thread_id, title, edit_time, recommend, has_img, platform, tags, skus)
    try:
        conn = engine.connect()
        res = conn.execute("insert into threads (user_id, img_id, content, category_id, ip, review, main_thread_id, \
            title, edit_time, recommend, has_img, platform, tags, skus) values (%s, %s, %s, %s, inet_aton(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s);", thread)
        last_id = res.lastrowid
    except Exception, ex:
        print Exception, ex
        return 0
    finally:
        conn.close()
    return last_id

@timer
#@deco_cache(prefix = 'thread_ids', recycle = TEN_SECONDS)
def get_thread_ids(flag, num, category_id, use_cache = True):
    DBSession = rdbsession_generator()
    if category_id == 0:
        thread_ids = DBSession.query(Thread.id).filter(Thread.update_ts < flag).filter(Thread.review ==
                1).filter(Thread.main_thread_id == 0).order_by(Thread.update_ts.desc()).limit(num).all()
    else:
        thread_ids = DBSession.query(Thread.id).filter(Thread.category_id == category_id).filter(Thread.update_ts <
            flag).filter(Thread.review == 1).filter(Thread.main_thread_id == 0).order_by(Thread.update_ts.desc()).limit(num).all()
    DBSession.close()
    thread_ids = [id[0] for id in thread_ids]
    return thread_ids

@timer
def get_none_top_thread_ids(flag, num, category_id, use_cache = True):
    DBSession = rdbsession_generator()
    if category_id == 0:
        thread_ids = DBSession.query(Thread.id).filter(Thread.update_ts < flag).filter(Thread.review ==
                1).filter(Thread.is_top == 0).filter(Thread.main_thread_id == 0).order_by(Thread.update_ts.desc()).limit(num).all()
    else:
        thread_ids = DBSession.query(Thread.id).filter(Thread.category_id == category_id).filter(Thread.update_ts <
            flag).filter(Thread.review == 1).filter(Thread.is_top == 0).filter(Thread.main_thread_id == 
            0).order_by(Thread.update_ts.desc()).limit(num).all()
    DBSession.close()
    thread_ids = [id[0] for id in thread_ids]
    return thread_ids

@timer
@deco_cache(prefix = 'thread', recycle = MINUTE)
def get_thread_by_id(thread_id, use_cache = True):
    DBSession = dbsession_generator()
    thread = DBSession.query(Thread).filter(Thread.id == int(thread_id)).filter(Thread.review == 1).first()
    DBSession.close()
    return thread

@timer
def get_thread_ids_by_user_id(user_id, flag, limit):
    DBSession = rdbsession_generator()
    thread_ids = DBSession.query(Thread.id).filter(Thread.main_thread_id == 0).filter(Thread.user_id == user_id).filter(Thread.review == 1).filter(Thread.id <
            flag).order_by(Thread.id.desc()).limit(limit).all()
    DBSession.close()
    return thread_ids

@timer
@deco_cache(prefix = 'user_thread_count', recycle = HOUR)
def get_thread_count_by_user_id(user_id, use_cache = True):
    try:
        DBSession = rdbsession_generator()
        count = DBSession.query(func.count(Thread.id)).filter(Thread.main_thread_id == 0).filter(Thread.user_id == user_id).filter(Thread.review == 1).first()
    except Exception, ex:
        print Exception, ex
        transaction.abort()
        return 0
    finally:
        DBSession.close()
    return count[0]

@timer
def delete_thread(user_id, thread_id):
    try:
        DBSession = dbsession_generator()
        DBSession.query(Thread).filter(Thread.id == thread_id).filter(Thread.user_id == user_id).update({Thread.review:0})
        transaction.commit()
    except Exception, ex:
        print Exception, ex
        transaction.abort()
        return 0
    finally:
        DBSession.close()
    return 1

@timer
def update_thread_ts(thread_id):
    try:
        conn = engine.connect()
        res = conn.execute("update threads set update_ts = now() where id = %s", thread_id)
    except Exception, ex:
        print Exception, ex
        return 0
    finally:
        conn.close()
    return 1

@timer
@deco_cache(prefix = 'sub_thread', recycle = MINUTE)
def get_sub_threads_by_id(thread_id, use_cache = True):
    try:
        DBSession = rdbsession_generator()
        threads = DBSession.query(Thread).filter(Thread.main_thread_id == thread_id).order_by(Thread.id).all()
    except Exception, ex:
        print Exception, ex
        return []
    finally:
        DBSession.close()
    return threads

@timer
@deco_cache(prefix = 'recommend_thread_ids', recycle = MINUTE)
def get_recommend_thread_ids():
    try:
        DBSession = rdbsession_generator()
        ids = DBSession.query(Thread.id).filter(Thread.recommend > 0).filter(Thread.review ==
                1).order_by(Thread.recommend.desc()).limit(30).all()
        ids = [id[0] for id in ids]
    except Exception, ex:
        print Exception, ex
        return []
    finally:
        DBSession.close()
    return ids

@timer
@deco_cache(prefix = 'forum_elite_thread_ids', recycle = MINUTE)
def get_elite_thread_ids(forum_id, flag, limit):
    try:
        DBSession = rdbsession_generator()
        ids = DBSession.query(Thread.id).filter(Thread.is_favor == 1).filter(Thread.review == 1).filter(Thread.category_id
                == int(forum_id)).filter(Thread.update_ts < flag).order_by(Thread.update_ts.desc()).limit(limit).all()
        ids = [id[0] for id in ids]
    except Exception, ex:
        print Exception, ex
        return []
    finally:
        DBSession.close()
    return ids

@timer
@deco_cache(prefix = 'forum_top_thread_ids', recycle = MINUTE)
def get_top_thread_ids(forum_id):
    try:
        DBSession = rdbsession_generator()
        ids = DBSession.query(Thread.id).filter(Thread.is_top == 1).filter(Thread.review == 1).filter(Thread.category_id
                == int(forum_id)).order_by(Thread.update_ts.desc()).all()
        ids = [id[0] for id in ids]
    except Exception, ex:
        print Exception, ex
        return []
    finally:
        DBSession.close()
    return ids

@timer
@deco_cache(prefix = 'forum_thread_count', recycle = MINUTE)
def get_forum_thread_count(forum_id):
    try:
        DBSession = rdbsession_generator()
        count = DBSession.query(func.count(Thread.id)).filter(Thread.category_id == int(forum_id)).first()
        if count: count = count[0]
        else: count = 0
        DBSession.close()
    except Exception, ex:
        print Exception, ex
        return 0
    finally:
        DBSession.close()
    return count

@deco_cache(prefix = 'thread_category_id', recycle = HOUR)
def get_thread_category_id(thread_id):
    DBSession = rdbsession_generator()
    category_id = DBSession.query(Thread.category_id).filter(Thread.id == int(thread_id)).first()
    category_id = category_id[0]
    DBSession.close()
    return category_id

@timer
def get_ids_by_user_id(user_id, use_cache = True):
    DBSession = rdbsession_generator()
    thread_ids = DBSession.query(Thread.id).filter(
            Thread.user_id == int(user_id)).filter(
            Thread.review == 1).order_by(Thread.update_ts.desc()).all()
    DBSession.close()
    thread_ids = [id[0] for id in thread_ids]
    return thread_ids

def main():
    res = get_ids_by_user_id(739348)
    print res

if __name__ == "__main__":
    main()

