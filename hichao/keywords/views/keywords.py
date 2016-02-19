# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.keywords.models.keywords import (
        get_hot_words,
        get_keyword_list,
        sort_keyword_list,
        build_keyword_list,
        )
from hichao.keywords.models.hot_words import get_hot_words as get_find_words
from hichao.keywords.models.hot_words import (
        get_last_querys_id_by_type,
        get_querys_by_id,
        rebuild_hot_querys,
        rebuild_item_categorys,
        )
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        )
from hichao.base.views.view_base import View
from hichao.topic.models.topic import get_more_app_list
from hichao.util import xpinyin
from hichao.util.statsd_client import statsd

Pinyin = xpinyin.Pinyin()

@view_defaults(route_name = 'keywords')
class Keywords(View):
    def __init__(self, request):
        super(Keywords, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_keywords.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        platform = self.request.params.get('gf', 'iphone')
        data = {}
        data['hot'] = get_find_words()
        com = {}
        com['resultMode'] = 'sku'
        com['moreType'] = 'drop'
        com['title'] = u'女生必备应用'
        com['items'] = get_more_app_list(platform)
        data['hot'].append(com)
        data['stars'] = get_hot_words('star')
        data['words'] = get_hot_words('keywords')
        return '', data

@view_defaults(route_name = 'search_list')
class SearchList(View):
    def __init__(self, request):
        super(SearchList, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_search_list.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        data = {}
        list_type = self.request.params.get('list_type', 'star')
        if list_type != 'star':
            self.error['errorCode'] = '10001'
            self.error['error'] = 'Arguments error.'
            return '', data
        gv = self.request.params.get('gv', '')
        #if gv: gv = gv_float(gv)
        gf = self.request.params.get('gf', '')
        lite_action = 0
        if (version_ge(gv, 5.2) and gf == 'iphone') or (version_ge(gv, 60) and gf == 'android'):
            lite_action = 1
        data['list'] = build_keyword_list(list_type, lite_action)
        return '', data

@view_defaults(route_name = 'hotwords')
class HotWordsView(View):
    def __init__(self, request):
        super(HotWordsView, self).__init__()
        self.request = request
        self.query_type = {'hot':'hotquery', 'item':'itemcategory'}

    @statsd.timer('hichao_backend.r_hotwords.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        version = self.request.params.get('version', '')
        version = (version and [int(version),] or [0,])[0]
        _type = self.request.params.get('type', 'hot')
        _type = self.query_type.get(_type, self.query_type['hot'])
        last_version = int(get_last_querys_id_by_type(_type))
        if version == last_version: return '', {}

        data = {}
        values = []
        querys = get_querys_by_id(last_version)
        if not querys: return '', {}
        querys = eval(querys)
        if not querys: return '', {}

        method = _type == 'hotquery' and rebuild_hot_querys or rebuild_item_categorys
        querys = _type == 'hotquery' and querys[0]['items'] or querys
        if _type == 'itemcategory' and len(querys) > 0:
            querys[0]['items'] = querys[0]['items'][0:12]
            querys[-1]['items'] = querys[-1]['items'][0:12]
        for query in querys: values.append(method(query))

        words = []
        if _type == 'itemcategory':
            for query in querys:
                for item in query['items']:
                    word = self.build_word_init(item['query'].decode('utf-8'))
                    words.append(word)
        data['querys'] = values
        data['words'] = words
        data['version'] = str(last_version)
        return '', data

    def build_word_init(self, word):
        com = {}
        com['c'] = '0'
        com['fw'] = Pinyin.get_initials(word)
        com['pic'] = ''
        com['n'] = word
        com['aw'] = Pinyin.get_pinyin(word)
        com['type'] = 'searchWord'
        return com

