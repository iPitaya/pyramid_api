#-*- coding:utf-8 -*-

from tests.testutils.base import TestCaseBase
from tests.testutils.base import auto_generate_test_method

from hichao.topic.views.topic import TopicsView
from hichao.topic.views.topic import TopicView
from hichao.topic.views.topic import MoreAppsView
from hichao.topic.views.topic import TopicChecker

def callback_get(instance,response):
    instance.assertEqual(response['message'],'')

@auto_generate_test_method
class TopicsViewTests(TestCaseBase):
    view_class = TopicsView
    request_methods = {
        'get' : {
            'params' : [
                {
                    'flag':'',
                    'category':''
                },
            ],
            'callback' : callback_get,
        }
    }

@auto_generate_test_method
class TopicViewTests(TestCaseBase):
    view_class = TopicView
    request_methods = {
        'get' : {
            'params' : [
                {},
            ],
            'callback' : callback_get,
        }
    }

@auto_generate_test_method
class MoreAppsViewTests(TestCaseBase):
    view_class = MoreAppsView
    request_methods = {
        'get' : {
            'params' : [
                {},
            ],
            'callback' : callback_get,
        }
    }

@auto_generate_test_method
class TopicCheckerTests(TestCaseBase):
    view_class = TopicChecker
    request_methods = {
        'get' : {
            'params' : [
                {
                    'topic_id' : 2920
                },
            ],
            'callback' : callback_get,
        }
    }

