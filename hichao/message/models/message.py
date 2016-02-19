# -*- coding:utf-8 -*-

from icehole_client.message_client import (
        AllClient,
        ThreadClient,
        CommentClient,
        ForumClient,
        EventClient,
        OfficialClient,
        CustomerClient,
        )
from icehole_interface.message.ttypes import CustomerMessage
from hichao.user.models.user import get_user_by_id
from hichao.forum.models.thread import get_thread_by_id
from hichao.comment.models.sub_thread import (
        get_subthread_by_id,
        get_forum_comment_count_by_floor,
        )
from hichao.upload.models.image import get_image_by_id
from hichao.util.cps_util import get_cps_key, cps_title_styles_dict
from hichao.util.content_util import rebuild_content
from hichao.base.config import (
        APP_LOGO,
        DEFAULT_TITLE_STYLE_PIC,
        )
from hichao.util.statsd_client import timeit
from hichao.util.content_util import split_with_url
import time
import copy
import requests
import urllib2,urllib
import json
from hichao.message.config import CUSTOMER_ONLINE_URL

timer = timeit('hichao_backend.m_message')

tp = ['event_msg', 'forum_msg', 'comment_msg','customer_msg']
id = ['-1', '-2', '-3', '-4']

class MSG_TYPE:
    ALL_MSG = 'all'
    CUSTOMER_MSG = 'customer_msg'
    COMMENT_MSG = 'comment_msg'
    THREAD_MSG = 'thread_msg'
    NOTICE_MSG = 'notice_msg'
    FORUM_MSG = 'forum_msg'
    EVENT_MSG = 'event_msg'
    values = [ALL_MSG, CUSTOMER_MSG, COMMENT_MSG, THREAD_MSG, NOTICE_MSG,FORUM_MSG,EVENT_MSG]

MESSAGE_TYPE_NUM_DICT={
    "customer_msg":"customerTotal",
    "comment_msg":"commentTotal",
    "thread_msg":"threadTotal",
    "forum_msg":"forumTotal",
    "event_msg":"eventTotal",
}

tp_id_dict = dict(zip(tp, id))
id_tp_dict = dict(zip(id, tp))

@timer
def get_customer_message(user_id):
    client = CustomerClient()
    msgs = client.list_by_shop(user_id)
    data = []
    for msg in msgs:
        ui = {}
        com = build_component_customer_msg(msg)
        if com:
            ui['component'] = com
            ui['message_type'] = 'customer_msg'
        if ui: 
            data.append(ui)
    if data:
        data = build_component_customer_isOnline(data)
        data = sorted(data, key=lambda com:com['component']['datetime'], reverse=True)
    return data

@timer
def build_component_customer_msg(msg):
    com = {}
    if msg:
        com['messageCount'] = str(msg.count)
        com['componentType'] = 'messageGroupList'
        com['datetime'] = msg.ts
        if msg.msg_type == 1:
            com['description'] = '【图片】'
        else:
            com['description'] = msg.content
        com['name'] = msg.shop_name
        com['picUrl'] = msg.shop_avatar
        com['id'] = str(msg.shop_id)
        com['messageGroupId'] = tp_id_dict['customer_msg']
        action = {}
        action['actionType'] = 'customer'
        action['type'] = 'customer'
        action['id'] = str(msg.shop_id)
        action['title'] = msg.shop_name
        com['action'] = action
    return com

@timer
def build_component_customer_isOnline(data):
    data_online_state = []
    business_ids = [item['component']['id'] for item in data]
    business_id2ui = {item['component']['id']:item for item in data}
    online_result_state = get_customer_online_state(business_ids)
    for business_id, ui in business_id2ui.items():
        ui['component']['isOnline'] = str(online_result_state[business_id])
        data_online_state.append(ui)
    return data_online_state

@timer
def get_customer_online_state(business_ids):
    url = CUSTOMER_ONLINE_URL
    headers = {
        'Cookie':'PHPSESSID=ed012b9vt17gg1986aod1l6et1',
    }
    str_business_ids = ','.join(business_ids)
    query = {}
    query["version"] = "2.0"
    query["message_type"] = 70
    query["business_id_list"] = str_business_ids
    isOnline = 0
    business_id2online_state = {business_id:isOnline for business_id in business_ids}
    res = requests.post(url,data="data:"+json.dumps(query),headers=headers,verify=True)
    result = res.json()
    if result.has_key("state_list"):
        state_list = result['state_list']
        for bid, current_platform in state_list.items():
            is_online_curr = 0
            for item in current_platform['platform']:
                if item["state"] == 0:
                    is_online_curr = 1
                    break
            if not is_online_curr:
                for item in current_platform['current']:
                    if item["state"] == 0:
                        is_online_curr = 1
                        break
            business_id2online_state[str(bid)] = is_online_curr
    return business_id2online_state

