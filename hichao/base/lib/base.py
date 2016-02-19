# -*- coding: utf-8 -*-
from webob.exc import HTTPException, status_map


if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

