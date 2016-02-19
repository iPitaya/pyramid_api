#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import datetime
import json
import urllib
from os import urandom
from hashlib import md5
from urllib import quote
from base64 import urlsafe_b64encode
import requests
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from hichao.base.views.view_base import View
from hichao.base.lib.redis import redis, redis_key
from hichao.base.lib.require import require, RequirementException
from hichao.app.views.oauth2 import check_permission
from hichao.upload.lib.qiniu_upload import QiNiu
from hichao.upload.config import QINIU_BUCKET_NAME, UPLOAD_IMAGE_CALLBACK_URL, QINIU_UPLOAD_IMAGE_CALLBACK_URL, QINIU_IMAGE_URL
from hichao.forum import THREAD_STATUS
from hichao.forum.models.thread import add_thread
from hichao.upload.models.image import add_image
from hichao.util.pack_data import pack_data
from hichao.base.lib.timetool import today_days, day2days
from hichao.collect.models.thread import REDIS_THREAD_PUBLISH_DAYS, thread_collect_new
from hichao.user.models.refused_user import user_in_black_list
from hichao.user.models.user import add_user_avatar, add_user_background
from hichao.util.content_util import (
        content_has_sensitive_words,
        filter_tag,
        content_to_crawl,
        )
from hichao.points.models.points import point_change
from hichao.forum.models.forum import get_forum_cat_id_by_name
from hichao.util.statsd_client import statsd

ETAG_EXPIRE = 600# 10分钟
TAG_EXPIRE = 3600# 一个小时
REDIS_UPLOAD_ETAG = redis_key.UploadImageEtagByUserId('%s')
REDIS_UPLOAD_TAG = redis_key.UploadImageUserIdByTag('%s')

def generate_etag(user_id):
    tag = urlsafe_b64encode(urandom(8)).rstrip("=")
    key = REDIS_UPLOAD_ETAG%user_id
    r = 0
    try:
        r = redis.setex(key, ETAG_EXPIRE, tag)
    except Exception, ex:
        print Exception, ex
        r = redis.setex(key, ETAG_EXPIRE, tag)
    if r:
        return tag
    else:
        return 0

def check_etag(user_id, tag):
    key = REDIS_UPLOAD_ETAG%user_id
    tag = redis.get(key)
    if tag:
        return 1
    else:
        return 0

def generate_tag(user_id):
    tag = urlsafe_b64encode(urandom(8)).rstrip("=")
    key = REDIS_UPLOAD_TAG%tag
    r = 0
    try:
        r = redis.setex(key, ETAG_EXPIRE, tag)
    except Exception, ex:
        print Exception, ex
        r = redis.setex(key, ETAG_EXPIRE, tag)
    if r:
        return tag
    else:
        return 0

def check_tag(user_id, tag):
    #key = REDIS_UPLOAD_TAG%tag
    #_user_id = redis.get(key)
    #if _user_id and int(_user_id) == int(user_id):
    #    return 1
    #else:
    #    return 0
    return 1

def generate_file_name_key(user_id):
    dt = datetime.datetime.today()
    dt = dt.strftime('%Y-%m-%d-')
    filename = '%s%s'%(dt, md5('%s%s'%(user_id, time.time())).hexdigest())
    key = filename

    return filename, key


class UploadImage(View):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(UploadImage, self).__init__(*args, **kwargs)

    @statsd.timer('hichao_backend.r_img_upload_token.get')
    @check_permission
    @view_config(route_name='img_upload_token', request_method='GET', renderer = 'json')
    @pack_data
    def img_upload_token(self, bucket =QINIU_BUCKET_NAME):
        resp = dict()
        if self.user_id <= 0:
            self.error['errorCode'] = '21113'
            self.error['error'] = u'非法上传'
            #return self.error
            return '', {}

        policy = QiNiu.PutPolicy(bucket)
        policy.expires = 3600

        type = self.request.params.get('type', '')
        if not type:
            resp['tag'] = generate_etag(self.user_id)
            callbackUrl = UPLOAD_IMAGE_CALLBACK_URL
            callback_body = "key=$(key)&size=$(fsize)&uid=$(endUser)&imageInfo=$(imageInfo)&mimeType=$(mimeType)&category=$(x:category)&content=$(x:content)&rotate=$(x:rotate)&tag=%s&access_token=%s"%(resp['tag'], self.access_token)

        #根据type 生成callback_url, callback_body
        #elif type == 'subject':
        else:
            resp['tag'] = generate_tag(self.user_id)
            callbackUrl = QINIU_UPLOAD_IMAGE_CALLBACK_URL
            callback_body = "key=$(key)&size=$(fsize)&uid=$(endUser)&imageInfo=$(imageInfo)&mimeType=$(mimeType)&type=$(x:type)&rotate=$(x:rotate)&tag=%s&access_token=%s"%(resp['tag'], self.access_token)

        policy.callbackUrl = callbackUrl
        policy.callbackBody = callback_body

        uptoken = policy.token()
        resp['filename'], resp['key'] = generate_file_name_key(self.user_id)
        resp['uptoken'] =  uptoken
        return '', resp

    @statsd.timer('hichao_backend.r_qiniu_img_upload.post')
    @check_permission
    @view_config(route_name='qiniu_img_upload', request_method='POST', renderer = 'json')
    @pack_data
    def qiniu_img_callback(self):
        if self.user_id < 1:
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return '', {}
        tag = self.request.params.get('tag', '')
        _type = self.request.params.get('type', '')
        key = self.request.params.get('key', '')
        key = filter_tag(key)
        rotate = self.request.params.get('rotate', 0)
        imageInfo= self.request.params.get('imageInfo', '')
        imageInfo = json.loads(imageInfo)

        if tag:
            resp = dict()
            if check_tag(self.user_id, tag):
                if rotate and int(rotate) != 0 and int(rotate)%180 !=0:
                    height = imageInfo['width']
                    width = imageInfo['height']
                else:
                    height = imageInfo['height']
                    width = imageInfo['width']
                image_id = add_image(self.user_id, '%s%s'%(QINIU_IMAGE_URL, key), height, width, rotate)
                if image_id:
                    resp['image_id'] = image_id
                    if _type =="subject":
                        resp['ok'] = '图片上传成功'
                    elif _type =="background":
                        add_user_background(self.user_id, image_id)
                        resp['ok'] = '背景已更改'
                    elif _type =="avatar":
                        status, update_num = add_user_avatar(self.user_id, image_id)
                        if status and update_num:
                            resp['ok'] = '头像已更改'
                            #point_change.delay(self.user_id, "improve_personal_avatar", image_id, time.time())
                        elif not status:
                            resp['ok'] = '图片上传失败'
                    return '', resp
                else:
                    resp['ok'] = '图片上传失败'
                    return '', resp

