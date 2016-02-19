# -*- coding:utf-8 -*-

from pyramid.response import Response
import functools
import json
from  distutils.version  import  LooseVersion

def pack_data(func):
    @functools.wraps(func)
    def _(self):
        response = func(self)
        if isinstance(response, Response):
            return response
        message, data = response
        app_api = self.request.params.get('ga', '') 			# generic app api
        data['appApi'] = app_api
        result = {}
        result['message'] = message
        result['data'] = data
        if self.error:
            result['error'] = self.error['error']
            result['errorCode'] = self.error['errorCode']
        var = self.request.params.get('var', '')
        if var:
            return Response(var + '=' + json.dumps(result))
        return result
    return _


def gv_float(gv):
    gv_data=''
    gv_list = str(gv).split('.')
    if len(gv_list) > 2:
        gv_data = gv_list[0] + '.' + gv_list[1] + gv_list[2]
    if gv_data != '':
        gv =  float(gv_data)
    print gv , type(gv)
    return gv

def version_ge(gv1, gv2):   
    '''版本判断大于等于'''
    if not gv1: gv1 = 0
    if not gv2: gv2 = 0
    return LooseVersion(str(gv1)) >= LooseVersion(str(gv2))

def version_gt(gv1, gv2):  
    '''版本判断大于'''
    if not gv1: gv1 = 0
    if not gv2: gv2 = 0
    return LooseVersion(str(gv1)) > LooseVersion(str(gv2))


def version_eq(gv1, gv2):  
    '''版本判断等于'''
    if not gv1: gv1 = 0
    if not gv2: gv2 = 0
    return LooseVersion(str(gv1)) == LooseVersion(str(gv2))
