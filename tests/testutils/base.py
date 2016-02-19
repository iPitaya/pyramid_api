#-*- coding:utf-8 -*-

import functools
import copy
import unittest
from pyramid import testing
import mock

from sqlalchemy.orm.session import Session
from sqlalchemy.orm.query import Query
import transaction

class MockClass(object):
    __mapping_functions__ = [
        (Session,'delete',{'return_value':1}),
        (Session,'add',{'return_value':1}),
        (Query,'update',{'return_value':1}),
        (transaction,'commit',{'return_value':1}),
        (transaction,'abort',{'return_value':1}),
    ]
    #__mapping_functions__ = []

    def _init_mock_function(self):
        _mock_patcher_list = []
        for _mapping_function in self.__class__.__mapping_functions__:
            _class,_function,_attr_dict = _mapping_function
            _patcher = mock.patch.object(_class,_function)
            _mock_patcher_list.append(_patcher)
            _mock_func = _patcher.start()
            for _attr in _attr_dict:
                setattr(_mock_func,_attr,_attr_dict[_attr])
        return _mock_patcher_list

    def _del_mock_function(self):
        for _mock_patcher in self._mock_patchers:
            _mock_patcher.stop()

    def __init__(self):
        self._mock_patchers = []

    def delete_mapping_functions(self):
        self._del_mock_function()

    def bind_mapping_functions(self):
        self._mock_patchers += self._init_mock_function()


class TestCaseBase(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def DummyRequest(self,*args,**kw):
        _dummy_request = functools.partial(testing.DummyRequest,*args,**kw)
        return _dummy_request()

    def getResponseByTestView(self,view_class,view_method,*args,**kw):
        _request = self.DummyRequest(*args,**kw)
        _view = view_class(_request)
        _view_method = getattr(_view,view_method)
        response = _view_method()
        return response

    # view_class = None
    # request_methods = {
    #     'method_name':{ 
    #         'params' : [
    #             {'param_key':'param_value'},
    #         ],
    #         'callback' : def(instance,response):pass,
    #     },
    # }

    view_class = object
    request_methods = {}
    __mock_class__ = MockClass

    @classmethod
    def _run_test_func(cls,instance,method_name,request_param,callback):
        _request = testing.DummyRequest(params=request_param)
        _view = cls.view_class(_request)
        _view_method = getattr(_view,method_name)
        _response = _view_method()
        callback(instance,_response)

    @classmethod
    def _generate_test_method(cls):
        for _method_name in cls.request_methods:
            _request_params_dict = cls.request_methods[_method_name]
            _request_params = _request_params_dict['params']
            _callback = _request_params_dict['callback']
            _mock_mapping_funcs = _request_params_dict.get('mapping_functions',None)
            for _index,_request_param in enumerate(_request_params):
                _generate_test_func_name = 'test_{0}_{1}'.format(_method_name,_index)
                if hasattr(cls,_generate_test_func_name):
                    print '{0} is exsit !!!'.format(_generate_test_func_name)
                else:
                    exec(
'''
def {0}(self):
    print 'method name is {0} --------'
    _mock_class = self.__class__.__mock_class__()
    _mock_class.bind_mapping_functions()
    #print self.__class__.__name__,'|',self.{0}
    request_param = {1}
    method_name = '{2}'
    callback = self.__class__.request_methods[method_name]['callback'];
    self.__class__._run_test_func(self,method_name,request_param,callback)
    _mock_class.delete_mapping_functions()

cls.{0} = {0}
'''.format(_generate_test_func_name,_request_param,_method_name)
                    )

def auto_generate_test_method(cls):
    cls._generate_test_method()
    return cls


#from hichao.forum.views.thread import ThreadsView
#
#def callback_get(instance,response):
#    print response
#    instance.assertEqual(response['message'],'')
#
#@auto_generate_test_method
#class ThreadViewTests(TestCaseBase):
#    view_class = ThreadsView
#    request_methods = {
#        'get' : {
#            'params' : [
#                {
#                    'type' : 'hot',
#                    'flag' : -1,
#                    'gf'   : 'android',
#                    'crop' : '1',
#                },
#            ],
#            'callback' : callback_get,
#        },
#    }
#
#
#unittest.main()

