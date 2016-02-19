# -*- coding:utf-8 -*-

from pyramid.view import (
    view_defaults,
    view_config,
    )
from hichao.forum.models.recommend_tags import get_recommend_tags
from hichao.base.views.view_base import View
from hichao.util.pack_data import pack_data
from hichao.util.statsd_client import statsd


@view_defaults(route_name = 'new_forum_post_tags')
class TagsView(View):
    def __init__(self, request):
        super(TagsView, self).__init__()
        self.request= request

    @statsd.timer('hichao_backend.r_new_forum_post_tags.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        tags = get_recommend_tags()
        data = {}
        data['tags'] = []
        for tag in tags:
            if tag:
                item = {}
                item['id'] = tag.id
                item['tag'] = tag.tag
                data['tags'].append(item)
        return '', data

