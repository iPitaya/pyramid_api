# -*- coding:utf-8 -*-

from pyramid.view import (
        view_defaults,
        view_config,
        )
from hichao.base.views.view_base import View
from hichao.base.config import (
        FALL_PER_PAGE_NUM,
        APP_LOGO,
        )
from hichao.util.pack_data import pack_data
from hichao.app.views.oauth2 import check_permission
from hichao.message.models.message import (
        get_all_message,
        get_group_message,
        get_official_message,
        get_event_item_message,
        get_customer_unread_count,
        delete_message,
        id_tp_dict,
        tp_id_dict,
        event_reply,
        get_one_classify_message,
        get_message_num_per_classify,
        reset_notify,
        get_event_total_num,
        clean_up_message_num,
        )
from icehole_client.message_client import EventClient
from hichao.util.content_util import (
        rebuild_content,
        filter_tag,
        )
from hichao.util.statsd_client import statsd
from hichao.message.models.message import  get_customer_message, MSG_TYPE
import time

@view_defaults(route_name = 'message')
class MessageView(View):
    def __init__(self, request):
        super(MessageView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_message.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        uid = int(self.user_id)
        if not uid or uid <= 0:
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return '', {}
        flag = self.request.params.get('flag', '')
        first_time = 0
        if flag == '': first_time = 1
        flag = int(flag) if flag else 0
        group_id = self.request.params.get('group_id', '')
        item_id = self.request.params.get('item_id', '')
        item_id = int(item_id) if item_id else 0
        data = {}
        if not group_id:
            data['items'] = get_all_message(uid, flag, FALL_PER_PAGE_NUM)
            customer_data = get_customer_message(uid)
            if customer_data:
                for c_data in customer_data:
                    data['items'].append(c_data)
        else:
            tp = id_tp_dict.get(group_id, '')
            if tp == 'event_msg':
                item_id = self.request.params.get('item_id', '')
                item_id = int(item_id) if item_id else 0
                if item_id:
                    if item_id >= 404 and item_id <= 153702:
                        data['items'] = []
                    elif item_id in [398, 400, 401, 402]:
                        data['items'] = []
                    else:
                        data['items'] = get_event_item_message(uid, item_id, flag, FALL_PER_PAGE_NUM)
                        if first_time:
                            event = EventClient().event_by_id(item_id)
                            fake_dialog = {}
                            com = {}
                            com['componentType'] = 'eventItemMessageCell'
                            com['userAvatar'] = APP_LOGO
                            com['description'] = rebuild_content(event.content, font_color = '178,146,160,255')
                            com['publishDate'] = event.ts
                            fake_dialog['component'] = com
                            data['items'].insert(0, fake_dialog)
                else:
                    data['items'] = get_group_message(group_id, uid, flag, FALL_PER_PAGE_NUM)
                    data['eventTotal'] = str(get_event_total_num(data['items']))
                num = len(data['items'])
                if item_id and first_time:
                    flag = flag + num - 1
                else:
                    flag = flag + num
            else:
                data['items'] = get_group_message(group_id, uid, flag, FALL_PER_PAGE_NUM)
                num = len(data['items'])
                flag = flag + num
            data['flag'] = str(flag)
        return '', data

    @statsd.timer('hichao_backend.r_message.delete')
    @check_permission
    @view_config(request_method = 'DELETE', renderer = 'json')
    @pack_data
    def delete(self):
        group_id = self.request.params.get('group_id', '')
        group_id = int(group_id) if group_id else 0
        item_id = self.request.params.get('item_id', '')
        item_id = int(item_id) if item_id else 0
        uid = int(self.user_id)
        if not uid or uid <= 0:
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return '', {}
        res = delete_message(group_id, uid, item_id)
        if not res:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
        return '', {}

@view_defaults(route_name = 'official_message')
class OfficialMessageView(View):
    def __init__(self, request):
        super(OfficialMessageView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_official_message.get')
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        platform = self.request.params.get('gf', 'iphone')
        flag = self.request.params.get('flag', '')
        flag = int(flag) if flag else 0
        data = {}
        data['lts'] = str(int(time.time()))
        data['items'] = get_official_message(platform, flag, FALL_PER_PAGE_NUM)
        if len(data['items']) >= FALL_PER_PAGE_NUM:
            flag = flag + FALL_PER_PAGE_NUM
            data['flag'] = str(flag)
        return '', data

@view_defaults(route_name = 'message_reply')
class MessageReplyView(View):
    def __init__(self, request):
        super(MessageReplyView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_message_reply.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        user_id = int(self.user_id)
        if user_id <= 0:
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return '', {}
        group_id = self.request.params.get('group_id', '')
        tp = id_tp_dict.get(group_id, '')
        group_id = int(group_id) if group_id else 0
        if not group_id:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return '', {}
        item_id = self.request.params.get('item_id', '')
        content = self.request.params.get('content', '')
        content = filter_tag(content)
        res = 0
        if tp == 'event_msg':
            res = event_reply(user_id, item_id, str(content))
        if res <= 0:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
        return '', {}


@view_defaults(route_name = 'message_classify')
class MessageClassifyView(View):
    def __init__(self, request):
        super(MessageClassifyView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_message_classify.get')
    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        uid = int(self.user_id)
        if not uid or uid <= 0:
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return '', {}
        msg_type = self.request.params.get('msg_type', '')
        if msg_type not in MSG_TYPE.values:
            self.error['error'] = 'parameter  error'
            self.error['errorCode'] = '10001'
            return '', {}
        flag = self.request.params.get('flag', '')
        flag = int(flag) if flag else 0
        data = {}
        data['items'] = []
        data_num = {}
        data_num['customerTotal'] = 0
        data_num['commentTotal'] = 0
        data_num['threadTotal'] = 0
        data_num['forumTotal'] = 0
        data_num['eventTotal'] = 0
        customer_unread_count = get_customer_unread_count(uid)
        data_num['customerTotal'] = str(customer_unread_count)
        data_items = get_all_message(uid, 0, FALL_PER_PAGE_NUM)
        data_num = get_message_num_per_classify(data_items, data_num)

        if msg_type == 'comment_msg':
            group_id = tp_id_dict.get(msg_type,'')
            if group_id != '':
                comment_data = get_group_message(group_id, uid, flag, FALL_PER_PAGE_NUM)
                for comment_item in comment_data:
                    comment_item['component']['messageGroupId'] = str(group_id)
                    data['items'].append(comment_item)
        elif msg_type == 'customer_msg':
            customer_data = get_customer_message(uid)
            if customer_data:
                for c_data in customer_data:
                    data['items'].append(c_data)
        elif msg_type == 'notice_msg':
            result = get_one_classify_message(data_items, 'forum_msg')
            if result:
                for item in result:
                    data['items'].append(item)
            result = get_one_classify_message(data_items, 'event_msg')
            if result:
                for item in result:
                    data['items'].append(item)
        else:
            data['items'] = get_one_classify_message(data_items, msg_type)

        num = len(data['items'])
        if num >= FALL_PER_PAGE_NUM and msg_type != 'customer_msg':
            data['flag'] = str(flag + num)
        data['customerTotal'] = str(data_num['customerTotal'])
        data['commentTotal'] = str(data_num['commentTotal'])
        data['threadTotal'] = str(data_num['threadTotal'])
        data['noticeTotal'] = str(int(data_num['forumTotal']) + int(data_num['eventTotal']))
        clean_up_message_num(uid , data_num)
        return '', data

@view_defaults(route_name = 'message_reset_notify')
class MessageResetNotifyView(View):
    def __init__(self, request):
        super(MessageResetNotifyView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_message_reset_notify.post')
    @check_permission
    @view_config(request_method = 'POST', renderer = 'json')
    @pack_data
    def post(self):
        msg_type = self.request.params.get('msg_type', '')
        if not msg_type or msg_type not in MSG_TYPE.values:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '', {}
        uid = int(self.user_id)
        if not uid or uid <= 0:
            self.error['error'] = 'Permission denied.'
            self.error['errorCode'] = '40001'
            return '', {}
        res = reset_notify(uid, msg_type)
        if not res:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
        return '', {}

