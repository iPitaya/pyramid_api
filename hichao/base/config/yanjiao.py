# -*- coding:utf-8 -*-
##############################################################################
# MYSQL SECTION

MYSQL_USER = 'api2'
MYSQL_PASSWD = 'CXxY1KMSm5ewYBnfIqxnOtrMy'
MYSQL_HOST = '192.168.1.108'
MYSQL_PORT = '3306'

MYSQL_SLAVE_USER = 'read'
MYSQL_SLAVE_PASSWD = '8bde2bd~92!749#31_2cd0d2*%9'
MYSQL_SLAVE_HOST = '192.168.1.238'
MYSQL_SLAVE_PORT = '3306'

# ECSHOP MYSQL SECTION

ECSHOP_MYSQL_USER = 'shop'
ECSHOP_MYSQL_PASSWD = 'd86&e95%^!66964TD7l9Ch'
ECSHOP_MYSQL_HOST = '192.168.1.139'
ECSHOP_MYSQL_PORT = '3306'

ECSHOP_MYSQL_SLAVE_USER = 'shop'
ECSHOP_MYSQL_SLAVE_PASSWD = 'd86&e95%^!66964TD7l9Ch'
ECSHOP_MYSQL_SLAVE_HOST = '192.168.1.237'
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
stage = os.environ.get('procname') or 'api2_production'
print stage
server_config.from_object('hichao.base.config.redis_conf.'+stage)
REDIS_CACHE_CONFIG_LIST = server_config['REDIS_CACHE_CONFIG_LIST']
USE_LOCAL_CACHE = server_config['USE_LOCAL_CACHE']

#############################################################################
# REDIS SECTION

REDIS_CONFIG = dict(
    host = '192.168.1.137',
    port = 6379,
    db = 0,
    socket_connect_timeout = 4,     # 设置连接超时，单位为秒，可以为小数。
    )

REDIS_SLAVE_CONFIG = dict(
    host = '192.168.1.136',
    port = 6379,
    db = 0,
    socket_connect_timeout = 4,
    )

COLLECTION_REDIS_CONFIG = dict(
    host = '192.168.1.149',
    port = 8004,
    db = 0,
    socket_connect_timeout = 5,
    )

COLLECTION_REDIS_SLAVE_CONFIG = dict(
    #host = '192.168.1.145',
    host = '192.168.1.7',
    port = 8004,
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
        rmq_url ="amqp://admin:@192.168.1.147:5672/%2F",
        #发现 rmq_url 中间出现#会报错
        rmq_pwd = 'pGgEz2V^Gjh#Ol-#-OBjcKJs1~3hh4',
        thread_conf = dict(
            queue_name="exchange_search_online",
            exchange='exchange_search_online',
            routing_key='threads.insert'
        )
    )


SHOP_URL_DOMAIN = 'http://goods.shop.hichao-inc.com'
ORDER_SHOP_URL_DOMAIN = 'http://api.mall.hichao-inc.com'
API2_URL_DOMAIN = 'http://api2.hichao.com'
H5_URL_DOMAIN = 'http://fed.pimg.cn'
WEB_URL_DOMAIN = 'http://www.hichao.com'

