# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        )
from hichao.third_party_share.models.db import (
        Base,
        dbsession_generator,
        )
from hichao.util.statsd_client import timeit

import time
import transaction

class ThirdPartyShare(Base):
    __tablename__ = 'third_party_share'
    id = Column('id', INTEGER, primary_key = True, autoincrement = True)
    user_id = Column(VARCHAR(64))
    type_id = Column(VARCHAR(64))
    type = Column(VARCHAR(64))
    publish_date = Column(VARCHAR(20))
    third_party = Column(VARCHAR(20))
    review = Column(INTEGER)

    def __init__(self, user_id = '', type_id = '', type = '', publish_date = str(time.time()), third_party =
            'weixin', review = 0):
        self.user_id = user_id
        self.type_id = type_id
        self.type = type
        self.publish_date = publish_date
        self.third_party = third_party
        self.review = review


@timeit('hichao_backend.m_third_party_share')
def add_third_party_share(user_id, type_id, _type, publish_date, third_party):
    third_party_share = ThirdPartyShare(user_id, type_id, _type, publish_date, third_party)
    DBSession = dbsession_generator()
    try:
        DBSession.add(third_party_share)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ex
        return 0
    finally:
        DBSession.close()
    return 1

if __name__ == '__main__':
    Base.metadata.create_all()
