#coding:utf-8
import zmq
import json

context = zmq.Context()
sender = context.socket(zmq.PUSH)
sender.connect("tcp://192.168.1.167:7799")

if __name__ == '__main__':
    to_uid_list = [609821,398040,453993]
    for to_uid in to_uid_list:
        input_msg = {
                  'from_uid': 428326,
                  'to_uid': 50934,
                  'action_type': 'topicDetail',
                  'content_id': 2661,
                  'text': u"""hi，美妞！恭喜你已成功申领衣橱“乐Fan星期天·第七期”清洁水精灵补水洁面乳一份，赶紧加衣橱小助手qq：2375616916，把你的快递地址偷偷告诉我，若6个工作日内没有和我取得联系，只能视为放弃哦！""",
                  }
        sender.send(json.dumps(input_msg))
