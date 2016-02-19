#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.msgcenter.msgcenter.views import MsgCenter

def callback_msgcenter(instance,response):
    instance.assertEqual(response['message'],'')

@auto_generate_test_method
class MsgCenterTests(TestCaseBase):
    view_class = MsgCenter
    request_methods = {
        'get' : {
            'params' : [
                {
                    'category' : '',
                    'flag' : '0',
                },
            ],
            'callback' : callback_msgcenter,
        },
    }

