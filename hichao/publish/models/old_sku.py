#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, Text, String, VARCHAR, FLOAT
from hichao.publish.models.db import dbsession_generator, Base

class OldSku(Base):
    __tablename__ = 'spider_sku'

    id = Column('spider_sku_id', Integer,primary_key=True)
    description = Column(Text)
    publish_date = Column(VARCHAR)
    editor = Column(VARCHAR)
    is_recommend = Column(Integer)
    came_from = Column('from', VARCHAR)
    tags = Column(VARCHAR)

def get_sku_by_id(id):
    DBSession = dbsession_generator()
    old_sku = DBSession.query(OldSku).get(id)
    DBSession.close()
    return old_sku

#print get_sku_by_id(404)

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

