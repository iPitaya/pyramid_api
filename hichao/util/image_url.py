# -*- coding:utf-8 -*-

# _gsmall 100,133
# _wsmall 200,266
# _gtall 140,210
# _wtall 215,321
# _gfall 157 3G瀑布流图
# _wfall 314 瀑布流的大图
# _gnormal 235
# _wnormal 470 详情页的大图
# _large 640的大图

from hichao.base.config import (
    CDN_PREFIX,
    CDN_IMAGE_PREFIX,
    CDN_TOPIC_IMAGE_PREFIX,
    CDN_TOPIC_CELL_IMAGE_PREFIX,
    CDN_KEYWORD_IMAGE_PREFIX,
    CDN_VIDEO_PREFIX,
    CDN_DEFAULT_AVATAR_IMAGE,
    CDN_SEARCH_STAR_LIST_IMAGE_PREFIX,
    CDN_SKU_DETAIL_IMAGE_PREFIX,
    CDN_FORUM_IMAGE_PREFIX,
    CDN_SKU_ATTACHED_IMAGE_PREFIX,
    CDN_FAST_DFS_IMAGE_PREFIX,
    CDN_MXYC_UPLOADED_IMAGE_PREFIX,
)
from urlparse import urlparse
from icehole_client.files_client import get_filename as get_img_file
from hichao.base.config.CDN import (
    IMG_OPERATE_FUNCTION,
    IMG_CROP_FUNCTION,
    IMG_THUMBNAIL_FUNCTION,
    IMG_FORMAT_FUNCTION,
    IMG_QUALITY_FUNCTION,
    UPLOADED_HOSTS,
)
from os import path
import functools

STAR_FALL_SIZE = 314
STAR_DETAIL_SIZE = 640

SKU_ITEMS_SIZE = 320
SKU_NORMAL_SIZE = 320
SKU_ORIGIN_SIZE = 640
SKU_SMALL_SIZE = 100
SKU_ATTACHED_SIZE = 600
SKU_DETAIL_SIZE = 600

RE_CROP_IMG_WIDTH = 314

BANNER_IMAGE_WIDTH = 640

KEYWORD_IMG_WIDTH = 128

UPLOAD_IMAGE_FALL_WIDTH = 290
UPLOAD_IMAGE_WIDTH = 640

CRAWL_SMALL_WIDTH = 100

SEARCH_REVOMMEND_WORD_IMG_WIDTH = 120

USER_AVATAR_WIDTH = 120

PANIC_BUYING_WIDTH = 200
CMS_DEFAULT_WIDTH = 750
EVALUATION_DEFAULT_WIDTH = 600

default_user_avatar = CDN_PREFIX() + 'images/images/20131121/cd215d51-8824-45e3-b5f3-797238db303e.png'
qzone_user_avatar = 'http://qzapp.qlogo.cn/qzapp/111111/942FEA70050EEAFBD4DCE2C1FC775E56/100'


def build_cdn_suffix(cdn, width=0, support_webp=0, quality=0):
    suffix = ''
    domain = urlparse(cdn)[1]
    if IMG_OPERATE_FUNCTION.get(domain, ''):
        suffix = IMG_OPERATE_FUNCTION.get(domain)
    if support_webp and IMG_FORMAT_FUNCTION.get(domain, ''):
        suffix = '{0}{1}'.format(suffix, IMG_FORMAT_FUNCTION.get(domain))
    if width and IMG_THUMBNAIL_FUNCTION.get(domain, ''):
        suffix = '{0}{1}'.format(suffix, IMG_THUMBNAIL_FUNCTION.get(domain).format(width))
    if quality and IMG_QUALITY_FUNCTION.get(domain, ''):
        suffix = '{0}{1}'.format(suffix, IMG_QUALITY_FUNCTION.get(domain).format(quality))
    return suffix


def append_uploaded_img_ext(func):
    @functools.wraps(func)
    def _(*args, **kw):
        url = func(*args, **kw)
        parsed_url = urlparse(url)
        domain = 'http://{0}'.format(parsed_url[1])
        if domain in UPLOADED_HOSTS:
            file_path = parsed_url.path
            filename = file_path.rsplit('/', 1)[-1]
            ext = path.splitext(filename.split('_', 1)[0])[1]
            url = '{0}_{1}'.format(url, ext)
        return url
    return _


@append_uploaded_img_ext
def build_star_fall_image_url(str_url, support_webp=0):
    return build_star_image_url(str_url, STAR_FALL_SIZE, support_webp)