@timer
def get_all_message(user_id, flag, limit):
    client = AllClient()
    msgs = client.msg_list(user_id)
    data = []
    for msg in msgs:
        ui = {}
        com = build_component_msg(msg)
        if com:
            ui['component'] = com
            ui['message_type'] = msg.msg_type
        if ui: data.append(ui)
    return data

@timer
def get_one_classify_message(data_items, msg_type):
    data = []
    for items in data_items:
        if items['message_type'] == msg_type:
            data.append(items)
    return data
         
@timer
def get_message_num_per_classify(data_items, data):
    for items in data_items:
        if items['message_type'] in MESSAGE_TYPE_NUM_DICT.keys():
            if items['component']:
                key_total = MESSAGE_TYPE_NUM_DICT[items['message_type']]
                data[key_total] = int(data[key_total]) + int(items['component']['messageCount'])
    return data

@timer
def build_component_msg(msg):
    com = {}
    if msg:
        if msg.msg_type == 'event_msg':
            if msg.last_user_id == 100:
                tm = time.strptime(msg.ts, '%Y-%m-%d %H:%M:%S')
                start = time.strptime('2015-03-30 11:30:00', '%Y-%m-%d %H:%M:%S')
                end = time.strptime('2015-03-30 15:41:00', '%Y-%m-%d %H:%M:%S')
                if tm > start and tm < end:
                    return {}
        com['messageCount'] = str(msg.count)
        com['componentType'] = 'messageGroupList'
        if not msg.ts:
            com['datetime'] = u'刚刚'
        else:
            com['datetime'] = msg.ts
        if not msg.content:
            com['description'] = ''
        else:
            content_list = split_with_url(msg.content)
            count = len(content_list)
            desc = ''
            for i in range(count):
                if i % 2 == 0:
                    desc = desc + content_list[i]
                else:
                    desc = desc + '「网页链接」'
            com['description'] = desc
        if msg.msg_type == 'event_msg':
            com['messageGroupId'] = tp_id_dict[msg.msg_type]
            com['name'] = u'活动通知'
            com['picUrl'] = APP_LOGO
        elif msg.msg_type == 'forum_msg':
            com['messageGroupId'] = tp_id_dict[msg.msg_type]
            com['name'] = u'系统通知'
            com['picUrl'] = APP_LOGO
        elif msg.msg_type == 'thread_msg':
            thread_id = msg.item_id
            com['messageGroupId'] = str(thread_id)
            user = get_user_by_id(msg.last_user_id)
            if user:
                com['name'] = user.get_component_user_name()
                com['picUrl'] = user.get_component_user_avatar()
            else:
                com['name'] = ''
                com['picUrl'] = APP_LOGO
        elif msg.msg_type == 'comment_msg':
            com['messageGroupId'] = tp_id_dict[msg.msg_type]
            com['name'] = u'回复我的'
            user = get_user_by_id(msg.last_user_id)
            if user:
                com['picUrl'] = user.get_component_user_avatar()
            else:
                com['picUrl'] = APP_LOGO
            comment = get_subthread_by_id(msg.content)
            if comment:
                com['description'] = comment.content
            else:
                com['description'] = ''
        action = build_message_action(msg)
        action['title'] = com['name']
        com['action'] = action
    return com

@timer
def build_message_action(msg):
    action = {}
    if msg.msg_type == 'thread_msg':
        action['actionType'] = 'detail'
        action['type'] = 'thread'
        action['id'] = str(msg.item_id)
        comment = get_subthread_by_id(msg.custom_id)
        if comment:
            action['flag'] = str(comment.floor - 4)            # 用于前端跳转到具体楼层
        action['clearMsgNum'] = '1'     # 前端会在跳转到帖子详情时传入，清掉消息数
    else:
        action['actionType'] = 'list'
        action['type'] = 'msg'
        action['id'] = tp_id_dict[msg.msg_type]
    return action

