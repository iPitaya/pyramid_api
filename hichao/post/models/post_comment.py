# -*- coding:utf-8 -*-

from hichao.comment.models.sub_thread import SubThread
from hichao.comment.models.db import rdbsession_generator
from hichao.util.statsd_client import timeit
from hichao.cache.cache import (
    deco_cache_m,
    deco_cache,
    )
from hichao.sku.models.sku import (
    get_ecskus_by_source_id,
    get_sku_by_id,
    get_sku_cache_by_sourceid,
    )
from hichao.upload.models.image import get_images_by_id
from hichao.util.date_util import (
    MINUTE,
    FIVE_MINUTES,
    )
from hichao.base.config import FALL_PER_PAGE_NUM


timer = timeit('hichao_backend.m_post_comment')


class PostComment(SubThread):
    def __init__(self):
        super(PostComment, self).__init__()
        self._con_sku_coms = []
        self._con_coms = []

    def get_bind_imgs(self):
        img_ids = self.get_bind_img_ids()
        imgs = get_images_by_id(img_ids)
        return imgs

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

    def get_bind_skus(self):
        if self.skus:
            source_ids = self.skus.split(',')
            skus = []
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


@timer
@deco_cache(prefix = 'post_comment', recycle = FIVE_MINUTES)
def get_post_comment_by_id(comment_id):
    DBSession = rdbsession_generator()
    post_comment = DBSession.query(PostComment).filter(PostComment.id == int(comment_id)).first()
    DBSession.close()
    return post_comment

@timer
@deco_cache_m(prefix = 'post_comment', recycle = FIVE_MINUTES)
def get_post_comments_by_id(comment_ids):
    comment_ids = [int(comment_id) for comment_id in comment_ids]
    DBSession = rdbsession_generator()
    post_comments = DBSession.query(PostComment.id, PostComment).filter(PostComment.id.in_(comment_ids)).all()
    post_comments = dict(post_comments)
    DBSession.close()
    return post_comments
@timer
#@deco_cache(prefix = 'norepost_comment', recycle = FIVE_MINUTES)
def get_norepost_post_comment_ids_by_ids(post_id, offset, limit=FALL_PER_PAGE_NUM):
    DBSession = rdbsession_generator()
    post_comment_ids = DBSession.query(PostComment.id).filter(PostComment.repost == 0).filter(PostComment.item_id == int(post_id)).order_by(PostComment.ts.desc()).offset(offset).limit(limit).all()
    DBSession.close()
    post_comment_ids = [comment_id[0] for comment_id in post_comment_ids]
    return post_comment_ids

@timer
@deco_cache(prefix = 'repost_comments', recycle = MINUTE)
def get_repost_comments(post_id, use_cache = True):
    DBSession = rdbsession_generator()
    post_comments = DBSession.query(PostComment).filter(PostComment.repost == 1).filter(PostComment.item_id == int(post_id)).order_by(PostComment.ts.asc()).all()
    DBSession.close()
    return post_comments

