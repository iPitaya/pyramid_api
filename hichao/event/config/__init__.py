# -*- coding=utf-8 -*-

from hichao.base.config import (
        MYSQL_USER,
        MYSQL_PASSWD,
        MYSQL_HOST,
        MYSQL_PORT,
        ECSHOP_MYSQL_USER,
        ECSHOP_MYSQL_PASSWD,
        ECSHOP_MYSQL_HOST,
        ECSHOP_MYSQL_PORT,
        ECSHOP_MYSQL_SLAVE_USER,
        ECSHOP_MYSQL_SLAVE_PASSWD,
        ECSHOP_MYSQL_SLAVE_HOST,
        ECSHOP_MYSQL_SLAVE_PORT,
    )

SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'wodfan')
SQLALCHEMY_CONF_SHOP_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
                                            ECSHOP_MYSQL_USER,
                                            ECSHOP_MYSQL_PASSWD,
                                            ECSHOP_MYSQL_HOST,
                                            ECSHOP_MYSQL_PORT,
                                            'shop')
SQLALCHEMY_CONF_SLAVE_SHOP_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
                                            ECSHOP_MYSQL_SLAVE_USER,
                                            ECSHOP_MYSQL_SLAVE_PASSWD,
                                            ECSHOP_MYSQL_SLAVE_HOST,
                                            ECSHOP_MYSQL_SLAVE_PORT,
                                            'shop')
