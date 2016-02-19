# -*- coding: utf-8 -*-
from time import time
from sqlalchemy import (
        Column,
        Integer,
        BigInteger,
        SmallInteger,
        Text,
        String,
        VARCHAR,
        TIMESTAMP,
        )
from hichao.user.models.db import (
        Base,
        device_dbsession_generator,
        r_device_dbsession_generator,
        )
#from hichao.base.lib.redis import redis_device, redis_device_key
from hichao.base.lib.timetool import (
        today_days,
        ONE_DAY_SECOND,
        )
from hichao.util.statsd_client import timeit
import transaction
import datetime

USER_LOGIN_EXPIRE = ONE_DAY_SECOND * 7

#REDIS_USER_DEVICE_TOKEN_DAILY = redis_device_key.UserDeviceDaily('%s-%s-%s-%s')
#REDIS_USER_DEVICE_TOKEN_DAILY_ZSET = redis_device_key.UserDeviceDailyZset('%s-%s-%s-%s')

timer = timeit('hichao_backend.m_device')

@timer
def user_identify_last_new(app_name, app_from, app_version, app_identify):
    return
    ##key = REDIS_USER_DEVICE_TOKEN_DAILY%(app_name, app_from, app_version, today_days())
    #key_zset  = REDIS_USER_DEVICE_TOKEN_DAILY_ZSET%(app_name, app_from, app_version, today_days())
    #p = redis_device.pipeline(transaction=False)
    ##p.hset(key, app_identify, time())
    #p.zadd(key_zset, time(), app_identify)
    ##p.expire(key, USER_LOGIN_EXPIRE)
    #p.expire(key_zset, USER_LOGIN_EXPIRE)
    #p.execute()


@timer
def user_identify_last_login(app_name, app_from, app_version, days=today_days()):
    return
    #""" 返回一个字典, 可以用iteritems()迭代"""
    #return redis_device.hgetall(REDIS_USER_DEVICE_TOKEN_DAILY%(app_name, app_from, app_version, days))

#print user_identify_last_login('mxyc_lite_ip','iphone', '1.0', 15600 )

@timer
def user_identify_last_login_by_offset(app_name, app_from, app_version, days=today_days(), offset=0, limit=18, reverse=0):
    return
    #key_zset  = REDIS_USER_DEVICE_TOKEN_DAILY_ZSET%(app_name, app_from, app_version, days)
    #if reverse ==0:
    #    _list = redis_device.zrevrange(key_zset, offset, offset+limit, withscores=True)
    #else:
    #    _list = redis_device.zrange(key_zset, offset, offset+limit, withscores=True)
    #return _list

#print user_identify_last_login_by_offset('mxyc_lite_ip','iphone', '1.0')

class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer,primary_key=True)
    devicetoken = Column('devicetoken', VARCHAR(64))
    appname = Column(VARCHAR(64))
    open_uuid = Column(VARCHAR(64))
    mac = Column(VARCHAR(64))
    version = Column(VARCHAR(64))
    platform = Column(VARCHAR(64))
    enable = Column(SmallInteger)
    logintime = Column('timelog', TIMESTAMP)
    user_id = Column(Integer)
    third_push_name = Column(VARCHAR(64))
    tpn_token = Column(VARCHAR(128))

@timer
def device_new(devicetoken, appname, open_uuid, mac, version, platform, enable, third_push_name = '', user_id = 0, tpn_token = '', logintime = ''):
    ''' 新添加设备信息  '''
    device = Device()
    if not logintime: logintime = datetime.datetime.now()
    device.devicetoken = devicetoken
    device.appname = appname
    device.open_uuid = open_uuid
    device.mac = mac
    device.version = version
    device.platform = platform
    device.enable = enable
    device.logintime = logintime
    device.third_push_name = third_push_name
    device.user_id = user_id
    device.tpn_token = tpn_token
    return commit_update_session(device)

@timer
def device_update_by_devicetoken(devicetoken, appname, open_uuid, mac, version, platform, enable, third_push_name = '', user_id = 0, tpn_token = '', logintime = ''):
    ''' 更新设备信息 '''
    session = device_dbsession_generator()
    try:
        session.query(Device).filter(Device.devicetoken == devicetoken).filter(Device.third_push_name == third_push_name).update({
                Device.appname:appname,
                Device.open_uuid:open_uuid,
                Device.mac:mac,
                Device.version:version,
                Device.platform:platform,
                Device.enable:enable,
                Device.user_id:user_id,
                Device.tpn_token:tpn_token,
                Device.logintime:logintime})
        session.commit()
    except Exception, ex:
        print Exception, ex
        session.rollback()
    finally:
        session.close()

@timer
def commit_update_session(device):
    try:
        device_read_session = device_dbsession_generator()
        device_read_session.add(device)
        device_read_session.commit()
    except Exception,e:
        print e
        device_read_session.rollback()
    finally:
        device_read_session.close()


@timer
def device_OnOff_state_by_devicetoken(devicetoken, enable, logintime = '', third_push_name = ''):
    '''是否接受推送开关 enable = 1为接受 enable = 2 关闭接受'''
    device = get_device_by_devicetoken(devicetoken, third_push_name)
    if not logintime: logintime = datetime.datetime.now()
    device.logintime = logintime
    device.enable = enable
    return commit_update_session(device)

@timer
def device_relate_state_by_devicetoken(devicetoken,user_id, logintime = '', third_push_name = ''):
    ''' devicetoken和用户id关联  '''
    device = get_device_by_devicetoken(devicetoken, third_push_name)
    if not logintime: logintime = datetime.datetime.now()
    device.logintime = logintime
    device.user_id = user_id
    return commit_update_session(device)

@timer
def get_device_by_devicetoken(devicetoken, third_push_name = ''):
    try:
        device_read_session = r_device_dbsession_generator()
        device = device_read_session.query(Device).filter(Device.devicetoken == devicetoken).filter(Device.third_push_name == third_push_name).first()
        return device
    except Exception, ex:
        print Exception, ex
        return None
    finally:
        device_read_session.close()

@timer
def get_device_by_open_uuid(open_uuid):
    try:
        device_read_session = r_device_dbsession_generator()
        device = device_read_session.query(Device).filter(Device.open_uuid == open_uuid).first()
        return device
    except Exception, ex:
        print Exception, ex
        return None
    finally:
        device_read_session.close()

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
