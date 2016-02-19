# -*- coding:utf-8 -*-

import functools
from hichao.util.pack_data import version_eq

def patch_ios_description_with_forum_v_3_3(func):
    '''
    只有ios3.3版本中，帖子列表页，描述返回版块名称；其它版本均不返回。
    '''
    @functools.wraps(func)
    def _(self):
        res = func(self)
        platform = self.request.params.get('gf', '')
        version = self.request.params.get('gv', '')
        if platform == 'iphone' and version_eq(version, '3.3') and res.has_key('data'):
            for item in res['data']['items']:
                if item['component'].has_key('forum'):
                    item['component']['description'] = item['component']['forum'] + item['component']['description']
        return res
    return _

