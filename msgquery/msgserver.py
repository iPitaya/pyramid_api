# coding:utf-8
import ujson
import sys

import tornado.wsgi
import tornado.web

from hichao.base.lib.redis import redis_token, redis_token_key
from hichao.collect.models.collect import Collect
from hichao.collect.models.topic import topic_count_by_user_id
from hichao.collect.models.thread import thread_count_by_user_id
from hichao.collect.models.star import star_count_by_user_id
from hichao.collect.models.sku import sku_count_by_user_id
from hichao.collect.models.news import news_count_by_user_id
from hichao.collect.models.brand import brand_count_by_user_id
from hichao.forum.models.thread import get_thread_count_by_user_id

redis = redis_token
redis_key = redis_token_key

star_collector = Collect('star')
sku_collector = Collect('sku')

REDIS_OAURH2_USER_ID_BY_ACCESS_TOKEN = redis_key.Oauth2UserIdByAccessToken()

class Application(tornado.wsgi.WSGIApplication):

    def __init__(self):
        handlers = [
            (r"/hi_zone_nums", HiZoneNums),
        ]
        settings = dict(
            debug=False,
        )
        tornado.wsgi.WSGIApplication.__init__(self, handlers, **settings)


class HiZoneNums(tornado.web.RequestHandler):

    def get(self):
        self.set_header("Content-Type", "application/json")
        token = self.get_argument('access_token', '')
        user_id = self.get_argument('user_id', '')
        result = {}
        if not token and not user_id:
            result = {'errorCode': '10020', 'error': '传入参数错误'}
        if not user_id:
            key_by_token = REDIS_OAURH2_USER_ID_BY_ACCESS_TOKEN
            user_id = redis.hget(key_by_token, token)
        if not user_id or int(user_id) <= 0:
            result = {'errorCode': '20020', 'error': '用户验证错误'}
        else:
            data = {}
            # 收藏的帖子个数。
            data['collectThreadTotal'] = str(thread_count_by_user_id(user_id))
            data['starTotal'] = str(star_count_by_user_id(user_id))
            data['skuTotal'] = str(sku_count_by_user_id(user_id))
            data['topicTotal'] = str(topic_count_by_user_id(user_id))
            data['newsTotal'] = str(news_count_by_user_id(user_id))
            data['brandTotal'] = str(brand_count_by_user_id(user_id))
            # 发布的帖子个数。
            data['subjectTotal'] = str(get_thread_count_by_user_id(user_id))
            result['data'] = data
            result['message'] = ''
        return self.write(ujson.dumps(result))

app = Application()

if __name__ == "__main__":
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop
    import tornado.options

    tornado.options.parse_command_line()
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(12300)
    IOLoop.instance().start()
