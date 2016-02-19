# -*- coding:utf-8 -*-

from pyramid.view import (
    view_defaults,
    view_config,
    )
from hichao.base.views.view_base import View
from hichao.app.views.oauth2 import check_permission
from hichao.util.pack_data import pack_data
from hichao.feedback.models.feedback import add_feedback
from hichao.util.statsd_client import statsd
import time

@view_defaults(route_name = 'feedback')
class Feedback(View):
    def __init__(self, request):
        super(Feedback, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_feedback.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        user_id = self.user_id
        platform = self.request.params.get('gf', 'unknow')
        app_name = self.request.params.get('gn', 'unknow')
        app_channel = self.request.params.get('gc', 'unknow')
        version = self.request.params.get('gv', 'unknow')
        email = self.request.params.get('email', '')
        feedback = self.request.params.get('feedback', '')
        publish_date = time.time()
        re = add_feedback(user_id, platform, app_name, app_channel, version,
            email, feedback, publish_date)
        if re == 1:
            return u'您的意见我们已经收到，谢谢您的反馈。', {}
        elif re == 0:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return u'出错了哦。。反馈失败了。', {}
