# -*- coding: utf-8 -*-
import datetime
from time import time
from os import urandom
from hmac import HMAC
from base64 import urlsafe_b64encode
from hichao.base.lib.redis import (
        redis_token,
        redis_token_key,
        redis_token_slave,
        redis_token_slave_key,
        )
from hichao.app.models.db import Base
from hichao.base.lib.timetool import ONE_HOUR_SECOND, ONE_DAY_SECOND
from hichao.cache import get_cache_client
from ice_client import ClientFactory, HiExc

redis = redis_token
redis_key = redis_token_key
redis_slave = redis_token_slave
redis_slave_key = redis_token_slave_key

TOKEN_EXPIRE = ONE_DAY_SECOND * 90 

REDIS_OAURH2_ACCESS_TOKEN_BY_USER_ID = redis_key.Oauth2AccessTokenByUserId() 
REDIS_OAURH2_USER_ID_BY_ACCESS_TOKEN = redis_key.Oauth2UserIdByAccessToken() 

REDIS_NEW_OAURH2_ACCESS_TOKEN_BY_USER_ID = redis_key.NewOauth2AccessTokenByUserId('%s') 
REDIS_NEW_OAURH2_USER_ID_BY_ACCESS_TOKEN = redis_key.NewOauth2UserIdByAccessToken('%s') 

def generate_token(size=32):
    return urlsafe_b64encode(urandom(size)).rstrip("=")

class OAuth2AccessToken(object):

    def __init__(self):
        pass

    @classmethod
    def access_token_new(cls, user_id):
        key_by_user = REDIS_OAURH2_ACCESS_TOKEN_BY_USER_ID
        key_by_token  = REDIS_OAURH2_USER_ID_BY_ACCESS_TOKEN
        while True:
            _token = generate_token() 
            if not redis_slave.hget(key_by_token, _token):
                p = redis.pipeline(transaction=False)
                p.hset(key_by_user, user_id, _token)
                p.hset(key_by_token, _token, user_id)
                p.expire(key_by_user, TOKEN_EXPIRE)
                p.expire(key_by_token, TOKEN_EXPIRE)
                #p.setex(REDIS_NEW_OAURH2_ACCESS_TOKEN_BY_USER_ID%user_id, _token, TOKEN_EXPIRE)
                #p.setex(REDIS_NEW_OAURH2_USER_ID_BY_ACCESS_TOKEN%_token, user_id, TOKEN_EXPIRE)
                r = p.execute()
                return OAuth2AccessToken.get_access_token(user_id) 

    @classmethod
    def get_access_token(cls, user_id):
        key = REDIS_OAURH2_ACCESS_TOKEN_BY_USER_ID
        return redis_slave.hget(key, user_id)
        #key = REDIS_OAURH2_ACCESS_TOKEN_BY_USER_ID
        #return redis.get(REDIS_NEW_OAURH2_ACCESS_TOKEN_BY_USER_ID%user_id, TOKEN_EXPIRE)

    @classmethod
    def get_user_id(cls, token):
        try:
            throne_client = ClientFactory.create('throne')
            user_id = throne_client.GetUidByToken(token)
        except Exception as e:
            user_id = None
            print '=====================>>    get_user_id_by_token_error'
            print e
        if not user_id:
            cli = get_cache_client()
            user_id = cli.get(token)
            if not user_id:
                key_by_token  = REDIS_OAURH2_USER_ID_BY_ACCESS_TOKEN
                key_by_user = REDIS_OAURH2_ACCESS_TOKEN_BY_USER_ID
                user_id = redis_slave.hget(key_by_token, token)
                cli.setex(token, 1800, user_id)
        return user_id

#TODO  到redis user token 数据

#print OAuth2AccessToken.access_token_new(276469)
#print OAuth2AccessToken.get_access_token(276469)
#print OAuth2AccessToken.get_user_id('ki4Yrpht720SNwqWsf_K9guAumviQfshCa2FMXeU_Vo')

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