@append_uploaded_img_ext
def build_star_detail_image_url(str_url, support_webp=0):
    return build_star_image_url(str_url, STAR_DETAIL_SIZE, support_webp)


@append_uploaded_img_ext
def build_star_image_url(str_url, size=STAR_FALL_SIZE, support_webp=0):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(str_url), build_cdn_suffix(cdn, size, support_webp))


@append_uploaded_img_ext
def build_default_url(str_url):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX() if 'group' in str_url else CDN_PREFIX()
    return cdn + r'/' + remove_first_slash(str_url)


@append_uploaded_img_ext
def build_image_url(str_url, support_webp=0, width=0):
    if str_url.startswith("http://"):
        str_url = str_url.replace('img.haobao.com', 'm.pimg.cn')
        return str_url.replace('_.webp', '')

    else:
        if 'group' in str_url:
            cdn = CDN_FAST_DFS_IMAGE_PREFIX()
        else:
            cdn = CDN_IMAGE_PREFIX()
        return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(str_url)), build_cdn_suffix(cdn, width, support_webp))


@append_uploaded_img_ext
def exchange_cdn(str_url, support_webp=0, width=0, quality=0):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX() if 'group' in str_url else CDN_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(str_url)), build_cdn_suffix(cdn, width, support_webp, quality))


@append_uploaded_img_ext
def build_sku_small_image_url(str_url, support_webp=0):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(str_url), build_cdn_suffix(cdn, SKU_SMALL_SIZE, support_webp))


@append_uploaded_img_ext
def build_topic_image_url(str_url, support_webp=0):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX() if 'group' in str_url else CDN_TOPIC_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(str_url)), build_cdn_suffix(cdn, BANNER_IMAGE_WIDTH, support_webp))


@append_uploaded_img_ext
def build_news_image_url(str_url):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    str_url = get_img_file('navigate_images', str_url)
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(str_url)), build_cdn_suffix(cdn, BANNER_IMAGE_WIDTH))


@append_uploaded_img_ext
def build_topic_cell_image_url(str_url, width=0, support_webp=0, quality=100):
    ext = path.splitext(str_url)[-1].lower()
    if ext == '.gif':
        support_webp = 0
    return exchange_cdn(str_url, support_webp, width, quality)


@append_uploaded_img_ext
def build_topic_cell_image_url_from_dfs(str_url, namespace):
    if 'http' in str_url:
        # 兼容后台的老数据
        str_url = str_url[str_url.find('navigate') + len('navigate'):]
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    str_url = get_img_file(namespace, str_url)
    return '{0}{1}'.format(cdn, remove_first_slash(remove_image_url_domain(str_url)))


@append_uploaded_img_ext
def build_theme_cell_image_url(str_url, width=0, support_webp=0):
    cdn = CDN_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(str_url)), build_cdn_suffix(cdn, width, support_webp))


@append_uploaded_img_ext
def build_topic_show_big_pic_url(str_url, support_webp=0):
    return exchange_cdn(str_url, support_webp)


@append_uploaded_img_ext
def build_topic_drop_image_url(str_url, support_webp=0):
    return build_topic_cell_image_url(str_url, STAR_FALL_SIZE, support_webp)


@append_uploaded_img_ext
def build_theme_drop_image_url(str_url, support_webp=0):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return "{0}{1}{2}".format(cdn, remove_first_slash(str_url), build_cdn_suffix(cdn, support_webp=1))


@append_uploaded_img_ext
def build_banner_theme_image_url(str_url, support_webp=0):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return "{0}{1}{2}".format(cdn, remove_first_slash(str_url), build_cdn_suffix(cdn, support_webp=1))


@append_uploaded_img_ext
def build_video_url(str_url):
    return CDN_VIDEO_PREFIX() + remove_first_slash(str_url)


@append_uploaded_img_ext
def build_flow_image_url(str_url):
    return build_image_url(str_url)


@append_uploaded_img_ext
def build_keyword_image_url(str_url):
    cdn = CDN_KEYWORD_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(str_url), build_cdn_suffix(cdn, KEYWORD_IMG_WIDTH))


@append_uploaded_img_ext
def build_search_star_list_image_url(str_url):
    return '{0}{1}'.format(str_url, build_cdn_suffix(str_url, KEYWORD_IMG_WIDTH))


@append_uploaded_img_ext
def build_fake_user_avatar_url(str_url, support_webp=0):
    return build_image_url(str_url, support_webp)


