# -*- coding:utf-8 -*-

from hichao.forum.models.thread import Thread
from hichao.forum.models.db import (
    dbsession_generator,
    rdbsession_generator,
    )
from hichao.util.statsd_client import timeit
from hichao.util.date_util import HOUR
from hichao.cache.cache import (
    deco_cache_m,
    deco_cache,
    )
from hichao.upload.models.image import get_images_by_id
from hichao.sku.models.sku import (
    get_ecskus_by_source_id,
    get_sku_cache_by_sourceid,
    )
from hichao.comment.models.sub_thread import (
    get_latest_subthread_ids_by_thread_id,
    get_subthreads_by_id,
    )
from hichao.base.config import (
    APP_LOGO,
    FALL_PER_PAGE_NUM,
    WEB_URL_DOMAIN,
    )
from hichao.collect.models.thread import thread_collect_user_list_by_thread_id
from hichao.user.models.user import get_users_by_id
from hichao.forum.models.tag import get_tags_by_id
from hichao.forum.models.star_user import (
    get_staruser_by_id,
    user_is_staruser,
    get_staruser_by_user_id,
    )
from hichao.util.date_util import get_rough_time
from hichao.sku.models.sku import get_sku_by_id
timer = timeit('hichao_backend.m_post')


class Post(Thread):
    def __init__(self):
        super(Post, self).__init__()
        self._con_coms = []
        self._con_sku_coms = []

    def get_bind_tags(self):
        if self.tags:
            tag_ids = self.tags.split(',')
            tags = get_tags_by_id(tag_ids,use_cache=False)
            return tags
        return []

    @property
    def split_items(self):
        return 1

    @property
    def inner_redirect(self):
        return 1

    @property
    def support_brandstore(self):
        return 1

    @property
    def con_sku_coms(self):
        if not getattr(self, '_con_sku_coms', None): return []
        return self._con_sku_coms

    @con_sku_coms.setter
    def con_sku_coms(self, value):
        self._con_sku_coms = value

    @property
    def con_coms(self):
        if not getattr(self, '_con_coms', None): return []
        return self._con_coms

    @con_coms.setter
    def con_coms(self, value):
        self._con_coms = value

    def get_component_tags(self):
        tags = self.get_bind_tags()
        tag_coms = []
        if tags:
            for tag in tags:
                tag_com = {}
                if tag:
                    tag_com['category'] = tag.tag
                    tag_com['id'] = str(tag.id)
                    tag_com['collectionType'] = 'topic'
                    tag_com['action'] = tag.get_tag_action()
                    tag_coms.append(tag_com)
        return tag_coms

    def get_bind_imgs(self):
        img_ids = self.get_bind_img_ids()
        return get_images_by_id(img_ids, use_cache = False)

    def get_component_imgs(self):
        imgs = self.get_bind_imgs()
        img_coms = []
        for img in imgs:
            if img:
                img.support_webp = 1
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
                img_coms.append(ui)
        return img_coms

    def get_component_lite_imgs(self):
        imgs = self.get_bind_imgs()
        img_coms = []
        for img in imgs:
            if img:
                img.support_webp = 1
                img_url = img.get_component_pic_detail_url()
                img_coms.append(img_url)
        return img_coms

    def get_bind_skus(self):
        if self.skus:
            skus = []
            source_ids = self.skus.split(',')
            for source_id in source_ids:
                item = get_sku_cache_by_sourceid(source_id)
                if item:
                    sku_id = item[1]
                    sku = get_sku_by_id(sku_id)
                    skus.append(sku)
            return skus
        return []

    def get_con_coms(self):
        if not self.con_coms:
            self.con_coms, self.con_sku_coms = self.get_component_content_with_sku()

    def get_component_skus(self):
        skus = self.get_bind_skus()
        sku_coms = []
        if skus:
            for sku in skus:
                if sku:
                    sku['support_ec'] = 1
                    ui = {}
                    com = {}
                    com['componentType'] = 'embedItem'
                    com['picUrl'] = sku.get_small_pic_url()
                    com['description'] = sku.get_component_description()
                    com['price'] = sku.get_component_price()
                    com['channelPicUrl'] = sku.get_channel_url()
                    com['source'] = sku.get_channel_name()
                    com['action'] = sku.to_lite_ui_action()
                    ui['component'] = com
                    sku_coms.append(ui)
        self.get_con_coms()
        sku_coms.extend(self.con_sku_coms)
        return sku_coms

    def get_component_content(self):
        self.get_con_coms()
        return self.con_coms

    def get_bind_comment_ids(self):
        limit = 3
        return get_latest_subthread_ids_by_thread_id(self.id, limit)

    def get_bind_comments(self):
        comment_ids = self.get_bind_comment_ids()
        if comment_ids:
            comments = get_subthreads_by_id(comment_ids)
            return comments
        return []

    def get_component_comments(self):
        comments = self.get_bind_comments()
        comment_coms = []
        for comment in comments:
            com = {}
            com['username'] = title = comment.get_component_user_name()
            if comment.comment_id > 0:
                to_user = comment.get_to_user()
                if to_user:
                    title += ' 回复 ' + to_user.get_component_user_name() + ':'
                else:
                    title += ':'
            else:
                title += ':'
            com['title'] = title
            com['content'] = comment.get_content()
            comment_coms.append(com)
        return comment_coms

    def get_bind_liked_users(self):
        user_ids = thread_collect_user_list_by_thread_id(self.id, offset = 0, limit = 5)
        user_ids = [int(user_id[0]) for user_id in user_ids if int(user_id[0]) > 0]
        user_ids_new = []
        for user_id in user_ids:
            if user_id not in user_ids_new:
                user_ids_new.append(user_id)
        if not user_ids_new: return []
        return get_users_by_id(user_ids_new)

    def get_component_liked_users(self):
        users = self.get_bind_liked_users()
        user_coms = []
        for user in users:
            if user:
                com = {}
                com['userAvatar'] = user.get_component_user_avatar()
                com['userId'] = str(user.get_component_id())
                com['action'] = user.to_lite_ui_action()
                user_coms.append(com)
        return user_coms

    def get_component_user(self):
        user = self.get_bind_user()
        if not user:
            return {}
        com = {}
        com['action'] = user.to_lite_ui_action()
        com['userAvatar'] = user.get_component_user_avatar()
        com['userId'] = user.get_component_id()
        com['username'] = user.get_component_user_name()
        com['datatime'] = self.get_component_publish_date()
        return com

    def get_share_action(self):
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
        obj['type']='topic'
        obj['typeId']=self.get_component_id()
        obj['trackValue']='{0}_{1}'.format(obj['type'],obj['typeId'])
        obj['share']=action
        return obj

    def to_ui_action(self):
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'thread'
        action['id'] = str(self.id)
        return action

    def to_lite_ui_action(self):
        return self.to_ui_action()

    def get_user_identify(self):
        staruser = get_staruser_by_user_id(self.user_id)
        if staruser:
            return staruser.get_staruser_type()
        return {}
    def get_user_type_name(self):
        if user_is_staruser(self.user_id):
            staruser = get_staruser_by_user_id(self.user_id)
            _type = staruser.get_staruser_type()
            return _type
        return {}

@timer
@deco_cache_m(prefix = 'post', recycle = HOUR)
def get_posts_by_id(post_ids):
    post_ids = [int(_id) for _id in post_ids]
    DBSession = rdbsession_generator()
    posts = DBSession.query(Post.id, Post).filter(Post.id.in_(post_ids)).filter(Post.review == 1).all()
    posts = dict(posts)
    DBSession.close()
    return posts

@timer
@deco_cache(prefix = 'post', recycle = HOUR)
def get_post_by_id(post_id):
    DBSession = rdbsession_generator()
    post = DBSession.query(Post).filter(Post.id == int(post_id)).filter(Post.review == 1).first()
    DBSession.close()
    return post

@timer
def get_post_ids_by_user_ids(user_ids,flag ,limit =FALL_PER_PAGE_NUM):
    DBSession = rdbsession_generator()
    post_ids = DBSession.query(Post.id).filter(Post.user_id.in_(user_ids)).filter(Post.review == 1).order_by(Post.edit_time.desc()).offset(flag).limit(limit).all()
    DBSession.close()
    post_ids = [post_id[0] for post_id in post_ids]
    return post_ids