@timer
def get_group_message(group_id, user_id, flag, limit):
    tp = id_tp_dict.get(group_id, '')
    items = []
    if not tp: return items
    method = ''
    build_method = ''
    client = ''
    if tp == 'event_msg':
        client = EventClient()
        method = client.user_event_list
        build_method = build_event_msg
    elif tp == 'forum_msg':
        client = ForumClient()
        method = client.forum_list
        build_method = build_forum_msg
    elif tp == 'comment_msg':
        client = CommentClient()
        method = client.comment_list
        build_method = build_comment_msg
    msgs = method(user_id, flag, limit)
    for msg in msgs:
        if tp == 'event_msg':
            try:
                msg = int(msg)
                if msg >= 404 and msg <= 153702:
                    client.user_event_rm(int(user_id), msg)
                    continue
                if msg in [398, 400, 401, 402]:
                    client.user_event_rm(int(user_id), msg)
                    continue
                msg = client.event_by_id(msg, int(user_id))
            except Exception, ex:
                print Exception, ex
                msg = None
            if not msg: continue
        com = build_method(msg)
        if com: items.append(com)
    return items

@timer
def get_event_item_message(user_id, item_id, flag, limit):
    client = EventClient()
    key = '{0}_{1}'.format(user_id, item_id)
    items = []
    msgs = client.event_pm_list(key, flag, limit)
    for msg in msgs:
        com = build_event_item_msg(msg, user_id)
        items.append(com)
    return items

@timer
def build_event_item_msg(msg, user_id):
    ui = {}
    com = {}
    com['componentType'] = 'eventItemMessageCell'
    user = get_user_by_id(msg.from_uid)
    com['userAvatar'] = user.get_component_user_avatar()
    com['publishDate'] = msg.ts
    if int(user_id) == int(msg.from_uid):
        com['mySelf'] = '1'
        com['description'] = rebuild_content(msg.content, font_color = '255,255,255,255')
    else:
        com['description'] = rebuild_content(msg.content, font_color = '178,146,160,255')
    ui['component'] = com
    return ui

@timer
def build_event_msg(msg):
    ui = {}
    com = {}
    com['componentType'] = 'eventMessageCell'
    com['id'] = str(msg.id)
    user = get_user_by_id(msg.user_id)
    if user:
        com['userName'] = user.get_component_user_name()
        com['userAvatar'] = user.get_component_user_avatar()
    else:
        com['userName'] = ''
        com['userAvatar'] = APP_LOGO
    com['publishDate'] = msg.ts
    content_list = split_with_url(msg.content)
    count = len(content_list)
    desc = ''
    for i in range(count):
        if i % 2 == 0:
            desc = desc + content_list[i]
        else:
            desc = desc + '「网页链接」'
    com['description'] = desc
    com['messageCount'] = str(msg.count)
    action = {}
    action['actionType'] = 'list'
    action['type'] = 'msgEvent'
    action['groupId'] = tp_id_dict['event_msg']
    action['id'] = str(msg.id)
    com['action'] = action
    ui['component'] = com
    return ui

@timer
def build_forum_msg(msg):
    ui = {}
    com = {}
    com['componentType'] = 'forumMessageCell'
    com['id'] = str(msg.id)
    #user = get_user_by_id(msg.from_uid)
    #if user:
    #    com['userName'] = user.get_component_user_name()
    #    com['userAvatar'] = user.get_component_user_avatar()
    #else:
    #    com['userName'] = ''
    #    com['userAvatar'] = APP_LOGO
    com['userName'] = u'明星小助手'
    com['userAvatar'] = APP_LOGO
    com['publishDate'] = msg.ts
    com['description'] = msg.content
    ui['component'] = com
    return ui

@timer
def build_comment_msg(msg):
    ui = {}
    com = {}
    com['id'] = str(msg.id)
    comment = get_subthread_by_id(msg.comment_id)
    if not comment: return {}
    com['userName'] = comment.get_component_user_name()
    com['userAvatar'] = comment.get_component_user_avatar()
    com['publishDate'] = comment.get_component_publish_date()
    com['description'] = comment.get_component_content()
    com['reply'] = comment.get_component_reply()
    action = {}
    action['actionType'] = 'detail'
    action['type'] = 'thread'
    action['id'] = str(comment.item_id)
    count = get_forum_comment_count_by_floor(comment.item_id, comment.floor)
    action['flag'] = str(count)
    com['action'] = action
    com['componentType'] = 'commentMessageCell'
    ui['component'] = com
    return ui

