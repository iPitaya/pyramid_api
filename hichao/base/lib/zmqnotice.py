#coding:utf-8
import zmq
import ujson

def send_notice(msg_type, content_id, from_uid, token='4B21D298EF307D04'):
    return None
    #try:
    #    context = zmq.Context()
    #    sender = context.socket(zmq.PUSH)
    #    sender.connect("tcp://192.168.1.167:7788")
    #    msg = {'token':token, 'type':msg_type, 'content_id':content_id, 'from_uid':from_uid}
    #    sender.send(ujson.dumps(msg))
    #except Exception, ex:
    #    print ex
    #else:
    #    pass
    #finally:
    #    pass
