# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        )
from hichao.winner_info.models.db import (
        Base,
        dbsession_generator,
        rdbsession_generator,
        )
import transaction

class WinnerAttachinfo(Base):
    __tablename__ = 'topic_winner_attachinfo'
    topic_id = Column(INTEGER, primary_key = True, nullable = False)
    type = Column(VARCHAR(32))
    user_id = Column(INTEGER, primary_key = True, nullable = False)
    attachment = Column(VARCHAR(256))

    def __init__(self, topic_id, user_id, attachment, type = 'topic'):
        self.topic_id = topic_id
        self.type = type
        self.user_id = user_id
        self.attachment = attachment


def add_winner_attachinfo(topic_id, user_id, attachment, type = 'topic'):
    info = WinnerAttachinfo(topic_id, user_id, attachment, type)
    DBSession = dbsession_generator()
    try:
        DBSession.add(info)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        return 0
    finally:
        DBSession.close()
    return 1

def update_winner_attachinfo(topic_id, user_id, attachment, type = 'topic'):
    if get_winner_attachinfo(topic_id, user_id, type):
        DBSession = dbsession_generator()
        try:
            DBSession.query(WinnerAttachinfo).filter(WinnerAttachinfo.topic_id ==
                    topic_id).filter(WinnerAttachinfo.user_id ==
                            user_id).update({WinnerAttachinfo.attachment:attachment})
            transaction.commit()
        except Exception, ex:
            transaction.abort()
            print Exception, ex
            return 0
        finally:
            DBSession.close()
        return 1
    else:
        return add_winner_attachinfo(topic_id, user_id, attachment, type)

def get_winner_attachinfo(topic_id, user_id, type = 'topic'):
    RDBSession = rdbsession_generator()
    user_info = RDBSession.query(WinnerAttachinfo).filter(WinnerAttachinfo.topic_id ==
            topic_id).filter(WinnerAttachinfo.user_id == user_id).filter(WinnerAttachinfo.type == type).first()
    RDBSession.close()
    return user_info

