#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, Text, String, VARCHAR, FLOAT
from hichao.publish.models.db import dbsession_generator, Base

class OldWodfanSku(Base):
    __tablename__ = 'sku'

    id = Column('sku_id', Integer,primary_key=True)
    url = Column(VARCHAR(256), nullable = False)
    height = Column(Integer)
    width = Column(Integer)

def get_wodfan_sku_by_id(id):
    DBSession = dbsession_generator()
    old_wodfan_sku = DBSession.query(OldWodfanSku).get(id)
    DBSession.close()
    return old_wodfan_sku

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