@timer
def build_official_msg(msg):
    ui = {}
    com = {}
    com['componentType'] = 'officialMessageCell'
    com['id'] = str(msg.id)
    com['title'] = msg.title
    com['publishDate'] = msg.ts
    com['description'] = u'点击查看详细内容'
    img = get_image_by_id(msg.image_id)
    if img:
        com['picUrl'] = img.get_component_pic_detail_url()
    else:
        com['picUrl'] = APP_LOGO
    action = {}
    action['actionType'] = 'webview'
    title_style = copy.deepcopy(cps_title_styles_dict[get_cps_key('', '')])
    title_style['text'] = msg.title
    action['titleStyle'] = title_style
    action['means'] = 'push'
    action['webUrl'] = 'http://www.hichao.com/wap/message/{0}'.format(msg.id)
    share_action = {}
    share_action['type'] = 'webpage'
    share_action['actionType'] = 'share'
    share_action['trackValue'] = 'officialMessage_{0}'.format(msg.id)
    share_action['typeId'] = str(msg.id)
    share = {}
    share['description'] = msg.title
    share['title'] = msg.title
    share['shareType'] = 'webpage'
    share['id'] = str(msg.id)
    share['detailUrl'] = action['webUrl']
    share['picUrl'] = com['picUrl']
    share_action['share'] = share
    action['shareAction'] = share_action
    com['action'] = action
    ui['component'] = com
    return ui


@timer
def delete_message(group_id, user_id, item_id):
    res = 0
    if not group_id:
        client = AllClient()
        res = client.rm_all(user_id)
        cc = CustomerClient()
        cc.rm_all(user_id)
    else:
        tp = id_tp_dict.get(str(group_id), '')
        rm_method = ''
        if not tp:
            client = ThreadClient()
            res = client.rm(user_id, group_id)
        else:
            if tp == 'event_msg':
                client = EventClient()
                if item_id:
                    res = client.user_event_rm(user_id, item_id)
                else:
                    res = client.user_event_rm_all(user_id)
            elif tp == 'forum_msg':
                client = ForumClient()
                if item_id:
                    res = client.rm(user_id, item_id)
                else:
                    res = client.rm_all(user_id)
            elif tp == 'comment_msg':
                client = CommentClient()
                if item_id:
                    res = client.rm(item_id)
                else:
                    res = client.rm_all(user_id)
            elif tp == 'customer_msg':
                client = CustomerClient()
                if item_id:
                    res = client.rm(user_id,item_id)
                else:
                    res = client.rm_all(user_id)
    return res

@timer
def get_official_message(platform, flag, limit):
    client = OfficialClient()
    status = 1
    msgs = client.list_by_platform_and_status(platform, status, flag, limit)
    items = []
    for msg in msgs:
        com = build_official_msg(msg)
        if com: items.append(com)
    return items

@timer
def event_reply(user_id, item_id, content):
    client = EventClient()
    key = '{0}_{1}'.format(user_id, item_id)
    user_id = int(user_id)
    res = client.event_pm_new(key, user_id, user_id, int(item_id), str(content), str(int(time.time())))
    return res

@timer
def reset_notify(user_id, msg_type):
    user_id = int(user_id)
    if msg_type == MSG_TYPE.ALL_MSG:
        status = AllClient().clean_up(user_id)
        if status:
            status = CustomerClient().clean_up(user_id)
        return status
    elif msg_type == MSG_TYPE.CUSTOMER_MSG:
        return CustomerClient().clean_up(user_id)
    elif msg_type == MSG_TYPE.COMMENT_MSG:
        return CommentClient().clean_up(user_id)
    elif msg_type == MSG_TYPE.THREAD_MSG:
        return ThreadClient().clean_up(user_id)
    elif msg_type == MSG_TYPE.NOTICE_MSG:
        status = EventClient().clean_up(user_id)
        if status:
            statu = ForumClient().clean_up(user_id)
        return status
    elif msg_type == MSG_TYPE.FORUM_MSG:
        return ForumClient().clean_up(user_id)
    elif msg_type == MSG_TYPE.EVENT_MSG:
        return EventClient().clean_up(user_id)

@timer
def get_event_total_num(items):
    eventTotal = 0
    for item in items:
        if item['component']:
            eventTotal = eventTotal + int(item['component']['messageCount'])
    return eventTotal

@timer
def clean_up_message_num(user_id , data_num):
    msg_num = int(data_num['customerTotal']) + int(data_num['commentTotal']) + int(data_num['threadTotal']) + int(data_num['forumTotal']) + int(data_num['eventTotal'])
    if msg_num == 0:
        if AllClient().count(user_id) > 0:
            reset_notify(user_id,'all')

@timer
def get_customer_unread_count(user_id):
    cli = CustomerClient()
    msgs = cli.list_by_shop(user_id)
    count = 0
    for msg in msgs:
        if msg: count = count + int(msg.count)
    return count


if __name__ == '__main__':
    pass

