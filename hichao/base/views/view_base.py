import json
from time import time
from pyramid.view import view_config
from pyramid.response import Response
from hichao.base.lib.redis import redis, redis_key
from hichao.base.lib.require import require, RequirementException
from hichao.base.lib.timetool import today_days
from hichao.base.models.app import REDIS_APP_IDENTIFY


#class CommonMiddleware(object):
#    def __init__(self):
#        pass
#
class View(object):
    def __init__(self):
        self.error = {}

    def message(self, code=None, content=None):
        self.error['errorCode'] = code
        self.error['error'] = content
    #def __call__(self):
    #    try:
    #        app_name = self.request.params['gn']
    #        identify = self.request.params['gi']
    #        redis.hset(REDIS_APP_IDENTIFY%(app_name, today_days()), identify, time())
    #        print '__call__'
    #    except Exception as ex:
    #        print ex

def require_type(func):
    print 'start checking type', '*'*20
    def _(self, *args, **kwargs):
        try:
            self.type = self.request.params['type']
            require(self.type)
        except KeyError, RequirementException:
            self.error["error"] = "none_type"
            self.error["errorCode"] = "21324"
        if self.error:
            return Response(json.dumps(self.error))
        return func(self, *args, **kwargs)
    return _
