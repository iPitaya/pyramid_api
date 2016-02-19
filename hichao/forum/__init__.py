# -*- coding:utf-8 -*-

from hichao.base.config import CDN_PREFIX

class THREAD_STATUS():
    class TYPE():
        NORMAL = 1      # 正常
        DELETED = 0     # 已删除
        CENSORING = 2   # 审核中
        UNAPPROVED = 3  # 未通过审核

FORUM_ALL = {
            'id':'-1',
            'name':u'全部',
            'picUrl':CDN_PREFIX() + 'images/images/20140529/893ebe23-c9a6-48b6-bc52-b1ae2b7d6bd4.png',
        }

