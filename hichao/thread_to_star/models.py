# -*- coding:utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        TEXT,
        BIGINT,
        func,
        TIMESTAMP,
        )
from sqlalchemy.dialects.mysql import TINYINT

Base = declarative_base()

class ThreadStar(Base):
    __tablename__ = "thread_star"

    id = Column(INTEGER, primary_key = True, autoincrement = True)
    thread_id = Column(INTEGER, nullable = False)
    star_id = Column(INTEGER, nullable = False)
    review = Column(TINYINT)
    ts = Column(BIGINT, nullable = False)

    def __init__(self,thread_id,star_id,review,ts):
        self.thread_id = thread_id
        self.star_id = star_id
        self.review = review
        self.ts=ts

class StarComment(Base):
    __tablename__="star_comment"
     
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    star_id = Column(INTEGER, nullable = False)
    content=Column(VARCHAR(4096), nullable = False)
    from_uid=Column(INTEGER, nullable = False)
    to_uid=Column(INTEGER, nullable = False)
    comment_id=Column(INTEGER, nullable = False)
    floor=Column(INTEGER, nullable = False)
    review = Column(TINYINT)
    ts = Column(BIGINT, nullable = False)

    def __init__(self,star_id,content,from_uid,to_uid,comment_id,floor,review,ts):
        self.star_id=star_id
        self.content=content
        self.from_uid=from_uid
        self.to_uid=to_uid
        self.comment_id=comment_id
        self.floor=floor
        self.review=review
        self.ts=ts

class ThreadComment(Base):
    __tablename__="thread_comment"
     
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    thread_id = Column(INTEGER, nullable = False)
    content=Column(VARCHAR(4096), nullable = False)
    from_uid=Column(INTEGER, nullable = False)
    to_uid=Column(INTEGER, nullable = False)
    comment_id=Column(INTEGER, nullable = False)
    floor=Column(INTEGER, nullable = False)
    review = Column(TINYINT)
    ts = Column(BIGINT, nullable = False)

    def __init__(self,thread_id,content,from_uid,to_uid,comment_id,floor,review,ts):
        self.thread_id=thread_id
        self.content=content
        self.from_uid=from_uid
        self.to_uid=to_uid
        self.comment_id=comment_id
        self.floor=floor
        self.review=review
        self.ts=ts
