# -*- coding:utf-8 -*-
from urlparse import urlparse
#QINIUDN_HOST_CDN = "http://img1.hichao.com"
#FAST_DFS_QINIU_HOST = "http://mxycsku.u.qiniudn.com"
#SKU_ATTACHED_IMAGE_HOST = 'http://mxycsku.qiniudn.com'
#UPAPYUN_HOST_CDN = 'http://mxyc-img.b0.upaiyun.com'
#FORUM_HOST_CDN = 'http://img2.hichao.com'
#FORUM_HOST_CDN_1 = 'http://img2.hichao.com'

# ================ MXYC ================
#QINIUDN_HOST_CDN = "http://mxyc.qiniucdn.com"
MXYC_HOST_1 = 'http://m.pimg.cn'
MXYC_HOST_2 = 'http://m0.pimg.cn'
MXYC_HOST_3 = 'http://m1.pimg.cn'
MXYC_HOST_4 = 'http://m2.pimg.cn'
MXYC_HOST_5 = 'http://m3.pimg.cn'
MXYC_HOST_6 = 'http://m4.pimg.cn'
MXYC_HOST_7 = 'http://m5.pimg.cn'
MXYC_HOST_8 = 'http://m6.pimg.cn'

MXYC_HOSTS_QINIU = [
        MXYC_HOST_1,
        MXYC_HOST_2,
        MXYC_HOST_3,
        MXYC_HOST_4,
        MXYC_HOST_5,
        MXYC_HOST_6,
        MXYC_HOST_7,
        MXYC_HOST_8,
]

MXYC_HOSTS_WANGSU = []

MXYC_HOSTS = MXYC_HOSTS_QINIU + MXYC_HOSTS_WANGSU

# ================ MXYC_SKU =================
#FAST_DFS_QINIU_HOST = "http://mxycsku.qiniucdn.com"
FAST_DFS_QINIU_HOST_1 = "http://s0.pimg.cn"
FAST_DFS_QINIU_HOST_2 = "http://s1.pimg.cn"
FAST_DFS_QINIU_HOST_3 = "http://s2.pimg.cn"
FAST_DFS_QINIU_HOST_4 = "http://s3.pimg.cn"
FAST_DFS_QINIU_HOST_5 = "http://s4.pimg.cn"
FAST_DFS_QINIU_HOST_6 = "http://s5.pimg.cn"
FAST_DFS_QINIU_HOST_7 = "http://s6.pimg.cn"
FAST_DFS_QINIU_HOST_8 = "http://s.pimg.cn"
FAST_DFS_WANGSU_HOST_1 = "http://mxycsku1.pimg.cn"
FAST_DFS_WANGSU_HOST_2 = "http://mxycsku2.pimg.cn"
FAST_DFS_WANGSU_HOST_3 = "http://mxycsku3.pimg.cn"
FAST_DFS_WANGSU_HOST_4 = "http://mxycsku4.pimg.cn"

MXYC_SKU_HOSTS_QINIU = [
        FAST_DFS_QINIU_HOST_1,
        FAST_DFS_QINIU_HOST_2,
        FAST_DFS_QINIU_HOST_3,
        FAST_DFS_QINIU_HOST_4,
        FAST_DFS_QINIU_HOST_5,
        FAST_DFS_QINIU_HOST_6,
        FAST_DFS_QINIU_HOST_7,
        FAST_DFS_QINIU_HOST_8,
]

#MXYC_SKU_HOSTS_WANGSU = [
#        FAST_DFS_WANGSU_HOST_1,
#        FAST_DFS_WANGSU_HOST_2,
#        FAST_DFS_WANGSU_HOST_3,
#        FAST_DFS_WANGSU_HOST_4,
#]

MXYC_SKU_HOSTS_WANGSU = []

MXYC_SKU_HOSTS = MXYC_SKU_HOSTS_QINIU + MXYC_SKU_HOSTS_WANGSU

#SKU_ATTACHED_IMAGE_HOST = 'http://mxycsku.qiniucdn.com'

# ================ MXYC_FORUM ===============
#FORUM_HOST_CDN = 'http://mxycforum.qiniucdn.com'
#FORUM_HOST_CDN_1 = 'http://mxycforum.qiniucdn.com'
FORUM_HOST_CDN_2 = 'http://f.pimg.cn'
FORUM_HOST_CDN_3 = 'http://f0.pimg.cn'
FORUM_HOST_CDN_4 = 'http://f1.pimg.cn'
FORUM_HOST_CDN_5 = 'http://f2.pimg.cn'
FORUM_HOST_CDN_6 = 'http://fws.pimg.cn'
FORUM_HOST_CDN_7 = 'http://fws0.pimg.cn'
FORUM_HOST_CDN_8 = 'http://fws1.pimg.cn'
FORUM_HOST_CDN_9 = 'http://fws2.pimg.cn'

#MXYC_FORUM_HOSTS_QINIU = [
#        FORUM_HOST_CDN_2,
#        FORUM_HOST_CDN_3,
#        FORUM_HOST_CDN_4,
#        FORUM_HOST_CDN_5,
#]

