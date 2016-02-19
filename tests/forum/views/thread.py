#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.forum.views.thread import ThreadView
from hichao.forum.views.thread import ThreadsView

def callback_get(instance,response):
    instance.assertEqual(response['message'],'')

@auto_generate_test_method
class ThreadViewTests(TestCaseBase):
    view_class = ThreadView
    request_methods = {
        'get' : {
            'params' : [
                {},
            ],
            'callback' : callback_get,
        },
        'delete' : {
            'params' : [
                {'subjectId':1},
            ],
            'callback' :callback_get,
        },
    }

@auto_generate_test_method
class ThreadsViewTests(TestCaseBase):
    view_class = ThreadsView
    request_methods = {
        'get' : {
            'params' : [
                 {
                     'type' : 'hot',
                     'flag' : '-1',
                     'gf'   : 'android',
                     'crop' : '1',
                 },
             ],
            'callback' : callback_get,
        },
    }


