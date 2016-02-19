# -*- coding:utf-8 -*-

from hichao.base.config import (
        MYSQL_USER,
        MYSQL_HOST,
        MYSQL_PASSWD,
        MYSQL_PORT,
        MYSQL_SLAVE_USER,
        MYSQL_SLAVE_HOST,
        MYSQL_SLAVE_PASSWD,
        MYSQL_SLAVE_PORT,
        )

MYSQL_DBNAME = 'forum'

SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % (MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, MYSQL_DBNAME)
SQLALCHEMY_SLAVE_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % (MYSQL_SLAVE_USER, MYSQL_SLAVE_PASSWD, MYSQL_SLAVE_HOST, MYSQL_SLAVE_PORT, MYSQL_DBNAME)

SQLALCHEMY_THREADLOCAL_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % (MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'qianfang')