MXYC_FORUM_HOSTS_QINIU = []

MXYC_FORUM_HOSTS_WANGSU = [
        FORUM_HOST_CDN_6,
        FORUM_HOST_CDN_7,
        FORUM_HOST_CDN_8,
        FORUM_HOST_CDN_9,
]

MXYC_FORUM_HOSTS = MXYC_FORUM_HOSTS_QINIU + MXYC_FORUM_HOSTS_WANGSU

# =============== MXYC_UPLOAD =================
MXYC_UPLOADED_CDN_1 = 'http://api.upload1.pimg.cn'
MXYC_UPLOADED_CDN_2 = 'http://api.upload2.pimg.cn'
MXYC_UPLOADED_CDN_3 = 'http://api.upload3.pimg.cn'
MXYC_UPLOADED_CDN_4 = 'http://api.upload4.pimg.cn'

MXYC_UPLOADED_HOSTS_WANGSU = [
        MXYC_UPLOADED_CDN_1,
        MXYC_UPLOADED_CDN_2,
        MXYC_UPLOADED_CDN_3,
        MXYC_UPLOADED_CDN_4,
]

MXYC_UPLOADED_HOSTS = MXYC_UPLOADED_HOSTS_WANGSU

QINIU_HOSTS = MXYC_HOSTS_QINIU + MXYC_SKU_HOSTS_QINIU + MXYC_FORUM_HOSTS_QINIU
WANGSU_HOSTS = MXYC_HOSTS_WANGSU + MXYC_SKU_HOSTS_WANGSU + MXYC_FORUM_HOSTS_WANGSU
UPLOADED_HOSTS = MXYC_UPLOADED_HOSTS
ALL_CDN_HOSTS = MXYC_HOSTS + MXYC_SKU_HOSTS + MXYC_FORUM_HOSTS + MXYC_UPLOADED_HOSTS

CDN_IMAGE_PATH = '/images/images/'
CDN_TOPIC_IMAGE_PATH = '/images/topic/'
CDN_TOPIC_CELL_IMAGE_PATH = '/images/navigator/'
CDN_DEFAULT_AVATAR_IMAGE_PATH = '/static/admin/avatar.png'
CDN_VIDEO_PATH = '/images/video/'
CDN_KEYWORD_IMAGE_PATH = '/images/keyword/'
CDN_ROOT_PATH = '/'

CDN_CHECK_PATH = []
#CDN_CHECK_PATH = [
#        'http://m.pimg.cn/images/images/20141104/3352cffe-6716-41a3-b5f8-e59cf7de795e.jpg',
#        'http://s.pimg.cn/group5/M00/27/36/wKgBf1SvpbuAWZYCAAACdwZ6Pvc699.jpg',
#        'http://f.pimg.cn/check_cdn.jpg',
#        'http://fws.pimg.cn/check_cdn.jpg',
#        'http://cdn1.hichao.com/group6/M00/0C/E7/wKgBjVTAmDmAbxAVAAACdwZ6Pvc45.jpeg',
#        'http://d06.res.meilishuo.net/img/_o/f7/8d/be707422599980f959a651bffe4c_60_34.c6.png',
#        'http://s7.mogucdn.com/pic/140814/pjj0f_ieydqmjrgiydqytbmiytambqgyyde_64x54.png',
#]

QINIU_IMG_OPERATE_FUNCTION = '?imageMogr2'
WANGSU_IMG_OPERATE_FUNCTION = '?op=imageMogr2'
UPLOADED_IMG_OPERATE_FUNCTION = ''

IMG_OPERATE_FUNCTION = {}
for host in ALL_CDN_HOSTS:
    if host in QINIU_HOSTS:
        IMG_OPERATE_FUNCTION[urlparse(host)[1]] = QINIU_IMG_OPERATE_FUNCTION
    elif host in WANGSU_HOSTS:
        IMG_OPERATE_FUNCTION[urlparse(host)[1]] = WANGSU_IMG_OPERATE_FUNCTION
    elif host in UPLOADED_HOSTS:
        IMG_OPERATE_FUNCTION[urlparse(host)[1]] = UPLOADED_IMG_OPERATE_FUNCTION

QINIU_IMG_FORMAT_FUNCTION = '/format/WEBP'
WANGSU_IMG_FORMAT_FUNCTION = ''
UPLOADED_IMG_FORMAT_FUNCTION = ''

IMG_FORMAT_FUNCTION = {}
for host in ALL_CDN_HOSTS:
    if host in QINIU_HOSTS:
        IMG_FORMAT_FUNCTION[urlparse(host)[1]] = QINIU_IMG_FORMAT_FUNCTION
    elif host in WANGSU_HOSTS:
        IMG_FORMAT_FUNCTION[urlparse(host)[1]] = WANGSU_IMG_FORMAT_FUNCTION
    elif host in UPLOADED_HOSTS:
        IMG_FORMAT_FUNCTION[urlparse(host)[1]] = UPLOADED_IMG_FORMAT_FUNCTION

