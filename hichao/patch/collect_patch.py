# -*- coding:utf-8 -*-

import functools
from hichao.util.pack_data import version_eq

def patch_ios_collect_v_3_3(func):
    '''
    解决 ios 3.3 中收藏没有读取返回结构里data下的flag，而是读了data平级的flag，导致无法读到下一页的问题。
    解决方法 在data平级也加上一个flag，与data['flag']相同。
    '''
    @functools.wraps(func)
    def _(self):
        data = func(self)
        platform = self.request.params.get('gf', '')
        version = self.request.params.get('gv', '')
        if platform == 'iphone' and version_eq(version, '3.3') and data.has_key('data') and data['data'].has_key('flag'):
            data['flag'] = data['data']['flag']
        return data
    return _
        

