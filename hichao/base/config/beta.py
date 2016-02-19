# -*- coding:utf-8 -*-
##############################################################################
# MYSQL SECTION

MYSQL_USER = 'api2'
MYSQL_PASSWD = 'CXxY1KMSm5ewYBnfIqxnOtrMy'
MYSQL_HOST = '192.168.1.20'
MYSQL_PORT = '3306'

MYSQL_SLAVE_USER = 'api2'
MYSQL_SLAVE_PASSWD = 'CXxY1KMSm5ewYBnfIqxnOtrMy'
MYSQL_SLAVE_HOST = '192.168.1.20'
MYSQL_SLAVE_PORT = '3306'

# ECSHOP MYSQL SECTION

ECSHOP_MYSQL_USER = 'dev_b2c'
ECSHOP_MYSQL_PASSWD = 'dev_b2c_pwd'
ECSHOP_MYSQL_HOST = '192.168.1.20'
ECSHOP_MYSQL_PORT = '3306'

ECSHOP_MYSQL_SLAVE_USER = 'dev_b2c'
ECSHOP_MYSQL_SLAVE_PASSWD = 'dev_b2c_pwd'
ECSHOP_MYSQL_SLAVE_HOST = '192.168.1.20'
ECSHOP_MYSQL_SLAVE_PORT = '3306'

# TEST ECSHOP MYSQL SECTION

TEST_ECSHOP_MYSQL_USER = 'dev_b2c'
TEST_ECSHOP_MYSQL_PASSWD = 'dev_b2c_pwd'
TEST_ECSHOP_MYSQL_HOST = '192.168.1.20'
TEST_ECSHOP_MYSQL_PORT = '3306'

# BETA ECSHOP MYSQL SECTION

BETA_ECSHOP_MYSQL_USER = 'beta'
BETA_ECSHOP_MYSQL_PASSWD = 'f0cf2a92516045024a0c99147b28f05b'
BETA_ECSHOP_MYSQL_HOST = '192.168.1.16'
BETA_ECSHOP_MYSQL_PORT = '3306'


import os
import sys
from hichao.hichao_misc.utils import Config

server_config = Config(os.path.dirname(os.path.abspath(__file__)))
stage = os.environ.get('procname') or 'api2_beta'
print stage
server_config.from_object('hichao.base.config.redis_conf.'+stage)
REDIS_CACHE_CONFIG_LIST = server_config['REDIS_CACHE_CONFIG_LIST']
USE_LOCAL_CACHE = server_config['USE_LOCAL_CACHE']

#############################################################################
# REDIS SECTION

REDIS_CONFIG = dict(
    host = '192.168.1.222',
    port = 5555,
    db = 0,
    socket_connect_timeout = 4,     # 设置连接超时，单位为秒，可以为小数。
    )

REDIS_SLAVE_CONFIG = dict(
    host = '192.168.1.222',
    port = 5555,
    db = 0,
    socket_connect_timeout = 4,
    )

COLLECTION_REDIS_CONFIG = dict(
    host = '192.168.1.222',
    port = 5555,
    db = 0,
    socket_connect_timeout = 5,
    )

COLLECTION_REDIS_SLAVE_CONFIG = dict(
    #host = '192.168.1.145',
    host = '192.168.1.222',
    port = 5555,
    db = 0,
    socket_connect_timeout = 5,
    )

SHORTY_REDIS_CONF = dict(
    host = '192.168.1.146',
    port = 6380,
    db = 0,
    socket_connect_timeout = 1,
    socket_timeout = 0.02,
    )

DEVICE_REDIS_CONFIG = dict(
    host = '192.168.1.137',
    port = 6604,
    db = 0,
    socket_connect_timeout = 1,
    socket_timeout = 1,
    )

CELERY_BROKER_URL = 'redis://192.168.1.146:6380/0'

RABBITMQ_CONF = dict(
        rmq_url ='amqp://admin:admin@192.168.1.222:5672/%2F',
        thread_conf = dict(
            queue_name="exchange_search_dev",
            exchange='exchange_search_dev',
            routing_key='threads.insert'
        )
    )


SHOP_URL_DOMAIN = 'http://dev.goods.shop.hichao.com'
ORDER_SHOP_URL_DOMAIN = 'http://dev.api.mall.hichao.com'
API2_URL_DOMAIN = 'http://api.beta.hichao.com'
H5_URL_DOMAIN = 'http://fed.dev.pimg.cn'
WEB_URL_DOMAIN = 'http://dev.hichao.com'

