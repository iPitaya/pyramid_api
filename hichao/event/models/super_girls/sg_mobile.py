# -*- coding:utf-8 -*-

from sqlalchemy import (
    Column,
    INTEGER,
    TIMESTAMP,
    VARCHAR,
    )
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.exc import IntegrityError
from hichao.user.models.user import get_user_by_mobile_num
from hichao.event.models.super_girls.sg_mgtv_code import SuperGirlsCode
from hichao.event.models.db import (
    Base,
    dbsession_generator_write,
    dbsession_generator,
    )
from icehole_client.message_client import EventClient
import time
import datetime
import logging

logger = logging.getLogger('mgtv')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('/data/log/api2/mgtv_sg_code.log')
fh.setLevel(logging.INFO)
logger.addHandler(fh)

class SuperGirlsActMobile(Base):
    __tablename__ = 'sg_mobile'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    mobile = Column(VARCHAR(32), unique = True, nullable = False, index = True)
    sg_code = Column(VARCHAR(255), unique = True, nullable = True, index = True)
    user_id = Column(INTEGER, nullable = True)
    sent = Column(TINYINT, nullable = False, default = 0)
    
    def __init__(self, mobile):
        self.mobile = mobile

def add_super_girls_act_mobile(mobile):
    mb = SuperGirlsActMobile(mobile)
    try:
        sess = dbsession_generator_write()
        sess.add(mb)
        sess.commit()
        return 1
    except IntegrityError:
        sess.rollback()
        return -1
    except Exception, ex:
        print Exception, ex
        logger.info(str(ex))
        sess.rollback()
        return 0
    finally:
        sess.close()

def get_super_girls_act_mobile(mobile):
    try:
        sess = dbsession_generator()
        user = sess.query(SuperGirlsActMobile).filter(SuperGirlsActMobile.mobile == mobile).first()
        return user
    except Exception, ex:
        print Exception, ex
        return None
    finally:
        sess.close()

def sg_bind_code(user_id, mobile):
    '''
        returns:
            0:      关联失败
            code:   关联成功
            2:      兑换码已经领完
            3:      用户没填过手机号
            4:      该手机号已经领取过了
    '''
    try:
        sess = dbsession_generator_write()
        code = sess.query(SuperGirlsCode).filter(SuperGirlsCode.used == 0).first()
        if not code: return 2
        mobile_user = sess.query(SuperGirlsActMobile).filter(SuperGirlsActMobile.mobile == mobile).first()
        if not mobile_user: return 3
        if mobile_user.sg_code: return 4
        mobile_user.sg_code = code.code
        mobile_user.user_id = user_id
        code.used = 1
        sess.add(mobile_user)
        sess.add(code)
        sess.commit()
        return str(code.code)
    except Exception, ex:
        print Exception, ex
        logger.info(str(ex))
        sess.rollback()
        return 0
    finally:
        sess.close()

def make_user_sent(mobile):
    try:
        sess = dbsession_generator_write()
        sess.query(SuperGirlsActMobile).filter(SuperGirlsActMobile.mobile == mobile).update({SuperGirlsActMobile.sent:1})
        sess.commit()
    except Exception, ex:
        logger.info(str(ex))
        sess.rollback()
    finally:
        sess.close()

def sg_send_code(mobile):
    logger.info('{0} {1} sg_send_code enter'.format(mobile, datetime.datetime.now()))
    user = get_user_by_mobile_num(mobile)
    if not user:
        logger.info('{0} {1} sg_send_code no_user'.format(mobile, datetime.datetime.now()))
        return 0
    code = sg_bind_code(user.id, mobile)
    logger.info('{0} {1} sg_send_code sg_bind_code_return_{2}'.format(mobile, datetime.datetime.now(), code))
    res = 0
    if not isinstance(code, int):
        url = 'http://s.mgtv.com/c?c={0}&p={1}'.format(code, mobile)
        content = '快来领取你的超女币吧~ {0}'.format(url)
        cli = EventClient()
        res = cli.event_new(100, [user.id], 100, content, str(time.time()))
        logger.info('{0} {1} sg_send_code send_message_{2}'.format(mobile, datetime.datetime.now(), res))
        if res:
            r = make_user_sent(mobile)
            logger.info('{0} {1} sg_send_code mark_user_{2}'.format(mobile, datetime.datetime.now(), r))
    else:
        logger.info('{0} {1} sg_send_code sg_bind_code_failed'.format(mobile, datetime.datetime.now()))
        res = 0
    return res

