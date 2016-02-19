#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.feedback.views.feedback import Feedback

def callback_get(instance,response):
    instance.assertNotEqual(response['message'],'')

@auto_generate_test_method
class FeedbackTests(TestCaseBase):
    view_class = Feedback
    request_methods = {
        'post' : {
            'params' : [
                {
                    'gf' : 'unknow',
                    'gn' : 'unknow',
                    'gc' : 'unknow',
                    'gv' : 'unknow',
                    'email' : '',
                    'feedback' : '',
                },
            ],
            'callback' : callback_get,
        },
    }
