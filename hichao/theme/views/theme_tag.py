# -*- coding:utf-8 -*-
from hichao.util.statsd_client import statsd
from pyramid.view import (
    view_defaults,
    view_config,
)
from hichao.base.views.view_base import View
from hichao.util.pack_data import pack_data
from hichao.theme.models.tag import get_all_tag_ids,get_tag_by_id
from hichao.theme.models import zuixintag


@view_defaults(route_name='theme_tags')
class tagsView(View):
    def __init__(self, request):
        super(tagsView, self).__init__()
        self.request = request

    @statsd.timer("hichao_backend.r_theme_tags.get")
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        tag_list= {}
        tag_list['items'] = []
        tag_ids = get_all_tag_ids()
        tag = get_tag_by_id(int(zuixintag))
        if tag:
            tag_dict = {}
            tag_dict['action'] = tag.to_ui_action()
            tag_dict['tag'] = tag.get_component_tag()
            tag_dict['description'] = tag.get_component_description()
            tag_list['items'].append(tag_dict)
        for tag_id in tag_ids:
            if tag_id and tag_id != int(zuixintag):
                tag = get_tag_by_id(tag_id)
                if tag:
                    tag_dict = {}
                    tag_dict['action'] = tag.to_ui_action()
                    tag_dict['tag'] = tag.get_component_tag()
                    tag_dict['description'] = tag.get_component_description()
                    tag_list['items'].append(tag_dict)
        return '', tag_list

