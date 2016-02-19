# -*- coding=utf-8 -*-

from hichao.base.config import (
        MYSQL_SLAVE_USER,
        MYSQL_SLAVE_PASSWD,
        MYSQL_SLAVE_HOST,
        MYSQL_SLAVE_PORT,
        ECSHOP_MYSQL_USER,
        ECSHOP_MYSQL_PASSWD,
        ECSHOP_MYSQL_HOST,
        ECSHOP_MYSQL_PORT,
        )

SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (ECSHOP_MYSQL_USER, ECSHOP_MYSQL_PASSWD, ECSHOP_MYSQL_HOST, ECSHOP_MYSQL_PORT, 'shop')
ACTIVITY_SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (MYSQL_SLAVE_USER, MYSQL_SLAVE_PASSWD, MYSQL_SLAVE_HOST, MYSQL_SLAVE_PORT, 'wodfan')

