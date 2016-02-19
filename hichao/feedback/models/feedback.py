# -*- coding:utf-8 -*-

from sqlalchemy import (
    Column,
    INTEGER,
    BIGINT,
    VARCHAR,
    TEXT,
    func,
    )
from hichao.feedback.models.db import (
    Base,
    dbsession_generator,
    )
from hichao.base.models.base_component import BaseComponent
from hichao.util.statsd_client import timeit
import transaction

class Feedback(Base, BaseComponent):
    __tablename__ = 'feedback'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    user_id = Column(INTEGER, nullable = True)
    platform = Column(VARCHAR(64), nullable = False)
    app_name = Column(VARCHAR(64), nullable = False)
    app_channel = Column(VARCHAR(32), nullable = True)
    version = Column(VARCHAR(32), nullable = False)
    email = Column(VARCHAR(64), nullable = True)
    feedback = Column(TEXT, nullable = False)
    publish_date = Column(BIGINT, nullable = False)

    def __init__(self, user_id, platform, app_name, app_channel, version, email, feedback, publish_date):
        self.user_id = user_id
        self.platform = platform
        self.app_name = app_name
        self.app_channel = app_channel
        self.version = version
        self.email = email
        self.feedback = feedback
        self.publish_date= publish_date

@timeit('hichao_backend.m_feedback')
def add_feedback(user_id, platform, app_name, app_channel, version, email, feedback, publish_date):
    try:
        feedback = Feedback(user_id, platform, app_name, app_channel, version, email, feedback, publish_date)
        DBSession = dbsession_generator()
        DBSession.add(feedback)
        transaction.commit()
    except:
        transaction.abort()
        return 0
    finally:
        DBSession.close()
    return 1

if __name__ == '__main__':
    if not Base.metadata.bind.has_table('feedback'):
        Base.metadata.create_all()

