#-*-coding=utf-8-*-

from hichao.base.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWD
from hichao.forum.models.db import rdbsession_generator
from hichao.comment.models.db import rdbsession_generator as dbsession_generator
from hichao.forum.models.star_user import get_user_id_by_id
from hichao.forum.models.thread import (
    Thread,
)
from hichao.comment.models.sub_thread import(
    SubThread,
    )

from hichao.base.lib.redis import redis_slave
from hichao.forum.models.pv import (
    tag_thread_count_incr,
    tag_comment_count_incr,
    REDIS_TAG_THREAD_COUNT,
    REDIS_TAG_COMMENT_COUNT,
    )

from sqlalchemy import func
import time
import logging


logfile = 'tag_thread_comment_count_info.log'
logger = logging.getLogger()
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
PER_PAGE = 2000

def get_thread_tags(offset, limit):
    DBSession = rdbsession_generator()
    ids_tags = DBSession.query(Thread.id, Thread.tags).offset(offset).limit(limit)
    DBSession.close()
    return ids_tags

def get_comment_count_by_thread_id(thread_id):
    DBSession = dbsession_generator()
    count = DBSession.query(func.count(SubThread.id)).filter(SubThread.item_id ==thread_id).first()[0]
    DBSession.close() 
    return count

def update_tag_thread_comment_count():
        offset = 0
        flag = True
        limit = PER_PAGE
        tag_thread_count = {}
        tag_comment_count = {}
        while flag:
            ids_tags = get_thread_tags(offset, limit);
            curr_count = 0
            for id_tag in ids_tags:
                curr_count = curr_count + 1
                thread_id, tag_ids = id_tag
                tag_ids = tag_ids.split(',')
                thread_comment_count = get_comment_count_by_thread_id(thread_id)
                print thread_id
                for tag_id in tag_ids:
                    if tag_id in tag_thread_count.keys():
                        thread_count = tag_thread_count.get(tag_id)
                        tag_thread_count[tag_id] = thread_count + 1
                    else:
                        tag_thread_count[tag_id] = 1
                    if tag_id in tag_comment_count.keys():
                        comment_count = tag_comment_count.get(tag_id)
                        tag_comment_count[tag_id] = comment_count + thread_comment_count
                    else:
                        tag_comment_count[tag_id] = thread_comment_count
 
            offset = offset + curr_count
            if curr_count < PER_PAGE:
                flag = False
        for tag_id, count in tag_thread_count.items():
            redis_slave.hset(REDIS_TAG_THREAD_COUNT,tag_id,count)
        for tag_id, count in tag_comment_count.items():
            redis_slave.hset(REDIS_TAG_COMMENT_COUNT,tag_id,count)

if __name__ == "__main__":
    update_tag_thread_comment_count()
