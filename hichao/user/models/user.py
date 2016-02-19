# -*- coding: utf-8 -*-
from datetime import datetime
import time
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, Text, String, VARCHAR, DATETIME, FLOAT
from sqlalchemy.dialects.mysql import INTEGER
from hichao.user.models.db import DBSession, Base, dbsession_generator, new_dbsession_generator, user_dbsession_generator, new_session, rdbsession_generator
from hichao.base.models.app import REDIS_APP_IDENTIFY
from hichao.base.lib.timetool import today_days
from hichao.base.lib.redis import redis, redis_key
from hichao.base.models.base_component import BaseComponent
from hichao.util.image_url import build_user_avatar_url
from hichao.util.date_util import HOUR
from hichao.cache.cache import deco_cache, deco_cache_m
import transaction
from hichao.upload.models.image import get_image_by_id
from hichao.shop.models.user import get_ec_user_by_user_id
from hichao.util.statsd_client import timeit
from hichao.base.config import MEMBER_RANKS
from hichao.user.models.user_register import check_tel_legal
from hichao.follow.models.follow import get_user_follow_status

# class User(Base):
#    __tablename__ = 'User'
# id = Column(Integer, primary_key=True)
#    id = Column('user_id', Integer, primary_key=True, autoincrement=True)
#    username = Column(VARCHAR(64))
#    password = Column(VARCHAR(128))
#    email = Column(VARCHAR(128))
#    avatar = Column(VARCHAR(256))
#    url = Column(VARCHAR(256))
#    role = Column(Integer)
#    user_type = Column(VARCHAR(64))
#    open_id = Column(VARCHAR(64))
#    gender = Column(VARCHAR(2))
#    location = Column(VARCHAR(64))
#    register_date = Column(VARCHAR(20))
#    last_date = Column(VARCHAR(20))
#
#    def __init__(self):
#        if not Base.metadata.bind.has_table(self.__tablename__):
#            self.metadata.create_all()
#
#    def can_admin(self, user_id):
#        return self.user_id == user_id

timer = timeit('hichao_backend.m_user')

class User(Base, BaseComponent):
    __tablename__ = 'user'

    id = Column('user_id', Integer, primary_key=True, autoincrement=True)
    username = Column(VARCHAR(64))
    password = Column(VARCHAR(128))
    email = Column(VARCHAR(128))
    url = Column(VARCHAR(256))
    role = Column(Integer)
    user_type = Column(VARCHAR(64))
    open_id = Column(VARCHAR(64))
    token = Column(VARCHAR(64))
    gender = Column(Integer)
    location = Column(VARCHAR(64))
    identifier = Column(VARCHAR(64))
    apple_uid = Column(VARCHAR(32))
    last_date = Column(VARCHAR(20))
    register_date = Column(VARCHAR(20))
    avatar = Column(VARCHAR(256))
    background_img_id = Column(Integer)
    avatar_img_id = Column(INTEGER(unsigned=True), nullable=False, server_default="0")
    birthday = Column(DATETIME)
    constellation = Column(VARCHAR(64))
    nickname = Column(VARCHAR(64))
    connect = Column(VARCHAR(32))
    loginname = Column(VARCHAR(128))
    mobile_num = Column(VARCHAR(16))

    def __init__(self):
        pass
    
    def test(self):
        print '********************* start *******************'
        for i,j in vars(self).items():
            print '%32r = %r'%(i,j)
        print '********************** end ********************'

    def get_component_id(self):
        return str(self.id)

    def get_bind_ec_user(self):
        return get_ec_user_by_user_id(self.id)

    def get_component_user_name(self):
        user_name = self.nickname if self.nickname else self.username
        user_name = user_name.strip().replace('\n','')
        return user_name

    def get_component_user_avatar(self):
        avatar = build_user_avatar_url(self.avatar)
        if self.avatar_img_id > 0:
            image = get_image_by_id(self.avatar_img_id)
            if image: avatar = image.get_component_user_avatar()
        return avatar

    def get_component_user_rank(self):
        ec_user = self.get_bind_ec_user()
        if ec_user: return ec_user.get_component_user_rank()
        return 'v0'

    def get_component_user_rank_icon(self):
        ec_user = self.get_bind_ec_user()
        if ec_user: return ec_user.get_component_user_rank_icon()
        return MEMBER_RANKS.get(0)

    def get_rank(self):
        ec_user = self.get_bind_ec_user()
        if ec_user: return ec_user.get_rank()
        else: return 0

    def get_component_level(self):
        return '1'
    
    def to_ui_action(self):
        action = {}
        action['actionType'] = 'space'
        action['userId'] = self.get_component_id()
        action['userName'] = self.get_component_user_name()
        action['userAvatar'] = self.get_component_user_avatar()
        return action

    def to_lite_ui_action(self):
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'user'
        action['id'] = self.get_component_id()
        return action

    def get_register_date(self):
        register_time = float(1450841046.445965)
        if self.register_date:
            return float(self.register_date)
        return register_time

    def to_staruser_ui_action(self):
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'user'
        action['id'] = str(self.id)
        return action

    # 判断用户是否关注这个用户
    def check_user_follow_status(self,app_user_id):
        result = 0
        if app_user_id > 0:
            result = get_user_follow_status(app_user_id,self.id)
        return result

