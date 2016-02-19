#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.sku.views.sku import SkuImgView

def callback_get(instance,response):
    instance.assertEqual(response['message'],'')

@auto_generate_test_method
class SkuImgViewTests(TestCaseBase):
    view_class = SkuImgView
    request_methods = {
        'get' : {
            'params' : [
                {
                    'source' : 'tmall',
                    'source_id' : '37333533660',
                },
            ],
            'callback' : callback_get,
        },
    }

