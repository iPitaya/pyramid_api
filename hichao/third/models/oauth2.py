# -*- coding: utf-8 -*-
from time import time
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, Text, String
from hichao.third.models.db import dbsession_generator, Base
import transaction

class Oauth2Token(Base):
    __tablename__ = 'Oauth2Token'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    access_token = Column(String(60))
    refresh_token = Column(String(60))
    third_party = Column(String(10))
    time = Column(BigInteger)

    def __init__(self):
        if not Base.metadata.bind.has_table(self.__tablename__):
            self.metadata.create_all()

    def can_admin(self, user_id):
        return self.user_id == user_id


def third_party_oauth2_token_new(user_id, access_token, 
                                third_party, refresh_token=None):
    oauth2 = Oauth2Token()
    oauth2.user_id = user_id
    oauth2.access_token = access_token 
    oauth2.refresh_token= refresh_token 
    oauth2.third_party = third_party 
    oauth2.time = int(time())
    try:
        DBSession = dbsession_generator()
        DBSession.add(oauth2)
        _id = oauth2.id
        transaction.commit()
    except Exception, ex:
        print Exception, ex
        #DBSession.rollback()
        transaction.abort()
        return 0
    finally:
        DBSession.close()
    return _id


if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
