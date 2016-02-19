# -*- coding:utf-8 -*- 

from hichao.base.config import MYSQL_MAX_TIMESTAMP
from hichao.forum.models.thread import get_thread_ids
from hichao.util.object_builder import build_thread_by_id
from hichao.forum.models.top_thread import get_all_top_thread_ids
import datetime
import time

MAX_PAGE = 30
now = datetime.datetime.now

def main():
    print '=========================================================='
    print 'begin at:{0}'.format(now())
    flag = MYSQL_MAX_TIMESTAMP
    num = 20
    tp = 0
    crop = 1
    not_crop = 0
    more_img = 1
    page = 1
    top_ids = get_all_top_thread_ids(tp == 0 and -2 or tp)
    for id in top_ids:
        build_thread_by_id(id, not_crop, more_img)
        build_thread_by_id(id, crop, more_img)
    print 'top threads cached.'
    while page <= MAX_PAGE:
        ids = get_thread_ids(flag, num, tp)
        for id in ids:
            build_thread_by_id(id, not_crop, more_img)
            com = build_thread_by_id(id, crop, more_img)
            if com:
                flag = com['uts']
        #print 'latest offset {0} set cache done.'.format(page * num)
        page = page + 1
    print 'latest {0} done, at:{1}'.format(MAX_PAGE * num, now())


if __name__ == '__main__':
    main()

