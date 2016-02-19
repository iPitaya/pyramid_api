# -*- coding:utf-8 -*-
#!/usr/bin/env python

import sys

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relation
from zope.sqlalchemy import ZopeTransactionExtension
import transaction

from hichao.forum.models.thread import Thread
from hichao.collect.models.transport import collect_thread_to_star
from hichao.star.models.star import Star
from models import *

import zmq
import json
from hichao.base.config import MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT
#MYSQL_HOST="127.0.0.1"
#MYSQL_PASSWD=""
#MYSQL_USER="root"

SQLALCHEMY_CONF_URL = 'mysql+pymysql://%s:%s@%s:%s/' % (MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT)

def dbsession_generator(database_name):
    Base = declarative_base()
    engine = create_engine(SQLALCHEMY_CONF_URL+database_name, pool_recycle = 60)
    Base.metadata.bind = engine
    DBSession = scoped_session(sessionmaker(extension = ZopeTransactionExtension(), bind = engine))
    return DBSession()


def thread_to_star(star_id):
    #insert comment to star_comment
    forum_db=dbsession_generator('forum')
    star=None
    thread_id=-1

    try:
        star=forum_db.query(ThreadStar).filter(ThreadStar.star_id==star_id)

        if star[0].review!=0:
            return False

        thread_id=star[0].thread_id
        star_id=star[0].star_id

        comment_db=dbsession_generator('comment')
        fc=comment_db.query(ThreadComment).filter(ThreadComment.thread_id==thread_id)
        for f in fc:
            sc=StarComment(f.id,f.content,f.from_uid,f.to_uid,f.comment_id,f.floor,f.review,f.ts)
            comment_db.add(sc)
    except Exception,e:
        print e
        return False

    #change thread_star review to 1
    star.update({ThreadStar.review:1})

    transaction.commit()
    #thread collect to star
    collect_thread_to_star(thread_id,star_id)
    #send message to notice

    #context = zmq.Context()
    #sender = context.socket(zmq.PUSH)
    #sender.connect("tcp://192.168.1.169:7788")
    #
    #star_db=dbsession_generator('star')
    #star_detail=star_db.query(Star).filter(Star.star_id==star_id).one()

    #msg={"token":"4B21D298EF307D04","type":"thread_2star_msg",'content_id':str(thread_id),'from_uid':str(0),'to_uid':str(star_detail.user_id)}
    #sender.send(json.dumps(msg))
    return True
    
if __name__=="__main__":
    thread_to_star(202168)
