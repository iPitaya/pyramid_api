#-*-coding=utf-8-*-

import torndb
from hichao.base.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWD
from hichao.forum.models.hot_star_user import (
    get_staruser_ids,
)
from hichao.forum.models.star_user import get_user_id_by_id
from hichao.forum.models.thread import (
    Thread,
    get_ids_by_user_id,
    get_thread_by_id
)
from hichao.forum.models.thread_img import get_thread_img_by_thread_id
from hichao.upload.models.image import get_image_by_id
import time
import logging


#logfile = '/home/quwm/data/log/latest_staruser_info.log'
logfile = '/data/log/api2/latest_staruser_info.log'
logger = logging.getLogger()
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(filename = os.path.join('/data/log/api2/log.log'), level = logging.info)
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.ERROR)


def update_hot_starusers_info():
    try:
        hot_staruser_list_query = get_staruser_ids()
    except:
        raise logger.error('message')
    if len(hot_staruser_list_query) == 0:
        return False
    for staruser_id in hot_staruser_list_query:
        try:
            updata_hot_staruser_info(staruser_id)
        except:
            raise logger.error('message')


def updata_hot_staruser_info(staruser_id):
    logger.error('{0}:BEGIN!'.format(staruser_id))
    num = 0
    thread_ids_list = []
    img_ids_list = []
    try:
        user_id = get_user_id_by_id(staruser_id)
    except Exception, ex:
        raise logger.error(str(ex))
    if user_id:
        user_id = user_id[0]
    else:
        return False
    try:
        thread_ids = get_ids_by_user_id(user_id)
    except Exception, ex:
        raise logger.error(str(ex))
    if len(thread_ids) == 0:
        return False
    for thread_id in thread_ids:
        try:
            thread = get_thread_by_id(thread_id)
        except Exception, ex:
            raise logger.error(str(ex))
        if thread:
            if thread.has_image():
                try:
                    img_id = get_thread_img_by_thread_id(thread_id)
                except Exception, ex:
                    raise logger.error(str(ex))
                if img_id:
                    img_id = img_id[0]
                    img = get_image_by_id(img_id)
                else:
                    continue
                if img:
                    thread_ids_list.append(str(thread_id))
                    img_ids_list.append(str(img_id))
                    num = num + 1
                else:
                    continue
            if num == 3:
                break
    try:
        update_db_hot_staruser_tables(
            thread_ids_list,
            img_ids_list,
            staruser_id)
    except Exception, ex:
        raise logger.error(str(ex))


def update_db_hot_staruser_tables(thread_ids_list, img_ids_list, staruser_id):
    if len(img_ids_list) != 0 and len(thread_ids_list) == len(img_ids_list):
        thread_ids_str = ','.join(thread_ids_list)
        img_ids_str = ','.join(img_ids_list)
    else:
        thread_ids_str = ''
        img_ids_str = ''
    MYSQL_HOST_STR = "{0}:{1}".format(MYSQL_HOST, MYSQL_PORT)
    db_hot_staruser = torndb.Connection(
        MYSQL_HOST_STR,
        "forum",
        MYSQL_USER,
        MYSQL_PASSWD
    )
    mysql = "UPDATE  hot_staruser SET thread_ids = %s,img_ids = %s WHERE staruser_id = %s"
    try:
        db_hot_staruser.execute(
            mysql,
            thread_ids_str,
            img_ids_str,
            staruser_id)
    except Exception, ex:
        raise logger.error(str(ex))
    logger.error('{0}:DONE!'.format(staruser_id))
    print "DONE!", staruser_id


def main():
    while True:
        logger.error('BEGIN')
        time.sleep(300)
        try:
            update_hot_starusers_info()
        except Exception, ex:
            logger.error(str(ex))

if __name__ == "__main__":
    main()
