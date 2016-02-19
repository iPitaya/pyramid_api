# -*- codinf:utf-8 -*-

from sqlalchemy import (
        Column,
        VARCHAR,
        TIMESTAMP,
        )
from sqlalchemy.dialects.mysql import (
        INTEGER,
        TINYINT,
        )
from hichao.forum.models.db import (
        Base,
        dbsession_generator,
        engine,
        )
from hichao.user.models.user import get_user_by_id
from hichao.util.statsd_client import timeit

class Report(Base):
    __tablename__ = 'report'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    _type = Column('type', VARCHAR(255))
    type_id = Column(INTEGER(unsigned = True))
    ts = Column(TIMESTAMP)
    content = Column(VARCHAR(1000))
    review = Column(TINYINT, default = 1)
    from_uid = Column(INTEGER(unsigned = True), default = 0)
    from_ip = Column(INTEGER(unsigned = True), default = 0)

    def __init__(self, _type, type_id, ts, content, from_uid, from_ip, review = 1):
        self._type = _type
        self.type_id = type_id
        self.ts = ts
        self.content = content
        self.from_uid = from_uid
        self.from_ip = from_ip
        self.review = review

@timeit('hichao_backend.m_forum_report')
def add_report(_type, type_id, ts, content, from_uid, from_ip, review = 1):
    report = (_type, type_id, ts, content, from_uid, from_ip, review)
    try:
        conn = engine.connect()
        res = conn.execute("insert into report (type, type_id, ts, content, from_uid, from_ip, review)\
                values (%s, %s, %s, %s, %s, inet_aton(%s), %s);", report)
        last_id = res.lastrowid
    except Exception, ex:
        print Exception, ex
        return 0
    finally:
        conn.close()
    return last_id
    

