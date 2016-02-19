#UPLOAD_IMAGE_CALLBACK_URL = 'http://api2.hichao.com/upload_check?'
UPLOAD_IMAGE_CALLBACK_URL = 'http://api2.hichao.com/upload_check'
QINIU_UPLOAD_IMAGE_CALLBACK_URL = 'http://api2.hichao.com/qiniu_img_upload'
QINIU_ACCESS_KEY = "Z3deq1tMDYEUnB01zQrq77vLb4QqkCbTCVbNAYMw"
QINIU_SECRET_KEY = "jCietDVqwPnq-AwhriPJbKyhuo1b9t682oPtYO8z"
QINIU_BUCKET_NAME = 'mxycforum'
QINIU_IMAGE_URL = 'http://%s.u.qiniudn.com/'%QINIU_BUCKET_NAME

from hichao.base.config import MYSQL_USER,MYSQL_PASSWD,MYSQL_HOST, MYSQL_PORT
from hichao.base.config import MYSQL_SLAVE_USER, MYSQL_SLAVE_PASSWD, MYSQL_SLAVE_HOST, MYSQL_SLAVE_PORT

SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, 'upload')
SQLALCHEMY_SLAVE_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (MYSQL_SLAVE_USER, MYSQL_SLAVE_PASSWD, MYSQL_SLAVE_HOST, MYSQL_SLAVE_PORT, 'upload')