QINIU_IMG_THUMBNAIL_FUNCTION = '/thumbnail/{0}x%3E'
WANGSU_IMG_THUMBNAIL_FUNCTION = '&thumbnail={0}x0%3E'
UPLOADED_IMG_THUMBNAIL_FUNCTION = '_thumb_{0}x%3E'

IMG_THUMBNAIL_FUNCTION = {}
for host in ALL_CDN_HOSTS:
    if host in QINIU_HOSTS:
        IMG_THUMBNAIL_FUNCTION[urlparse(host)[1]] = QINIU_IMG_THUMBNAIL_FUNCTION
    elif host in WANGSU_HOSTS:
        IMG_THUMBNAIL_FUNCTION[urlparse(host)[1]] = WANGSU_IMG_THUMBNAIL_FUNCTION
    elif host in UPLOADED_HOSTS:
        IMG_THUMBNAIL_FUNCTION[urlparse(host)[1]] = UPLOADED_IMG_THUMBNAIL_FUNCTION

QINIU_IMG_CROP_FUNCTION = '/crop/!{width}x{height}a{x}a{y}'
WANGSU_IMG_CROP_FUNCTION = '&crop=!{width}x{height}a{x}a{y}'
UPLOADED_IMG_CROP_FUNCTION = '_crop_{width}x{height}a{x}a{y}'

IMG_CROP_FUNCTION = {}
for host in ALL_CDN_HOSTS:
    if host in QINIU_HOSTS:
        IMG_CROP_FUNCTION[urlparse(host)[1]] = QINIU_IMG_CROP_FUNCTION
    elif host in WANGSU_HOSTS:
        IMG_CROP_FUNCTION[urlparse(host)[1]] = WANGSU_IMG_CROP_FUNCTION
    elif host in UPLOADED_HOSTS:
        IMG_CROP_FUNCTION[urlparse(host)[1]] = UPLOADED_IMG_CROP_FUNCTION

QINIU_IMG_QUALITY_FUNCTION = '/quality/{0}'
WANGSU_IMG_QUALITY_FUNCTION = '&quality={0}'
UPLOADED_IMG_QUALITY_FUNCTION = '_quality_{0}'

IMG_QUALITY_FUNCTION = {}
for host in ALL_CDN_HOSTS:
    if host in QINIU_HOSTS:
        IMG_QUALITY_FUNCTION[urlparse(host)[1]] = QINIU_IMG_QUALITY_FUNCTION
    elif host in WANGSU_HOSTS:
        IMG_QUALITY_FUNCTION[urlparse(host)[1]] = WANGSU_IMG_QUALITY_FUNCTION
    elif host in UPLOADED_HOSTS:
        IMG_QUALITY_FUNCTION[urlparse(host)[1]] = UPLOADED_IMG_QUALITY_FUNCTION


IMG_HOST_CLUSTER = MXYC_HOSTS_QINIU + MXYC_HOSTS_WANGSU

FASTDFS_HOST_CLUSTER = MXYC_SKU_HOSTS_QINIU + MXYC_SKU_HOSTS_WANGSU

FORUM_HOST_CLUSTER = MXYC_FORUM_HOSTS_QINIU + MXYC_FORUM_HOSTS_WANGSU

UPLOADED_HOST_CLUSTER = MXYC_UPLOADED_HOSTS

def generate_cdn_image_url(route_str):
    index = 0
    count = len(IMG_HOST_CLUSTER)
    while True:
        mystr = IMG_HOST_CLUSTER[index] + route_str
        yield mystr
        index = index + 1
        if index == count:
            index = 0

def generate_cdn_prefix(cluster, route_str):
    index = 0
    count = len(cluster)
    while True:
        mystr = cluster[index] + route_str
        yield mystr
        index = index + 1
        if index == count:
            index = 0

def generate_forum_image_prefix():
    index = 0
    count = len(FORUM_HOST_CLUSTER)
    while True:
        yield FORUM_HOST_CLUSTER[index]
        index = index + 1
        if index == count:
            index = 0

generate_fast_dfs_image_prefix = generate_cdn_prefix(FASTDFS_HOST_CLUSTER, CDN_ROOT_PATH)
generate_keyword_image_prefix = generate_cdn_prefix(IMG_HOST_CLUSTER, CDN_KEYWORD_IMAGE_PATH)
generate_search_star_list_image_prefix = generate_cdn_prefix(IMG_HOST_CLUSTER, CDN_ROOT_PATH)
generate_sku_detail_image_prefix = generate_cdn_prefix(FASTDFS_HOST_CLUSTER, CDN_ROOT_PATH)
generate_sku_attached_image_prefix = generate_cdn_prefix(FASTDFS_HOST_CLUSTER, CDN_ROOT_PATH)
generate_user_uploaded_image_prefix = generate_cdn_prefix(UPLOADED_HOST_CLUSTER, CDN_ROOT_PATH)

