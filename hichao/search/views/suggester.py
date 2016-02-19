# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.search.es import suggester
from hichao.util.pack_data import pack_data
from hichao.util.image_url import build_search_recommend_word_image_url,build_search_keywords_suggest_image_url
from hichao.base.views.view_base import View
from icehole_client.search_manage_client import SearchManageClient
from hichao.collect.models.brand import brand_collect_count
from icehole_client.coflex_agent_client import CoflexAgentClient
from hichao.util.component_builder import build_component_serach_hongren 

SUGGEST_COUNT = 10

@view_defaults(route_name = 'suggester')
class SuggesterView(View):
    def __init__(self, request):
        super(SuggesterView, self).__init__()
        self.request = request

    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        q = self.request.params.get('q', '')
        data_type = self.request.params.get('type', '')
        res = []
        if not q:
            client = SearchManageClient()
            hot_words = client.get_search_recommend_words(limit = 10)
            for word in hot_words:
                dct = {}
                img_url = word.get_image()
                if img_url:
                    dct['follow'] = str(word.get_focus_count())
                    dct['picUrl'] = build_search_recommend_word_image_url(word.get_image())
                    dct['description'] = word.get_description()
                dct['text'] = str(word.get_name())
                res.append(dct)
        elif data_type == 'hongren':
            res_hongren = CoflexAgentClient().suggester(text=q, type_='internet_star')
            if res_hongren:
                res_hongren = res_hongren.get('items',[])
                for item in res_hongren:    
                    com_item = build_component_serach_hongren(item)
                    if not com_item:
                        continue
                    com = {}
                    #不使用component
                    com['text'] = item['name']
                    com['picUrl'] = com_item['component']['userAvatar']
                    com['description'] = item['type']
                    com['id'] = str(item['id'])
                    res.append(com)
        else:
            words = suggester(q, SUGGEST_COUNT)
            for word in words:
                dct = {}
                if word['image_url']:
                    dct['follow'] = str(word['follow'])
                    dct['picUrl'] = build_search_keywords_suggest_image_url(word['image_url'])
                    dct['description'] = word['desc']
                dct['text'] = word['name']
                client = SearchManageClient()
                query = word['name']
                key_word = client.get_special_word(query.encode('utf-8'))
                if key_word:
                    brand_id = key_word.get_brand_id()
                    if brand_id > 0:
                        brand_total = brand_collect_count(int(brand_id), 0)
                        dct['follow'] = str(brand_total)
                    else:
                        dct['follow'] = str(key_word.get_focus_count())
                res.append(dct)
        data = {}
        data['items'] = res
        return '', data

