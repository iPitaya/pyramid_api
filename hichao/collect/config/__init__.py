from hichao.base.config import MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT

from hichao.base.config import SYNC_MYSQL_USER, SYNC_MYSQL_PASSWD, SYNC_MYSQL_HOST, SYNC_MYSQL_PORT

SQLALCHEMY_CONF_URL = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8"\
                        %(MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'wodfan')


SYNC_SQLALCHEMY_CONF_URL = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8"\
                        %(SYNC_MYSQL_USER, SYNC_MYSQL_PASSWD, SYNC_MYSQL_HOST, SYNC_MYSQL_PORT, 'collection')
