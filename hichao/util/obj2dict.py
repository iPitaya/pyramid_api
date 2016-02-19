# -*- coding:utf-8 -*-

def obj2dict(obj):
    res = {}
    if obj:
        for k, v in obj.__dict__.iteritems():
            res[k] = v
    return res