class UserLocation(Base, BaseComponent):
    __tablename__ = 'user_location'
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(INTEGER(unsigned=True), nullable=False)
    nation = Column(String(64), nullable=False, server_default="")
    province = Column(String(64), nullable=False, server_default="")
    city = Column(String(64), nullable=False, server_default="")
    longitude = Column(FLOAT(precision=9, scale=6), nullable=False)
    latitude = Column(FLOAT(precision=9, scale=6), nullable=False)

    def __init__(self):
        self.user_id=0
        self.nation=''
        self.province=''
        self.city=''
        self.longitude=0.0
        self.last_date=0.0

@timer
def user_new(username, password, email, avatar, url, role,
             user_type, open_id, gender, location):
    try:
        user = DBSession.query(User).filter(
            User.open_id == open_id, User.user_type == user_type).first()
    except Exception, ex:
        print ex
        DBSession.rollback()
        user = DBSession.query(User).filter(
            User.open_id == open_id, User.user_type == user_type).first()
    if not user:
        user = User()
    user.username = username
    user.password = password
    user.email = email
    user.avatar = avatar
    user.url = url
    user.role = role
    user.user_type = user_type
    user.open_id = open_id
    user.token = 0
    user.gender = gender
    user.location = location
    user.register_date = int(time())
    user.last_date = int(time())
    user.identifier = 0
    user.apple_uid = 0
    try:
        DBSession.add(user)
        _id = user.id
        transaction.commit()
    except Exception, ex:
        print ex
        # DBSession.rollback()
        transaction.abort()
        return 0
    finally:
        DBSession.close()
    return _id


@timer
@deco_cache(prefix='user', recycle=HOUR)
def get_user_by_id(user_id, use_cache=True):
    DBSession = dbsession_generator()
    user = DBSession.query(User).filter(User.id == int(user_id)).first()
    DBSession.close()
    return user

@timer
@deco_cache_m(prefix = 'user', recycle = HOUR)
def get_users_by_id(user_ids, use_cache = False):
    user_ids = [int(user_id) for user_id in user_ids]
    DBSession = dbsession_generator()
    users = DBSession.query(User.id,User).filter(User.id.in_(user_ids)).all()
    users = dict(users)
    DBSession.close()
    return users

@timer
@deco_cache(prefix="user_location", recycle=HOUR)
def get_user_location_by_id(user_id, use_cache=True):
    DBSession = dbsession_generator()
    location = DBSession.query(UserLocation).filter(UserLocation.user_id==user_id).first()
    DBSession.close()
    return location

@timer
@deco_cache(prefix='user_ids', recycle=HOUR)
def get_user_ids(use_cache=True):
    DBSession = dbsession_generator()
    user_ids = DBSession.query(User.id).order_by(User.id.asc()).limit(1000).all()
    DBSession.close()
    res = [use_id[0] for use_id in user_ids]
    return res

@timer
def user_login_today_by_redis(app_name):
    """ for identify, time in user_login_today_by_redis(app_name):
            print identify, time
    """
    return redis.hgetall(REDIS_APP_IDENTIFY % (app_name, today_days()))


