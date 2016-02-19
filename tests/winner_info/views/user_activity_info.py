#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.winner_info.views.user_activity_info import UserActivityInfoView

def callback_useractivityinfoview(instance,response):
    instance.assertEqual(response['message'],'')

@auto_generate_test_method
class UserActivityInfoViewTests(TestCaseBase):
    view_class = UserActivityInfoView
    request_methods = {
        'post' : {
            'params' : [
                {
                    'name':'',
                    'cellphone':'',
                    'email':'',
                    'address':'',
                    'attachment':'',
                    'type_id':'',
                    'type':'topic',
                },
            ],
            'callback' : callback_useractivityinfoview,
        },
    }
