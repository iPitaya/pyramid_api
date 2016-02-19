# -*- coding:utf-8 -*-
from pyramid.view import view_defaults
from pyramid.view import view_config
from hichao.base.views.view_base import View, require_type
from hichao.app.views.oauth2 import check_permission
from hichao.comment.models.evaluation import (
        get_goods_commets_by_goods_id,
        add_comment_business_replace,
        get_goods_commets_by_business_id,
        add_goods_business_comment,
        get_goods_comment_dict,
        generate_BusinessComment_from_dict,
        generate_GoodsComment_from_dict,
        get_business_score,
        get_comment_state,
        GoodsComment_to_dict,
        get_goods_comment_by_comment_id,
        get_comment_num,
        add_additional_comments,
        get_order_detail,
        get_items_from_order_detail,
        get_goods_comment_num_public,
        get_goods_commets_by_goods_id_to_app,
        check_goods_additional_comment_business_reply,
        update_order_comment_state,
        check_evaluation_legal,
        get_order_detail_new,
        get_goods_comment_list_cache,
        get_comment_and_reply_list,
        delete_comment_cache,
        )
from hichao.util.statsd_client import statsd
from hichao.util.pack_data import (
        pack_data,
        version_ge,
        version_eq,
        )
from hichao.base.config import FALL_PER_PAGE_NUM
from hichao.cache.cache import delete_cache_by_key
from hichao.util.content_util import filter_tag
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


