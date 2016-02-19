# -*- coding:utf8 -*-

from icehole_client.files_client import (
        get_filename,
        )
from hichao.base.config import CDN_FAST_DFS_IMAGE_PREFIX
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_tuangou_imageurl')

@timer
def build_tuan_image_url(url):
    res = get_filename("tuangou", url)
    res = '{0}/{1}?imageMogr2/auto-orient/thumbnail/{2}x%3E/quality/80'.format(CDN_FAST_DFS_IMAGE_PREFIX(), res, '600')
    return res

@timer
def build_tuan_sku_image_url(url, origin=False):
    #res = url.split(".")
    #if origin==False:
    #    if res[1] == 'jpg':
    #        #_url = res[0]+"_wnormal."+res[1]
    #        _url = res[0] + res[1] + r'/' + '?imageMogr2/auto-orient/thumbnail/320x>'
    #    else:
    #        #_url = res[0]+"_normal."+res[1]
    #        _url = res[0] + res[1] + r'/' + '?imageMogr2/auto-orient/thumbnail/320x>'
    #else:
    #    _url = url
    res = get_filename("tuangou",url)
    if not res:
        res = get_filename("backend_images",url)
    if origin:
        return '{0}/{1}?imageMogr2/auto-orient/thumbnail/{2}x%3E/quality/80'.format(CDN_FAST_DFS_IMAGE_PREFIX(), res, '640')
    else:
        return '{0}/{1}?imageMogr2/auto-orient/thumbnail/{2}x%3E/quality/80'.format(CDN_FAST_DFS_IMAGE_PREFIX(), res, '320')

