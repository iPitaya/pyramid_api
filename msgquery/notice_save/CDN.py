#coding:utf-8
import random
import urlparse

IMG_HOST_1 = "http://img.haobao.com"
IMG_HOST_2 = "http://img2.haobao.com"
QINIUDN_HOST_CDN = "http://mxyc.qiniudn.com"

CDN_IMAGE_PATH = '/images/images/'
CDN_TOPIC_IMAGE_PATH = '/images/topic/'
CDN_TOPIC_CELL_IMAGE_PATH = '/images/navigator/'
CDN_DEFAULT_AVATAR_IMAGE_PATH = '/static/admin/avatar.png'
CDN_VIDEO_PATH = '/images/video/'
CDN_KEYWORD_IMAGE_PATH = '/images/keyword/'
CDN_ROOT_PATH = ''

IMG_HOST_CLUSTER = [
        IMG_HOST_2,
        QINIUDN_HOST_CDN,
        IMG_HOST_2,
        QINIUDN_HOST_CDN,
        QINIUDN_HOST_CDN,
        IMG_HOST_2,
        QINIUDN_HOST_CDN,
        QINIUDN_HOST_CDN,
        IMG_HOST_1,
        QINIUDN_HOST_CDN]

def get_img_url(path):
    if path.startswith("http://"):
        return path.replace('_.webp', '')
    else:
        return random.choice(IMG_HOST_CLUSTER) + CDN_IMAGE_PATH + path

def get_topic_url(path):
    if path.startswith("http://"):
        return path
    else:
        return random.choice(IMG_HOST_CLUSTER) + CDN_TOPIC_IMAGE_PATH + path

def get_drop_url(path):
    split_path = urlparse.urlparse(path)
    main_host = random.choice(IMG_HOST_CLUSTER)
    return urlparse.urljoin(main_host, split_path.path)