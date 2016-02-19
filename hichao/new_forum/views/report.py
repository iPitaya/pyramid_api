# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.util.pack_data import pack_data
from hichao.forum.models.report import add_report
from hichao.cache import get_cache_client
from hichao.util.statsd_client import statsd

import datetime
import md5

cache_client = get_cache_client()

@view_defaults(route_name = 'report')
class ReportView(View):
    def __init__(self, request):
        super(ReportView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_report.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        from_uid = self.user_id
        if self.user_id == -1:
            self.error['error'] = 'User info error.'
            self.error['errorCode'] = '10004'
            return u'登录后才可以举报哦~', {}
        if self.user_id == -2:
            self.error['error'] = 'User info expired.'
            self.error['errorCode'] = '20002'
            return u'登录信息过期了，请重新登录一下吧~', {}
        if self.user_id < 1 or too_fast_report(from_uid):
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return u'不要恶意举报哦～', {}
        _type = self.request.params.get('type', '')
        item_id = self.request.params.get('item_id', '')
        if not _type or not item_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10001'
            return '', {}
        comment_id = self.request.params.get('comment_id', '')
        content = self.request.params.get('content', '')
        ip = self.request.environ.get('HTTP_X_REAL_IP', '')
        if not ip: ip = self.request.client_addr
        report_type = 'thread'
        report_id = 0
        if comment_id:
            report_type = _type + '_comment'
            report_id = comment_id
        else:
            report_type = _type
            report_id = item_id
        res = add_report(report_type, report_id, datetime.datetime.now(), content, from_uid, ip)
        if not res:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
        return '', {}

def too_fast_report(user_id):
    mstr = 'user_report_times_' + str(user_id)
    key = md5.new(mstr).hexdigest()
    res = cache_client.get(key)
    if res is not None:
        res = int(res)
        if res > 5: return True
        else:
            cache_client.setex(key, 60, res + 1)
            return False
    else:
        cache_client.setex(key, 60, 1)
        return False