@append_uploaded_img_ext
def build_drop_image_url(str_url, support_webp=0):
    str_url = str_url.replace('/images/images/', '')        # 因有些吊牌地址可能包含'/images/images/'前缀，去掉这些前缀。
    return build_image_url(str_url, support_webp, STAR_FALL_SIZE)


@append_uploaded_img_ext
def build_user_avatar_url(str_url):
    str_url = str_url.replace('http://haobao.com', 'http://m.pimg.cn')
    if str_url == qzone_user_avatar:
        return default_user_avatar
    return str_url and str_url or default_user_avatar


@append_uploaded_img_ext
def build_upload_image_fall_url(str_url, rotate=0, w=0, x=0, y=0, crop=False, self_uploaded=0, support_webp=0):
    ext = path.splitext(str_url)[1]
    if ext.lower() == '.gif':
        support_webp = 0
    if self_uploaded:
        cdn = CDN_MXYC_UPLOADED_IMAGE_PREFIX()
    else:
        cdn = CDN_FORUM_IMAGE_PREFIX()
    if crop or support_webp:
        domain = urlparse(cdn)[1]
        operate_func = IMG_OPERATE_FUNCTION.get(domain, '')
        str_url = '{0}{1}{2}'.format(cdn, remove_image_url_domain(str_url), operate_func)
        if support_webp:
            format_func = IMG_FORMAT_FUNCTION.get(domain, '')
            if format_func:
                str_url = '{0}{1}'.format(str_url, format_func)
        if crop:
            crop_func = IMG_CROP_FUNCTION.get(domain, '')
            if crop_func:
                str_url = '{0}{1}'.format(str_url, crop_func.format(width=w, height=w, x=x, y=y))
            thumbnail_func = IMG_THUMBNAIL_FUNCTION.get(domain, '')
            if thumbnail_func:
                str_url = '{0}{1}'.format(str_url, thumbnail_func.format(UPLOAD_IMAGE_FALL_WIDTH))
        return str_url
    else:
        return '{0}{1}{2}'.format(cdn, remove_image_url_domain(str_url), build_cdn_suffix(cdn, UPLOAD_IMAGE_FALL_WIDTH, support_webp))


@append_uploaded_img_ext
def build_upload_image_url(str_url, rotate=0, self_uploaded=0, support_webp=0):
    ext = path.splitext(str_url)[1]
    if ext.lower() == '.gif':
        support_webp = 0
    if self_uploaded:
        cdn = CDN_MXYC_UPLOADED_IMAGE_PREFIX()
    else:
        cdn = CDN_FORUM_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_image_url_domain(str_url), build_cdn_suffix(cdn, UPLOAD_IMAGE_WIDTH, support_webp))


@append_uploaded_img_ext
def build_upload_user_avatar_url(str_url, self_uploaded=0):
    ext = path.splitext(str_url)[1]
    if ext.lower() == '.gif':
        support_webp = 0
    if self_uploaded:
        cdn = CDN_MXYC_UPLOADED_IMAGE_PREFIX()
    else:
        cdn = CDN_FORUM_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_image_url_domain(str_url), build_cdn_suffix(cdn, USER_AVATAR_WIDTH))


@append_uploaded_img_ext
def build_sku_detail_image_url(str_url, support_webp=0):
    cdn = CDN_SKU_ATTACHED_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(str_url), build_cdn_suffix(cdn, SKU_ATTACHED_SIZE, support_webp))


@append_uploaded_img_ext
def build_sku_detail_big_image_url(str_url, support_webp=0):
    cdn = CDN_SKU_DETAIL_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(str_url), build_cdn_suffix(cdn, SKU_DETAIL_SIZE, support_webp))


@append_uploaded_img_ext
def build_re_crop_image_url(str_url, w=0, h=0, x=0, y=0, support_webp=0):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    domain = urlparse(cdn)[1]
    operate_func = IMG_OPERATE_FUNCTION.get(domain, '')
    if not operate_func:
        return '{0}{1}'.format(cdn, remove_first_slash(str_url))
    str_url = '{0}{1}{2}'.format(cdn, remove_first_slash(str_url), operate_func)
    if support_webp:
        format_func = IMG_FORMAT_FUNCTION.get(domain, '')
        if format_func:
            str_url = '{0}{1}'.format(str_url, format_func)
    crop_func = IMG_CROP_FUNCTION.get(domain, '')
    if crop_func:
        str_url = '{0}{1}'.format(str_url, crop_func.format(width=w, height=h, x=x, y=y))
    thumbnail_func = IMG_THUMBNAIL_FUNCTION.get(domain, '')
    if thumbnail_func:
        str_url = '{0}{1}'.format(str_url, thumbnail_func.format(RE_CROP_IMG_WIDTH))
    return str_url