@timer
def get_user_by_userid_openid(user_id, open_id):
    DBSession = dbsession_generator()
    user = DBSession.query(User).filter(
        User.id == user_id).filter(User.open_id == open_id).first()
    DBSession.close()
    return user

# print 'list ', user_login_today_by_redis('mxyc_lite_ip')


@timer
def add_user_background(user_id, img_id):
    rv = 1
    try:
        sess = new_session()
        res = sess.query(User)\
                  .filter(User.id == user_id)\
                  .first()
        sess.flush()
        res.background_img_id = img_id
        sess.add(res)
        sess.commit()
    except Exception, e:
        print Exception, ':', e
        sess.rollback()
        rv = 0
    finally:
        sess.close()
    return rv

@timer
def add_user_avatar(user_id, img_id):
    DBSession = user_dbsession_generator()
    # 在第一次上传头像和修改头像时，该用户信息都已存在与数据库，所以都为update操作
    # 双返回值，第一位表示是否修改成功，成功为1,失败为1;第二位表示是否为第一次修改，第一次为1,其他为0
    print user_id, img_id
    try:
        last_avatar_img_id = get_user_item_by_user_id(user_id, "avatar_img_id")
        DBSession.query(User).filter(
            User.id == user_id).update({"avatar_img_id": img_id})
        DBSession.commit()
    except Exception, e:
        print e, '*/'*20
        return 0, 0
    else:
        if last_avatar_img_id == 0:
            print '*/'*20
            return 1, 1
        else:
            return 1, 0
    finally:
        DBSession.close()


@timer
def get_user_info(user_id):
    user = get_user_by_id(user_id, use_cache=False)
    #location = get_user_location_by_id(user_id, use_cache=False)
    data = {}
    '''当前积分以及升级需要的积分\等级'''
    data['score'] = '0'
    data['needScore'] = '1000'
    data['level'] = '1'
    if user:
        nickname = user.nickname if user.nickname!='' else user.username
        data['nickname'] = nickname.replace('\n','')
        data['gender'] = '男' if user.gender==1 else '女'
        data['birthday'] = user.birthday.strftime('%Y-%m-%d') if user.birthday else ''
        data['constellation'] = user.constellation
        data['commonEmail'] = user.email if user.email!="0" else ""
        data['common_email'] = data['commonEmail']
        data['connect'] = user.connect
        if check_tel_legal(user.loginname):
            data['loginname'] = user.loginname
        else:
            data['loginname'] = ''
        data['avatarUrl'] = user.get_component_user_avatar()
        data['city'] = user.location
    
    return data

@timer
def update_user_info(user_id, nickname, gender, constellation, common_email, birthday, connect, nation, province, city, longitude, latitude):
    from hichao.points.models.points import point_change
    user = get_user_by_id(user_id)
    user_info = get_user_info(user_id)
    location = get_user_location_by_id(user_id)
    print '----------------------------------------------------------'
    print 'location is ', nation , province, city
    print 'email is ', common_email
    print '----------------------------------------------------------'
    DBSession = new_dbsession_generator()
    flag=0
    try:
        if not location:
            location = UserLocation()
            location.user_id = user_id
        if location.user_id==0 or (location.user_id!=0 and location.nation!=''):
            flag=1
        location.nation = nation
        location.province = province
        location.city = city
        location.longitude = longitude
        location.latitude = latitude
        DBSession.add(location)
        if flag==1:
            point_change(user_id, 'improve_personal_city',user_id, time.time())
        get_user_location_by_id(user_id, use_cache=False)

        if user:
            user.nickname= nickname
            user.gender = gender
            user.constellation = constellation
            user.email = common_email
            user.birthday = datetime.strptime(birthday, "%Y-%m-%d") if birthday!='' else None
            user.connect = connect
            user.location = city
            DBSession.add(user)
            transaction.commit()
            if user_info['nickname']=="":
                point_change(user_id, 'improve_personal_nickname',user_id, time.time())
            if user_info['commonEmail']=="":
                point_change(user_id, 'improve_personal_email',user_id, time.time())
            if user_info['connect']=="":
                point_change(user_id, 'improve_personal_connect',user_id, time.time())

            get_user_by_id(user_id, use_cache=False)
            return 1
    except Exception, e:
        print Exception, ":", e
        transaction.abort()
        return 0
    finally:
        DBSession.close()

