# -*- coding:utf-8 -*-

from hichao.base.config import MYSQL_USER,MYSQL_PASSWD,MYSQL_HOST, MYSQL_PORT

from hichao.base.config import READONLY_MYSQL_USER,READONLY_MYSQL_PASSWD,READONLY_MYSQL_HOST, READONLY_MYSQL_PORT


SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'wodfan')

READONLY_SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (READONLY_MYSQL_USER, READONLY_MYSQL_PASSWD,
        READONLY_MYSQL_HOST, READONLY_MYSQL_PORT, 'wodfan')

