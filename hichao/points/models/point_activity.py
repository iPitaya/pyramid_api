#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import transaction
from sqlalchemy import(
    Column,
    String,
    TIMESTAMP,
    DATETIME,
    func,
    Index,
    text,
    desc,
)
from sqlalchemy.dialects.mysql import INTEGER
from hichao.points.models.db import (
    point_dbsession_generator,
    dbsession_generator,
    Base,
    engine,
)


class PointActivity(Base):
    __tablename__ = 'point_activity'
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(INTEGER(unsigned=True), nullable=False)
    activity_id = Column(INTEGER(unsigned=True), nullable=False)
    item_id = Column(INTEGER(unsigned=True), nullable=False)
    method = Column(String(255), nullable=False, server_default="new")
    ts = Column(TIMESTAMP(timezone=False),
                nullable=False, server_default=func.current_timestamp())
    __table_args__ = (Index("user_id", "activity_id"), )


def point_activity_new(user_id, activity_id, item_id, ts, method):
    DBSession = point_dbsession_generator()
    try:
        ts_datetime = datetime.datetime.fromtimestamp(ts)
        point_activity = PointActivity(
            user_id=user_id, activity_id=activity_id, item_id=item_id, method=method, ts=ts_datetime)
        DBSession.add(point_activity)
        transaction.commit()
    except Exception, ex:
        transaction.abort()
        print Exception, ':', ex
        return 0
    finally:
        DBSession.close()
    return 1

if __name__ == "__main__":
    metadata = Base.metadata
    metadata.create_all(engine)
