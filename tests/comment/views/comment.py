#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.comment.views.comment import CommentView

def callback_get(instance,response):
    #instance.assertIsInstance(response,dict)
    pass

@auto_generate_test_method
class CommentViewTests(TestCaseBase):
    view_class = CommentView
    request_methods = {
        'get' : {
            'params' : [
                {
                    'flag':'',
                    'id':'',
                    'rtf':'',
                    'asc':'',
                    'gf':'',
                    'gv':'',
                },
            ],
            'callback' : callback_get,
        },
        'post' : {
            'params' : [
                {
                    'content':'',
                    'id':'',
                    'comment_id':'',
                },
            ],
            'callback' : callback_get,
        },
        'delete' : {
            'params' : [
                {
                    'comment_id':'',
                },
            ],
            'callback' : callback_get,
        }
    }

