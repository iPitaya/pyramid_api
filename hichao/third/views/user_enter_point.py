# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from pyramid.httpexceptions import (
        HTTPSeeOther,
        HTTPNotFound,
        )
from hichao.base.config import THIRD_PARTY_USER_ENTER_POINT
from hichao.base.views.view_base import View

@view_defaults(route_name = 'cart')
class CartView(View):
    def __init__(self, request):
        super(CartView, self).__init__()
        self.request = request

    @view_config(request_method = 'GET')
    def get(self):
        return redirect_to_third_party(self.request, 'cart')

@view_defaults(route_name = 'order')
class OrderView(View):
    def __init__(self, request):
        super(OrderView, self).__init__()
        self.request = request

    @view_config(request_method = 'GET')
    def get(self):
        return redirect_to_third_party(self.request, 'order')

@view_defaults(route_name = 'express')
class ExpressView(View):
    def __init__(self, request):
        super(ExpressView, self).__init__()
        self.request = request

    @view_config(request_method = 'GET')
    def get(self):
        return redirect_to_third_party(self.request, 'express')

def redirect_to_third_party(request, route):
    tp = request.matchdict.get('third_party', '')
    enter_point = THIRD_PARTY_USER_ENTER_POINT.get(tp, '')
    url = ''
    if enter_point: url = enter_point[route]
    if url:
        return HTTPSeeOther(location = url)
    else:
        return HTTPNotFound()


