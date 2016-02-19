#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hichao.base.config.sku_part import SUFFIX
ZERO, ONE, TWO, THERE, FOUR, FIVE, SIX = 0, 1, 2, 3, 4, 5, 6

N2C = {
    ONE:"周一",
    TWO:"周二",
    THERE:"周三",
    FOUR:"周四",
    FIVE:"周五",
    SIX:"周六",
    ZERO:"周日"
}


if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