@timer
def update_user_location(user_id, nation, province, city, longitude, latitude):
    from hichao.points.models.points import point_change
    location = get_user_location_by_id(user_id)
    DBSession = dbsession_generator()
    flag=0
    try:
        if not location:
            location = UserLocation()
        if location.user_id==0 or (location.user_id!=0 and location.nation!=''):
            flag=1
        location.nation = nation
        location.province = province
        location.city = city
        location.longitude = longitude
        location.latitude = latitude
        DBSession.add(location)
        DBSession.flush()
        transaction.commit()
        if flag==1:
            point_change(user_id, 'improve_personal_city',user_id, time.time())

        get_user_location_by_id(user_id, False)
        return 1
    except Exception, e:
        print Exception, ":", e
        transaction.abort()
        return 0
    finally:
        DBSession.close()


@timer
def get_user_avatar(user):
    if user:
        if user.avatar_img_id != 0:
            image = get_image_by_id(user.avatar_img_id)
            print 'iamge is ', image
            return image.url
            #return image.get_component_pic_fall_url
        else:
            return user.avatar
    return ''


@timer
def get_user_backgroundurl(user):
    if user:
        if user.background_img_id != 0:
            image = get_image_by_id(user.background_img_id)
            return image.get_component_pic_fall_url
    return ''

@timer
def get_user_item_by_user_id(user_id, item):
    """item为要从user表中拿取的字段"""
    DBSession = dbsession_generator()
    try:
        user_info = DBSession.query(
            User.__dict__[item]).filter(User.id == user_id).first()
    except Exception, e:
        print e
        return None
    else:
        if user_info:
            return user_info.__dict__[item]
    finally:
        DBSession.close()

@timer
def get_user_city_by_user_id(user_id):
    """从user_location表中拿取用户城市，字段默认为空字符串"""
    DBSession = dbsession_generator()
    try:
        user_info = DBSession.query(
            UserLocation.city).filter(UserLocation.user_id == user_id).first()
    except Exception, e:
        print e
        return 0
    else:
        if user_info:
            return user_info
    finally:
        DBSession.close()

@timer
def get_location_info(latitude, longitude):
    import urllib, urllib2, json, httplib
    url ='http://api.map.baidu.com/geocoder?output=json&location='+latitude+','+longitude+'&key=37492c0ee6f924cb5e934fa08c6b1676'
    request = urllib2.Request(url)
    response = urllib2.urlopen(url)
    res = response.read()
    res = json.loads(res)
    data={}
    if res['status'] in ['ok', 'Ok', 'OK']:
        res = res['result']['addressComponent']
    else:
        return data
    data['city']=res['city']
    data['province']=res['province']
    data['nation']='中国'
    return data

@timer
def update_user_nickname(user_id, nickname):
    result = 0
    try:
        DBSession = new_dbsession_generator()
        DBSession.query(User).filter(User.id == int(user_id)).update({User.nickname:nickname})
        transaction.commit()
        result = 1
    except Exception, e:
        print e
        DBSession.rollback()
    finally:
        DBSession.close()
    return result

def update_user_loginname_and_mobile_num(user_id, loginname = '',mobile_num = ''):
    result = 0
    try:
        user = get_user_by_id(user_id)
        if loginname:
            user.loginname = loginname
        if mobile_num:
            user.mobile_num = mobile_num
        DBSession = new_dbsession_generator()
        DBSession.add(user)
        transaction.commit()
        result = 1
    except Exception, e:
        print e
        DBSession.rollback()
    finally:
        DBSession.close()
    return result

def get_user_by_mobile_num(mobile):
    try:
        DBSession = rdbsession_generator()
        user = DBSession.query(User).filter(User.loginname == mobile).first()
        return user
    except Exception, ex:
        print Exception, ex
        DBSession.rollback()
    finally:
        DBSession.close()
    

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
