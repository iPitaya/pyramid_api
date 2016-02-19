#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.star.views.star import StarView

def callback_get(instance,response):
    instance.assertEqual(response['message'],'')

@auto_generate_test_method
class StarViewTests(TestCaseBase):
    view_class = StarView
    request_methods = {
        'get' : {
            'params' : [
                {
                    'category' : '本土',
                    'crop' : '1',
                    'flog' : '1',
                },
            ],
            'callback' : callback_get,
        },
    }

