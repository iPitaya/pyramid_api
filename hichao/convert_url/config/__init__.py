# -*- coding:utf-8 -*-
from hichao.base.config import MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT

DB_NAME = 'taobaoke'

SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, DB_NAME)

