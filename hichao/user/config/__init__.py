from hichao.base.config import MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT
from hichao.base.config import MYSQL_SLAVE_USER, MYSQL_SLAVE_PASSWD, MYSQL_SLAVE_HOST, MYSQL_SLAVE_PORT
from hichao.base.config import UDID_MYSQL_USER, UDID_MYSQL_PASSWD, UDID_MYSQL_HOST, UDID_MYSQL_PORT

SQLALCHEMY_CONF_URL = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4"\
                        %(MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'wodfan')

SQLALCHEMY_SLAVE_CONF_URL = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4"\
                        %(MYSQL_SLAVE_USER, MYSQL_SLAVE_PASSWD, MYSQL_SLAVE_HOST, MYSQL_SLAVE_PORT, 'wodfan')

UDID_SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4'\
                        %(UDID_MYSQL_USER, UDID_MYSQL_PASSWD, UDID_MYSQL_HOST, UDID_MYSQL_PORT, 'wodfan')

DEVICE_SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4'\
                        %(MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'device')

DEVICE_SQLALCHEMY_SLAVE_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4'\
                        %(MYSQL_SLAVE_USER, MYSQL_SLAVE_PASSWD, MYSQL_SLAVE_HOST, MYSQL_SLAVE_PORT, 'device')

TEL_REGEXP = r"(13|14|15|17|18)\d{9}$"
PASSWORD_MIN_SIZE = 6
PASSWORD_MAX_SIZE = 32
SECRET_KEY = '93f5c2eab7ba9b5ac39bac1b927f9101'
SECRET_KEY_NOTICE = '22927b036b271bad63d7218671e85e4a'
USER_REGISTER_TEMPLATE = 'user_register'
FIND_PASSWORD_TEMPLATE = 'find_password'
