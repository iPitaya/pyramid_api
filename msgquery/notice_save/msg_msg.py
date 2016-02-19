#coding:utf-8
import sys
sys.path.append('..')
from save_mysql import _initialize_component, _topic_action, _star_action, _thread_action, insert_notice
from notice_num import msg_all_new
import ujson
import tomdb
import zmq

def get_db():
    DB = tomdb.Connection('192.168.1.166', 'msgcenter', 'xuchuan', 'xuchuan', use_charset="utf8mb4")
    return DB

def _get_msg_description(text):
    return [{'component':{'componentType':'msgText','text':text}}]

def _get_msg_action(action_type, main_id):
    if action_type == 'topicDetail':
        action, pic_url = _topic_action(main_id)
    elif action_type == 'starDetail':
        action, pic_url = _star_action(main_id)
    elif action_type == 'subjectDetail':
        action, pic_url = _thread_action(main_id)
    else:
        action, pic_url = None, None
    return action, pic_url

def _insert_all_msg(component, ts):
    data = ujson.dumps(component)
    #sql_dict = {
    #            'sql': 'INSERT INTO msgcenter.notice_all (content) VALUES (%s, %s)',
    #            'value': (data, ts)
    #}
    #_execute(cp_167, sql_dict)
    DB = get_db()
    item_id = DB.execute("INSERT INTO msgcenter.notice_all (content, ts) VALUES (%s, FROM_UNIXTIME(%s))", data, ts)
    print item_id, data, ts
    DB.close()
    msg_all_new(item_id, int(ts))

def make_all_msg(input_msg):
    from_uid = input_msg['from_uid']
    content_id = input_msg['content_id']
    action_type = input_msg['type']
    text = input_msg['text']
    component, save_time = _initialize_component(from_uid)
    description = _get_msg_description(text)
    component['component']['description'] = description
    main_id = content_id
    action, pic_url = _get_msg_action(action_type, main_id)
    component['component']['actions'][1] = action
    component['component']['picUrl'] = pic_url
    _insert_all_msg(component, save_time)

def make_one_msg(input_msg):
    from_uid = input_msg['from_uid']
    to_uid = input_msg['to_uid']
    content_id = input_msg['content_id']
    action_type = input_msg['action_type']
    text = input_msg['text']
    notice_type = "msg_msg"
    component, save_time = _initialize_component(from_uid)
    description = _get_msg_description(text)
    component['component']['description'] = description
    main_id = content_id
    action, pic_url = _get_msg_action(action_type, main_id)
    if action and pic_url:
        component['component']['actions'][1] = action
        component['component']['picUrl'] = pic_url
        insert_notice(ujson.dumps(component), to_uid, save_time, notice_type)

if __name__ == '__main__':
    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://*:7799")
    print "ready"
    while True:
        recv = receiver.recv()
        try:
            recv_dict = ujson.loads(recv)
        except Exception, ex:
            print ex
        else:
            if recv_dict.has_key("from_uid") and recv_dict.has_key("to_uid") and recv_dict.has_key("action_type") and recv_dict.has_key("content_id") and recv_dict.has_key("text"):
                make_one_msg(recv_dict)

    # input_msg = {
    #             'from_uid': 100,
    #             'type': 'starDetail',
    #             'content_id': 60627,
    #             'text': u'筒子们，我是专题，我也是吊牌；我是单品，我也是明星图。我就是明星小助手',
    #             }
#    to_uid_list = [446207,409544,337420,385050,398646,423713,536979,531013,420472,558349,258699,564262,427010,561778,616156,574793,468270,248150,538079,309370,270232,587687,557666,419882,547071,426698,433062,570105,544967,433836]
#    for to_uid in to_uid_list:
#        input_msg = {
#                   'from_uid': 428326,
#                   'to_uid': to_uid,
#                   'action_type': 'topicDetail',
#                   'content_id': 2613,
#                   'text': u"""hi，美妞！恭喜你已成功申领衣橱“乐Fan星期天·第六期”人面桃花雅润舒养睡眠面膜一份，赶紧加衣橱小助手qq：2375616916，把你的快递地址偷偷告诉我，若6个工作日内没有和我取得联系，只能视为放弃哦！""",
#                   }
#        make_one_msg(input_msg)

