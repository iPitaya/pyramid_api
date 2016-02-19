# -*- coding:utf-8 -*-
from hichao.base.config import MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT
from hichao.base.config import POINT_MYSQL_USER, POINT_MYSQL_PASSWD, POINT_MYSQL_HOST, POINT_MYSQL_PORT

POINT_SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (POINT_MYSQL_USER, POINT_MYSQL_PASSWD,
    POINT_MYSQL_HOST, POINT_MYSQL_PORT, 'points')
SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
    MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'points')
