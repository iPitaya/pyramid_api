#coding:utf-8
import zmq

context = zmq.Context()

receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:7788")

sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:3000")

print "ready"
while True:
    recv = receiver.recv()
    sender.send(recv)