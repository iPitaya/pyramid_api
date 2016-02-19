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
import time
import transaction

class UserActivityInfo(Base):
    __tablename__ = 'user_activity_info'
    id = Column('id', INTEGER, primary_key = True, autoincrement = True)
    user_id = Column(VARCHAR(64), unique=True, default="", nullable=False)
    name = Column(VARCHAR(64), default="", nullable=False)
    cellphone = Column(VARCHAR(64), default="", nullable=False)
    email = Column(VARCHAR(64), default="", nullable=False)
    address = Column(VARCHAR(64), default="", nullable=False)
    publish_date = Column(VARCHAR(20), default="", nullable=False)

    def __init__(self, user_id = '', name = '', cellphone = '', email = '', address = '', publish_date = '',
    review=0):
        if not publish_date:
            publish_date = str(time.time())
        self.user_id = user_id
        self.name = name
        self.cellphone = cellphone
        self.email = email
        self.address = address
        self.publish_date = publish_date
        self.review = review


def add_user_activity_info(user_id, name, cellphone, email, address, publish_date = ''):
    if not publish_date:
        publish_date = str(time.time())
    user_info = UserActivityInfo(str(user_id), name, cellphone, email, address, publish_date)
    DBSession = dbsession_generator()
    try:
        DBSession.add(user_info)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        return 0
    finally:
        DBSession.close()
    return 1

def update_user_activity_info(user_id, name, cellphone, email, address, publish_date = ''):
    if not publish_date:
        publish_date = str(time.time())
    if get_user_activity_info(user_id):
        try:
            DBSession = dbsession_generator()
            DBSession.query(UserActivityInfo).filter(UserActivityInfo.user_id ==
                    str(user_id)).update({UserActivityInfo.name:name, UserActivityInfo.cellphone:cellphone,
                        UserActivityInfo.email:email, UserActivityInfo.address:address,
                        UserActivityInfo.publish_date:publish_date})
            transaction.commit()
        except Exception, ex:
            transaction.abort()
            print Exception, ex
            return 0
        finally:
            DBSession.close()
        return 1
    else:
        return add_user_activity_info(user_id, name, cellphone, email, address, publish_date)

def get_user_activity_info(user_id):
    RDBSession = rdbsession_generator()
    user_info = RDBSession.query(UserActivityInfo).filter(UserActivityInfo.user_id == str(user_id)).first()
    RDBSession.close()
    return user_info