@view_defaults(route_name='evaluation_goods_comments')
class GoodsCommentsView(View):
    def __init__(self, request):
        super(GoodsCommentsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_goods_comments.get')
    @check_permission
    @view_config(request_method='GET', renderer = 'json')
    @pack_data
    def get(self):
        type_id = self.request.params.get('id', '')
        m_type = self.request.params.get('type', 0)
        flag = self.request.params.get('flag', '')
        if not flag:
            flag = 0
        flag = int(flag)
        from_type = self.request.params.get('from_type', 'app')
        if not type_id :
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '',{}
        if from_type == 'app':
            comments = get_goods_commets_by_goods_id(int(type_id),int(m_type),flag,FALL_PER_PAGE_NUM)
        elif from_type == 'ecshop':
            comments = get_goods_commets_by_business_id(int(type_id),int(m_type),flag,FALL_PER_PAGE_NUM)
        data = {}
        data['items'] = comments
        if len(comments) >= FALL_PER_PAGE_NUM:
            data['flag'] = str(flag + FALL_PER_PAGE_NUM)
        return '', data

    @statsd.timer('hichao_backend.r_goods_comments.post')
    @check_permission
    @view_config(request_method='POST', renderer = 'json')
    @pack_data
    def post(self):
        gf =  self.request.params.get('gf', '')
        gv =  self.request.params.get('gv', '')
        token =  self.request.params.get('access_token', '')
        eva_auth =  self.request.params.get('eva_auth', '')
        comments_data = self.request.params.get('data', {})
        datas = eval(comments_data)
        datas_json =  json.loads(comments_data)
        order_id = datas.get('order_id',0)
        user_id = datas.get('user_id',0)
        if not check_evaluation_legal(token, gv, gf,self.user_id, comments_data,eva_auth):
            self.error['error'] = 'invalid comment'
            self.error['errorCode'] = '30001'
            return '',{'status':0,'message':'数据无效'}
        if datas.get('order_id',0) == 0:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '',{'status':0,'message':'参数错误'}        
        if int(get_comment_state(order_id)) > 0:
            update_order_comment_state(order_id, self.user_id, token, 0)
            self.error['error'] = 'error.'
            self.error['errorCode'] = '30001'
            return '',{'status':0,'message':'您已经评价过'}        
        if self.user_id < 1:
            self.error['error'] = 'user is not login.'
            self.error['errorCode'] = '20001'
            return '',{'status':0,'message':'缺少用户信息'}
            
        business = {}
        business['order_id'] = datas.get('order_id',0)
        business['user_id'] = self.user_id
        business['business_id'] = datas.get('business_id',0)
        business['goods_ratio'] = datas.get('goods_ratio',5)
        business['serve_satisfy'] = datas.get('serve_satisfy',5)
        business['logistics_satisfy'] = datas.get('logistics_satisfy',5)
        goods_id_list = []
        goods = []
        for i,comment in enumerate(datas['goods_comments']):
            if type(comment) == 'str':
                comment = eval(comment)
            goods_id_list.append(comment['goods_id'])
            comment['order_id'] = business.get('order_id',0)
            comment['user_id'] = business.get('user_id',0)
            comment['business_id'] = business.get('business_id',0)
            comment['content'] = filter_tag(datas_json['goods_comments'][i].get('content','').encode('utf8'))
            if datas.has_key('use_anonymous'):
                comment['use_anonymous'] = datas['use_anonymous']
            goods.append(generate_GoodsComment_from_dict(comment))
        bs = []
        bs.append(generate_BusinessComment_from_dict(business))
        result = add_goods_business_comment(goods, bs)
        try:
            for g_id in goods_id_list:
                delete_comment_cache(g_id)
                get_goods_comment_list_cache(g_id, 0, 0, FALL_PER_PAGE_NUM, use_cache = False)
                get_goods_comment_list_cache(g_id, 1, 0, FALL_PER_PAGE_NUM, use_cache = False)
                get_goods_comment_list_cache(g_id, 2, 0, FALL_PER_PAGE_NUM, use_cache = False)
                get_goods_comment_list_cache(g_id, 4, 0, 2, use_cache = False)
                get_comment_num(g_id, use_cache = False)
        except Exception,e:
            print e
        data = {}
        data['status'] = str(result)
        if data['status'] == '1':
            update_order_comment_state(order_id, self.user_id, token, 0)
        if data['status'] == '1':
            data['message'] = '评价成功'
        else:
            data['message'] = '评价失败'
        return '',data

@view_defaults(route_name='evaluation_goods_comment')
class GoodsCommentView(View):
    def __init__(self, request):
        super(GoodsCommentView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_goods_comment.get')
    @check_permission
    @view_config(request_method='POST', renderer = 'json')
    @pack_data
    def post(self):
        comment_id = self.request.params.get('comment_id', 0)
        business_id = self.request.params.get('business_id', 0)
        content = self.request.params.get('content', '')
        comment_type =  self.request.params.get('type', 2)
        platform = self.request.params.get('platform', 'ecshop')
        imgs = self.request.params.get('imgs', '[]')
        gf =  self.request.params.get('gf', '')
        if gf:
            platform = gf
        goods = get_goods_comment_by_comment_id(int(comment_id))
        if not comment_id or not business_id or not goods:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '',{}
        states = check_goods_additional_comment_business_reply(int(comment_id),int(comment_type))
        if len(states) > 0:
            self.error['error'] = 'error.'
            self.error['errorCode'] = '30001'
            return '',{'status':0,'message':'您已经回复过'}
        comment = GoodsComment_to_dict(goods)
        comment['parent_id'] = int(comment_id)
        comment['business_id'] = int(business_id)
        comment['content'] = content.encode('utf8')
        comment['type'] = int(comment_type)
        comment['platform'] = platform
        comment['imgs'] = eval(imgs)
        status = add_comment_business_replace(comment)
        if goods.type == 1:
            get_comment_and_reply_list(goods.parent_id, use_cache = False)
        else:
            get_comment_and_reply_list(goods.id, use_cache = False)
        data = {}
        if int(status) > 0:
            status = 1
        data['status'] = str(status)
        data['message'] = ''
        if data['status'] == '1':
            data['message'] = '评价成功'
        else:
            data['message'] = '评价失败'
        return '', data

@view_defaults(route_name='evaluation_additional_comments')
class AdditionalCommentsView(View):
    def __init__(self, request):
        super(AdditionalCommentsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_additional_comments.post')
    @check_permission
    @view_config(request_method='POST', renderer = 'json')
    @pack_data
    def post(self):
        gf =  self.request.params.get('gf', '')
        gv =  self.request.params.get('gv', '')
        token =  self.request.params.get('access_token', '')
        eva_auth =  self.request.params.get('eva_auth', '')
        datas = self.request.params.get('data', '')
        if not datas:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '',{}
        if gf:
            platform = gf
        if not check_evaluation_legal(token, gv, gf,self.user_id,datas,eva_auth):
            self.error['error'] = 'invalid comment'
            self.error['errorCode'] = '30001'
            return '',{'status':0,'message':'数据无效'}
        items = eval(datas)
        comments = []
        goods_id_list = []
        comment_id_list = []
        order_id = 0
        for item in items:
            goods = get_goods_comment_by_comment_id(int(item['comment_id']))
            if goods:
                goods_id_list.append(goods.goods_id)
                comment_id_list.append(int(item['comment_id']))
                order_id = goods.order_id
                comment = GoodsComment_to_dict(goods)
                comment['parent_id'] = int(item['comment_id'])
                comment['business_id'] = int(item['business_id'])
                comment['content'] = item.get('content','').encode('utf8')
                comment['type'] = int(item['type'])
                comment['platform'] = item['platform']
                comment['imgs'] = item.get('imgs',[])
                ct = generate_GoodsComment_from_dict(comment)
                comments.append(ct)
        result = add_additional_comments(comments)
        try:
            for g_id in goods_id_list:
                delete_comment_cache(g_id)
                get_goods_comment_list_cache(g_id, 0, 0, FALL_PER_PAGE_NUM, use_cache = False)
                get_goods_comment_list_cache(g_id, 1, 0, FALL_PER_PAGE_NUM, use_cache = False)
                get_goods_comment_list_cache(g_id, 2, 0, FALL_PER_PAGE_NUM, use_cache = False)
        except Exception,e:
            print e
        for c_id in comment_id_list:
            get_comment_and_reply_list(c_id, use_cache = False)
        data = {}
        data['status'] = str(result)
        data['message'] = ''
        if  order_id > 0:
            update_order_comment_state(order_id, self.user_id, token, 1)
        if data['status'] == '1':
            data['message'] = '评价成功'
        else:
            data['message'] = '评价失败'
        return '', data

    @statsd.timer('hichao_backend.r_additional_comments.get')
    @check_permission
    @view_config(request_method='GET', renderer = 'json')
    @pack_data
    def get(self):
        gf =  self.request.params.get('gf', '')
        gv =  self.request.params.get('gv', '')
        token =  self.request.params.get('access_token', '')
        order_id =  self.request.params.get('order_id', '')
        if not self.user_id and not order_id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '',{}
        #data_attr = {}
        #data_attr['order_id'] = str(order_id)
        #data_attr['token'] = str(token)
        #data_attr['app_uid'] = str(self.user_id)
        #order_info = get_order_detail(data_attr)
        d_attr = {}
        d_attr['order_id'] = str(order_id)
        order_info = get_order_detail_new('mxyc_ios',str(self.user_id),'order.detail',token, gv,d_attr=d_attr)
        order_info = json.loads(order_info)
        if order_info.get('response',''):
            if not order_info.get('response','').get('data',''):
                self.error['error'] = 'Arguments error.'
                self.error['errorCode'] = '10001'
                return '',{}
        result = get_items_from_order_detail(order_info['response']['data'],order_id)
        data = {}
        if result:
            data['items'] = result[0].get('goods',[])
            data['brand_name'] = result[0].get('brand_name','')
            data['business_id'] = result[0].get('business_id','')
        else:
            update_order_comment_state(order_id, self.user_id, token, 1)
            data['items'] = []
        if not data['items']:
            update_order_comment_state(order_id, self.user_id, token, 3)
            self.error['error'] = 'invalid comment'
            self.error['errorCode'] = '30001'
            return '数据无效',{'status':0,'message':'数据无效'}
        return '',data

@view_defaults(route_name='evaluation_business_comment')
class BusinessCommentView(View):
    def __init__(self, request):
        super(BusinessCommentView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_business_comment.get')
    @check_permission
    @view_config(request_method='GET', renderer = 'json')
    @pack_data
    def get(self):
        business_id = self.request.params.get('id', '')
        flag = self.request.params.get('flag', '')
        if not business_id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}


@view_defaults(route_name='evaluation_business_score')
class BusinessScoreView(View):
    def __init__(self, request):
        super(BusinessScoreView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_business_score.get')
    @check_permission
    @view_config(request_method='GET', renderer = 'json')
    @pack_data
    def get(self):
        business_id = self.request.params.get('id', '')
        if not business_id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        data = {}
        data['score'] = get_business_score(int(business_id))
        if data['score']:
            data['id'] = business_id
        return '',data

@view_defaults(route_name='evaluation_comment_state')
class CommentStateView(View):
    def __init__(self, request):
        super(CommentStateView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_comment_state.get')
    @check_permission
    @view_config(request_method='GET', renderer = 'json')
    @pack_data
    def get(self):
        order_id = self.request.params.get('id', '')
        rec_id = self.request.params.get('rec_id', '')
        if not order_id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        data = {}
        result = get_comment_state(order_id)
        data['state'] = result
        return '',data

@view_defaults(route_name='evaluation_comment_num')
class CommentNumView(View):
    def __init__(self, request):
        super(CommentNumView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_comment_num.get')
    @check_permission
    @view_config(request_method='GET', renderer = 'json')
    @pack_data
    def get(self):
        goods_id = self.request.params.get('id', '')
        if not goods_id:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        data = {}
        attr_list = []
        goods_attr1 = {}
        goods_attr1['opName'] = 'business_id'
        goods_attr1['opValue'] = int(goods_id)
        goods_attr1['op'] = '=='
        attr_list.append(goods_attr1)
        goods_attr2 = {}
        goods_attr2['opName'] = 'review'
        goods_attr2['opValue'] = 1
        goods_attr2['op'] = '=='
        attr_list.append(goods_attr2)
        goods_attr3 = {}
        goods_attr3['opName'] = 'type'
        goods_attr3['opValue'] = 0
        goods_attr3['op'] = '=='
        attr_list.append(goods_attr3)
        result = get_goods_comment_num_public(str(attr_list))
        data['count'] = str(result)
        return '',data

@view_defaults(route_name='evaluation_detail_comments')
class DetailCommentsView(View):
    def __init__(self, request):
        super(DetailCommentsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_detail_comments.get')
    #@check_permission
    @view_config(request_method='GET', renderer = 'json')
    @pack_data
    def get(self):
        type_id = self.request.params.get('id', '')
        m_type = self.request.params.get('type', 0)
        flag = self.request.params.get('flag', '')
        if not flag:
            flag = 0
        flag = int(flag)
        from_type = self.request.params.get('from_type', 'app')
        if not type_id :
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '',{}
        m_type = 4
        comments = get_goods_commets_by_goods_id_to_app(int(type_id),int(m_type),flag, 2)
        num = get_comment_num(int(type_id))
        data = {}
        data['items'] = comments
        data['count'] = str(num)
        return '',data

@view_defaults(route_name='evaluation_shop_comments')
class ShopCommentsView(View):
    def __init__(self, request):
        super(ShopCommentsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_goods_comments.get')
    @check_permission
    @view_config(request_method='GET', renderer = 'json')
    @pack_data
    def get(self):
        type_id = self.request.params.get('id', '')
        m_type = self.request.params.get('type', 0)
        flag = self.request.params.get('start', '')
        limit = self.request.params.get('pageSize',18)
        if not flag:
            flag = 0
        flag = int(flag)
        limit = int(limit)
        from_type = self.request.params.get('from_type', 'app')
        if not type_id :
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '',{}
        comments = get_goods_commets_by_business_id(int(type_id),int(m_type),flag,limit)
        data = {}
        data['items'] = comments
        if len(comments) >= limit: 
            data['flag'] = str(flag + limit)
        return '', data

@view_defaults(route_name='evaluation_update_cache')
class UpdateCacheView(View):
    def __init__(self, request):
        super(UpdateCacheView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_update_cache.get')
    @view_config(request_method='GET', renderer = 'json')
    @pack_data
    def get(self):
        goods_id = self.request.params.get('goods_id', '')
        comment_id = self.request.params.get('comment_id', '')
        comment_num_key = 'goods_comment_num'
        if comment_id:
            del_key = 'get_comment_and_reply_list_' + str(comment_id)
            print del_key,'del_key'
            delete_cache_by_key(del_key)
        if not goods_id:
            return '',{}
        try:
            g_id = goods_id
            delete_comment_cache(g_id)
            get_goods_comment_list_cache(g_id, 0, 0, FALL_PER_PAGE_NUM, use_cache = False)
            get_goods_comment_list_cache(g_id, 1, 0, FALL_PER_PAGE_NUM, use_cache = False)
            get_goods_comment_list_cache(g_id, 2, 0, FALL_PER_PAGE_NUM, use_cache = False)
            get_goods_comment_list_cache(g_id, 4, 0, 2, use_cache = False)
            get_comment_num(g_id, use_cache = False)
        except Exception,e:
            print e
        return '',{}

#评价此接口只有内部调用
@view_defaults(route_name='evaluation_goods_comments_inner')
class GoodsCommentsInnerView(View):
    def __init__(self, request):
        super(GoodsCommentsInnerView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_goods_comments.post')
    @check_permission
    @view_config(request_method='POST', renderer = 'json')
    @pack_data
    def post(self):
        gf =  self.request.params.get('gf', '')
        gv =  self.request.params.get('gv', '')
        token =  self.request.params.get('access_token', '')
        eva_auth =  self.request.params.get('eva_auth', '')
        comments_data = self.request.params.get('data', {})
        user_id =  self.request.params.get('user_id', 0)
        datas = json.loads(comments_data)
        order_id = datas.get('order_id',0)
        user_id = datas.get('user_id',0)
            
        if not check_evaluation_legal(token, gv, gf,user_id, comments_data,eva_auth):
            self.error['error'] = 'invalid comment'
            self.error['errorCode'] = '30001'
            return '',{'status':0,'message':'数据无效'}
        if datas.get('order_id',0) == 0:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '',{'status':0,'message':'参数错误'}        
        if int(get_comment_state(order_id)) > 0:
            update_order_comment_state(order_id, user_id, token, 0)
            self.error['error'] = 'error.'
            self.error['errorCode'] = '30001'
            return '',{'status':0,'message':'您已经评价过'}        
        if user_id < 1:
            self.error['error'] = 'user is not login.'
            self.error['errorCode'] = '20001'
            return '',{'status':0,'message':'缺少用户信息'}
            
        business = {}
        business['order_id'] = datas.get('order_id',0)
        business['user_id'] = user_id
        business['business_id'] = datas.get('business_id',0)
        business['goods_ratio'] = datas.get('goods_ratio',5)
        business['serve_satisfy'] = datas.get('serve_satisfy',5)
        business['logistics_satisfy'] = datas.get('logistics_satisfy',5)
        goods_id_list = []
        goods = []
        for comment in datas['goods_comments']:
            if type(comment) == 'str':
                comment = json.loads(comment)
            goods_id_list.append(comment['goods_id'])
            comment['order_id'] = business.get('order_id',0)
            comment['user_id'] = business.get('user_id',0)
            comment['business_id'] = business.get('business_id',0)
            comment['size_type'] = comment.get('size_type','').encode('utf-8')
            comment['color'] = comment.get('color','').encode('utf-8')
            if datas.has_key('use_anonymous'):
                comment['use_anonymous'] = datas['use_anonymous']
            goods.append(generate_GoodsComment_from_dict(comment))
        bs = []
        bs.append(generate_BusinessComment_from_dict(business))
        result = add_goods_business_comment(goods, bs)
        try:
            for g_id in goods_id_list:
                delete_comment_cache(g_id)
                get_goods_comment_list_cache(g_id, 0, 0, FALL_PER_PAGE_NUM, use_cache = False)
                get_goods_comment_list_cache(g_id, 1, 0, FALL_PER_PAGE_NUM, use_cache = False)
                get_goods_comment_list_cache(g_id, 2, 0, FALL_PER_PAGE_NUM, use_cache = False)
                get_goods_comment_list_cache(g_id, 4, 0, 2, use_cache = False)
                get_comment_num(g_id, use_cache = False)
        except Exception,e:
            print e
        data = {}
        data['status'] = str(result)
        if data['status'] == '1':
            update_order_comment_state(order_id, user_id, token, 0)
        if data['status'] == '1':
            data['message'] = '评价成功'
        else:
            data['message'] = '评价失败'
        return '',data