@append_uploaded_img_ext
def build_crawl_small_url(url):
    cdn = CDN_SKU_DETAIL_IMAGE_PREFIX()
    domain = urlparse(cdn)[1]
    operate_func = IMG_OPERATE_FUNCTION.get(domain, '')
    if not operate_func:
        return '{0}{1}'.format(cdn, url)
    str_url = '{0}{1}{2}'.format(cdn, url, operate_func)
    thumbnail_func = IMG_THUMBNAIL_FUNCTION.get(domain, '')
    if thumbnail_func:
        str_url = '{0}{1}'.format(str_url, thumbnail_func.format(CRAWL_SMALL_WIDTH))
    crop_func = IMG_CROP_FUNCTION.get(domain, '')
    if crop_func:
        str_url = '{0}{1}'.format(str_url, crop_func.format(width=CRAWL_SMALL_WIDTH, height=CRAWL_SMALL_WIDTH, x=0, y=0))
    return str_url


@append_uploaded_img_ext
def build_crawl_normal_url(url):
    cdn = CDN_SKU_DETAIL_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, url, build_cdn_suffix(cdn))


@append_uploaded_img_ext
def build_cooperation_image_url(url):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(url)), build_cdn_suffix(cdn))


@append_uploaded_img_ext
def build_banner_topic_image_url(url, support_webp=0):
    return exchange_cdn(url, support_webp)


@append_uploaded_img_ext
def build_banner_tuangou_image_url(url, support_webp=0):
    cdn = CDN_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(url)), build_cdn_suffix(cdn, BANNER_IMAGE_WIDTH, support_webp))


@append_uploaded_img_ext
def build_banner_group_image_url(url, support_webp=0):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(url)), build_cdn_suffix(cdn, BANNER_IMAGE_WIDTH, support_webp))


@append_uploaded_img_ext
def build_banner_worthy_image_url(url, support_webp=0):
    cdn = CDN_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(url)), build_cdn_suffix(cdn, BANNER_IMAGE_WIDTH, support_webp))


@append_uploaded_img_ext
def build_banner_thread_image_url(url, support_webp=0):
    cdn = CDN_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(url)), build_cdn_suffix(cdn, BANNER_IMAGE_WIDTH, support_webp))


@append_uploaded_img_ext
def build_banner_nojump_image_url(url, support_webp=0):
    cdn = CDN_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(url)), build_cdn_suffix(cdn, BANNER_IMAGE_WIDTH, support_webp))


@append_uploaded_img_ext
def build_banner_mall_image_url(url, support_webp=0):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(url)), build_cdn_suffix(cdn, BANNER_IMAGE_WIDTH, support_webp))


@append_uploaded_img_ext
def build_search_recommend_word_image_url(url, support_webp=0):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(url)), build_cdn_suffix(cdn, SEARCH_REVOMMEND_WORD_IMG_WIDTH, support_webp))


@append_uploaded_img_ext
def build_theme_image_url(str_url, width):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(str_url), build_cdn_suffix(cdn, width, quality=100))


def get_crop_path(str_url, crop='_wnormal', suffix='jpg'):
    url_parts = str_url.split('.')
    path = r'.'.join(url_parts[:-1])
    return r'{0}{1}.{2}'.format(path, crop, suffix)


def get_normal_image_path(str_url):
    # return get_crop_path(str_url, '_large')
    return str_url


def get_fall_image_path(str_url):
    # return get_crop_path(str_url, '_gnormal')
    # return get_crop_path(str_url, '_wfall')
    return str_url


def get_item_small_path(str_url):
    if str_url.startswith('http://'):
        return str_url.replace('_.webp', '')
    else:
        # return get_crop_path(str_url, '_small', suffix = 'jpg')
        return str_url


def get_item_normal_path(str_url):
    if str_url.startswith("http://"):
        return str_url.replace('_.webp', '')
    else:
        # return str_url
        # return get_crop_path(str_url, '_wnormal', suffix = 'jpg')
        return str_url


def remove_image_url_domain(str_url):
    if not str_url:
        return ''
    parsed_uri = urlparse(str_url)
    url_domain = '{0}://{1}'.format(parsed_uri[0], parsed_uri[1])
    mystr = ''
    mystr = str_url.replace(url_domain, '')
    return mystr


def remove_first_slash(str_url):
    if str_url.startswith(r'/'):
        return str_url[1:]
    else:
        return str_url


