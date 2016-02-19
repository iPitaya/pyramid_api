#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time, mktime, strptime, gmtime, timezone

ONE_HOUR_SECOND = 60 * 60
ONE_DAY_SECOND = 60 * 60 * 24
ONE_DAY_MINUTE = 60 * 24


def today_days():
    return int((time() - timezone) // ONE_DAY_SECOND)

def day2days(day):
    return (int(float(day) - timezone) // ONE_DAY_SECOND)

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

