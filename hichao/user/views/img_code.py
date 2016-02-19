# -*- coding:utf-8 -*-
from pyramid.view  import view_config
from pyramid.view  import view_defaults
from pyramid.response  import Response
from hichao.base.views.view_base  import View
from hichao.util.pack_data  import pack_data
from hichao.app.views.oauth2 import check_permission
from hichao.util.statsd_client import statsd
from hichao.user.models.img_code import get_img_code_content,get_code_key
from hichao.user.models.redis_sms import set_img_code_redis

@view_defaults(route_name='img_code')
class ImgCodeView(View):
    def __init__(self,request):
        super(ImgCodeView,self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_img_code.post')
    @check_permission
    @view_config(request_method='GET',renderer = 'json')
    #@pack_data
    def get(self):
        msg,code = get_img_code_content()
        key,code_key = get_code_key(code)
        response = Response(msg,content_type = "image/gif")
        #response.headerlist.append(('Access-Control-Allow-Origin', '*'))
        response.set_cookie('key', key, max_age=None,path='/', domain=None, secure=False, httponly=False,comment=None, expires=None, overwrite=False, key=None)
        return response