class CheckUpload(View):

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(CheckUpload, self).__init__(*args, **kwargs)

    @statsd.timer('hichao_backend.r_img_upload_check.post')
    @check_permission
    @view_config(route_name='img_upload_check', request_method='POST', renderer = 'json')
    @pack_data
    def img_upload_check(self):
        if self.user_id == -2:
            self.error['error'] = 'User info expired.'
            self.error['errorCode'] = '20002'
            return '', {}
        if self.user_id == -1:
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return '', {}
        tag = self.request.params.get('tag', '')
        key = self.request.params.get('key', '')

        category = self.request.params.get('category', '')
        if not category:
            QiNiu.uri_delete(QINIU_BUCKET_NAME, key)
            self.error['errorCode'] = '10002'
            self.error['error'] = u'Arguments missing.'
            return '', {}
        else:
            category = urllib.unquote_plus(category.encode('utf-8')).decode('utf-8')
            category_id = get_forum_cat_id_by_name(category)

        # 判断用户是否在黑名单内。
        if user_in_black_list(self.user_id):
            QiNiu.uri_delete(QINIU_BUCKET_NAME, key)
            self.error['errorCode'] = '40001'
            self.error['error'] = 'Permission denied.'
            return '', {}

        etag = self.request.params.get('etag', '')
        imageInfo= self.request.params.get('imageInfo', '')
        filename = self.request.params.get('fname', '')
        imageInfo = json.loads(imageInfo)

        #{"format":"jpeg","width":640,"height":960,"colorModel":"ycbcr"}

        content = self.request.params.get('content', '')
        rotate = self.request.params.get('rotate', '')
        if not rotate:
            rotate = 0
        content= urllib.unquote_plus(content.encode('utf-8'))

        # 判断是否包含敏感词。
        status = content_has_sensitive_words(content)
        if status == 1:
            QiNiu.uri_delete(QINIU_BUCKET_NAME, key)
            self.error['errorCode'] = '40001'
            self.error['error'] = 'Permission denied.'
            return '', {}
        key = filter_tag(key)
        content = filter_tag(content)

        if tag:
            resp = dict()
            if check_etag(self.user_id, tag):
                if rotate and int(rotate) != 0 and int(rotate)%180 !=0:
                    width = imageInfo['height']
                    height = imageInfo['width']
                else:
                    height = imageInfo['height']
                    width = imageInfo['width']
                image_id = add_image(self.user_id, '%s%s'%(QINIU_IMAGE_URL, key), height, width, rotate)
                if not image_id:
                    resp['ok'] = '发贴失败'
                    return '', resp
                review = 1

                thread = add_thread(self.user_id, image_id, content, category_id, review)
                #thread = 1
                thread_list = []
                if thread:
                    content_to_crawl(int(self.user_id), content, thread)
                    redis.hset(REDIS_THREAD_PUBLISH_DAYS, thread, day2days(time.time()))
                    thread_list.append(thread)
                    # 负1为 系统用户
                    thread_collect_new(-1, thread_list, n=0)
                    resp['ok'] =  '200'
                else:
                    resp['ok'] =  '发帖失败'

                return '', resp
            else:
                self.error['errorCode'] = '21111'
                QiNiu.uri_delete(QINIU_BUCKET_NAME, key)
        else:
            self.error['errorCode'] = '21112'
        if self.error:
            self.error['error'] = u'非法上传'
            #return self.error
            return '', {}


if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
