from hichao.base.config import MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT

SQLALCHEMY_CONF_URL = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8"\
                        %(MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'third')


#FAKE_TOKEN_URL = 'http://shanshui.me/connect/auth2/token'
FAKE_TOKEN_URL = 'http://haobao.com/connect/auth2/token'
