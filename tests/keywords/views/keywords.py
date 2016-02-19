#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.keywords.views.keywords import Keywords
from hichao.keywords.views.keywords import SearchList
from hichao.keywords.views.keywords import HotWordsView

def callback_get(instance,response):
    instance.assertEqual(response['message'],'')

@auto_generate_test_method
class KeywordsTests(TestCaseBase):
    view_class = Keywords
    request_methods = {
        'get' : {
            'params' : [
                {'gf':'iphone'},
            ],
            'callback' : callback_get,
        }
    }

@auto_generate_test_method
class SearchListTests(TestCaseBase):
    view_class = SearchList
    request_methods = {
        'get' : {
            'params' : [
                {'list_type':'star'},
            ],
            'callback' : callback_get,
        }
    }

@auto_generate_test_method
class HotWordsViewTests(TestCaseBase):
    view_class = HotWordsView
    request_methods = {
        'get' : {
            'params' : [
                {
                    'version':'',
                    'type':'hot',
                },
            ],
            'callback' : callback_get,
        }
    }