@append_uploaded_img_ext
def build_sku_normal_image_url(str_url, support_webp=0):
    return build_sku_image_url(str_url, SKU_NORMAL_SIZE, support_webp)


@append_uploaded_img_ext
def build_sku_items_image_url(str_url, support_webp=0):
    return build_sku_image_url(str_url, SKU_ITEMS_SIZE, support_webp)


@append_uploaded_img_ext
def build_sku_origin_image_url(str_url, support_webp=0):
    return build_sku_image_url(str_url, SKU_ORIGIN_SIZE, support_webp)


@append_uploaded_img_ext
def build_sku_image_url(str_url, size=STAR_FALL_SIZE, support_webp=0):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(str_url), build_cdn_suffix(cdn, size, support_webp))


@append_uploaded_img_ext
def build_image_url_by_short_url(img_namespace, str_url):
    str_url = get_img_file(img_namespace, str_url)
    return '{0}/{1}'.format(CDN_PREFIX(), str_url)


@append_uploaded_img_ext
def build_CMS_image_url_by_short_url(img_namespace, str_url):
    str_url = get_img_file(img_namespace, str_url)
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}/{1}'.format(cdn, str_url)


@append_uploaded_img_ext
def build_panic_image_url_by_short_url(img_namespace, str_url, size=PANIC_BUYING_WIDTH):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    if str_url.startswith('http'):
        return '{0}{1}'.format(str_url, build_cdn_suffix(cdn, size))
    else:
        str_url = get_img_file(img_namespace, str_url)
        return '{0}/{1}{2}'.format(cdn, str_url, build_cdn_suffix(cdn, size))


@append_uploaded_img_ext
def build_CMS_image_url_by_width(str_url, size=CMS_DEFAULT_WIDTH):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}'.format(str_url, build_cdn_suffix(cdn, size, quality=100))


@append_uploaded_img_ext
def build_category_and_brand_image_url(str_url):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}'.format(cdn, remove_first_slash(remove_image_url_domain(str_url)))


@append_uploaded_img_ext
def build_brand_designer_pic_url(str_url):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}'.format(cdn, remove_first_slash(remove_image_url_domain(str_url)))


@append_uploaded_img_ext
def build_flash_sale_image_url(str_url):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    str_url = get_img_file('tuangou', str_url)
    return '{0}{1}'.format(cdn, remove_first_slash(remove_image_url_domain(str_url)))


@append_uploaded_img_ext
def build_member_sku_image_url(str_url):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}{2}'.format(cdn, remove_first_slash(str_url), build_cdn_suffix(cdn))


@append_uploaded_img_ext
def build_ec_event_icon_image_url(str_url):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}'.format(cdn, remove_first_slash(str_url))


@append_uploaded_img_ext
def build_choiceness_thread_image_url(str_url, namespace):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    str_url = get_img_file(namespace, str_url)
    return '{0}{1}'.format(cdn, remove_first_slash(remove_image_url_domain(str_url)))


@append_uploaded_img_ext
def build_nationalflag_image_url(str_url):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    return '{0}{1}'.format(cdn, remove_image_url_domain(str_url))


@append_uploaded_img_ext
def build_search_keywords_image_url(str_url):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    if str_url.startswith('group'):
        return '{0}{1}'.format(cdn, remove_image_url_domain(str_url))
    else:
        return str_url


@append_uploaded_img_ext
def build_search_keywords_suggest_image_url(str_url):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    if str_url.startswith('group'):
        return '{0}{1}'.format(cdn, remove_image_url_domain(str_url))
    else:
        return str_url


@append_uploaded_img_ext
def build_evaluation_image_url(str_url, namespace, size=EVALUATION_DEFAULT_WIDTH):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    str_url = get_img_file(namespace, str_url)
    return '{0}{1}{2}'.format(cdn, remove_first_slash(remove_image_url_domain(str_url)), build_cdn_suffix(cdn, size, quality=95))


@append_uploaded_img_ext
def build_topic_image_url_new(str_url, namespace, size=EVALUATION_DEFAULT_WIDTH):
    cdn = CDN_FAST_DFS_IMAGE_PREFIX()
    if str_url.startswith('http'):
        str_url = remove_first_slash(remove_image_url_domain(str_url))
    elif not str_url.startswith('group'):
        str_url = get_img_file(namespace, str_url)
    return '{0}{1}{2}'.format(cdn, str_url, build_cdn_suffix(cdn, size, quality=95))


def build_star_user_icon(url):
    return CDN_FAST_DFS_IMAGE_PREFIX() + url
