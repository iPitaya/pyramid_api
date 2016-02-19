from hichao.base.config import MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT

from hichao.base.config import MYSQL_SLAVE_USER, MYSQL_SLAVE_PASSWD, MYSQL_SLAVE_HOST, MYSQL_SLAVE_PORT

SQLALCHEMY_CONF_URL = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8"\
                        %(MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'forum')


SQLALCHEMY_SLAVE_CONF_URL = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8"\
                        %(MYSQL_SLAVE_USER, MYSQL_SLAVE_PASSWD, MYSQL_SLAVE_HOST, MYSQL_SLAVE_PORT, 'forum')

