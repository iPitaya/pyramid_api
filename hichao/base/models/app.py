#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hichao.base.lib.redis import redis_key

REDIS_APP_IDENTIFY = redis_key.AppIdentify('%s-%s')

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

