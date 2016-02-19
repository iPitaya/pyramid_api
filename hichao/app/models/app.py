# -*- coding: utf-8 -*-
from time import time
from os import urandom
from uuid import uuid4
from base64 import urlsafe_b64encode
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, Text, String

from hichao.app.models.db import dbsession_generator, Base
from hichao.base.lib.redis import redis, redis_key, redis_slave


REDIS_APP_ID_BY_SECRET_KEY = redis_key.AppIdBySecretKey()
REDIS_APP_SECRET_BY_APP_ID = redis_key.AppSecretByAppId()

def generate_secret(size=32):
    return urlsafe_b64encode(urandom(size)).rstrip("=")

class App(Base):
    __tablename__ = 'App'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    name = Column(String(32), unique=True)
    secret = Column(String(32), unique=True)
    txt = Column(Text)
    time = Column(BigInteger)
    state = Column(SmallInteger)

    def __init__(self):
        if not Base.metadata.bind.has_table(self.__tablename__):
            self.metadata.create_all()

    def _secret(self):
        key_id = REDIS_APP_ID_BY_SECRET_KEY
        key_secret = REDIS_APP_SECRET_BY_APP_ID
        while True:
            secret = generate_secret()
            if not redis_slave.hget(key,secret):
                p = redis.pipeline(transaction=False)
                p.hset(key_id, self.id, secret)
                p.hset(key_secret, secret, self.id)
                p.execute()
                return secret 

    def can_admin(self, user_id):
        return self.user_id == user_id


def app_new(user_id, name, txt):
    app = App()
    app.user_id = user_id
    app.name = name
    app.secret = app._secret() 
    app.txt = txt
    app.time = int(time())
    app.state = APP_STATE.NORMAL 
    try:
        DBSession = dbsession_generator()
        DBSession.add(app)
        DBSession.flush()
    except Exception, ex:
        print ex
        DBSession.rollback()
        return 0
    finally:
        DBSession.close()
    return app

def app_list_by_user(user_id):
    app_list = App.filter(user_id=user_id).all()
    return app_list

#def _app_new(user_id, app_id, secret):
#    key = REDIS_APP_ID_BY_SECRET_KEY  
#    redis.hset(key, secret, app_id)

def app_id_by_secret(secret):
    key = REDIS_APP_ID_BY_SECRET_KEY  
    return redis_slave.hget(key, secret)

def app_secret_by_id(app_id):
    key = REDIS_APP_SECRET_BY_APP_ID
    return redis_slave.hget(key, app_id)

#app = app_new(10000000,'tardislabs', 'hichao 的app_id')
#print app.id, app.secret

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
