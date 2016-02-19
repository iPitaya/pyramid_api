#!/usr/bin/env python
# -*- coding: utf-8 -*-
import qiniu.conf

qiniu.conf.ACCESS_KEY = "Z3deq1tMDYEUnB01zQrq77vLb4QqkCbTCVbNAYMw"
qiniu.conf.SECRET_KEY = "jCietDVqwPnq-AwhriPJbKyhuo1b9t682oPtYO8z"

import qiniu.rs

QiNiu = qiniu.rs




if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
