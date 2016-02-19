# -*- coding:utf-8 -*-

from statsd import StatsClient
from functools import wraps

statsd = StatsClient("192.168.1.89", 8125)

def timeit(prefix = ''):
    def _(func):
        @statsd.timer('{0}.{1}'.format(prefix, func.__name__))
        @wraps(func)
        def __(*args, **kw):
            return func(*args, **kw)
        return __
    return _

