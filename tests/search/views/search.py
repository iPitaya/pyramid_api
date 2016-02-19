#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.search.views.search import Search

def callback_get(instance,response):
    instance.assertEqual(response['message'],'')

@auto_generate_test_method
class SearchTests(TestCaseBase):
    view_class = Search
    request_methods = {
        'get' : {
            'params' : [
                {
                    'flag':'',
                    'query':'复古印花衬衫',
                    'type':'sku',
                    'crop':'',
                },
            ],
            'callback' : callback_get,
        }
    }

