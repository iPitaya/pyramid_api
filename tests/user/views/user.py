#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.user.views.user import UserView
from hichao.user.views.user import CheckUserPermission

def callback_userview_get(instance,response):
    instance.assertEqual(response.status_code,200)

def callback_checkuser_get(instance,response):
    instance.assertEqual(response['message'],'')

@auto_generate_test_method
class UserViewTests(TestCaseBase):
    view_class = UserView
    request_methods = {
        'get' : {
            'params' : [
                {
                    'token' : '',
                },
            ],
            'callback' : callback_userview_get,
        },
        'post' : {
            'params' : [
                {},
            ],
            'callback' :callback_userview_get,
        },
        'delete' : {
            'params' : [
                {},
            ],
            'callback' :callback_userview_get,
        },
    }

@auto_generate_test_method
class CheckUserPermissionTests(TestCaseBase):
    view_class = CheckUserPermission
    request_methods = {
        'get' : {
            'params' : [
                {},
            ],
            'callback' :callback_checkuser_get,
        },
    }

