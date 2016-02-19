#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.banner.views.banner import Banner

def callback_get(instance,response):
    instance.assertEqual(response['message'],'')

@auto_generate_test_method
class BannerTests(TestCaseBase):
    view_class = Banner
    request_methods = {
        'get' : {
            'params' : [
                {},
            ],
            'callback' : callback_get,
        }
    }

