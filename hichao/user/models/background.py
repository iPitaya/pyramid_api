# -*- coding:utf-8 -*-
from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
    String
)

from hichao.user.models.db import (
    new_session, 
    Base,
    )

from hichao.cache.cache import deco_cache
from hichao.util.statsd_client import timeit
from hichao.util.date_util import (
    HOUR, 
    FOREVER,
    )

timer = timeit('hichao_backend.m_user_background') 


class  Background(object):
    def __init__(self, id, fdfs_name):
        self.id = id
        self.fdfs_name = fdfs_name
'''
g_background_list = [\
    Background(1,'group2/M00/1B/02/wKgBWlQ7PROAEUJqAALAckzh5cI798.jpg'),\
    Background(2,'group2/M00/1B/02/wKgBWlQ7PROAUYruAAQLeQZNS2Y134.jpg'),\
    Background(3,'group2/M00/1B/02/wKgBWlQ7PROAadOaAAUr99i1h3E249.jpg'),\
    Background(4,'group2/M00/1B/02/wKgBWlQ7PROAGAVfAALqtCznyxI405.jpg'),\
    Background(5,'group2/M00/1B/02/wKgBWlQ7PROANkKCAAPAeAWTHvE785.jpg'),\
    Background(6,'group2/M00/1B/02/wKgBWlQ7PROAKscEAAU3w_2YYi8877.jpg'),\
    Background(7,'group2/M00/1B/02/wKgBWlQ7PROAOv07AAJe2x8tQiU963.jpg'),\
    Background(8,'group2/M00/1B/02/wKgBWlQ7PRSAMwzVAATxe84I2us564.jpg'),\
    Background(9,'group2/M00/1B/02/wKgBWlQ7PRSASR2LAAStXNynTEU966.jpg'),\
    Background(10,'group2/M00/1B/02/wKgBWlQ7PRSACWrQAAOMpG4bsWE710.jpg'),\
    Background(11,'group2/M00/1B/02/wKgBWlQ7PRSAOOb7AALLKHjpNZ4166.jpg'),\
    Background(12,'group2/M00/1B/02/wKgBWlQ7PRSAfFgDAALk0YAzEdI838.jpg'),\
    Background(13,'group2/M00/1B/02/wKgBWlQ7PRWAEhYmAAHErrd5P84228.jpg'),\
    Background(14,'group2/M00/1B/02/wKgBWlQ7PRWAQh7FAAXbuPaglvY177.jpg'),\
    Background(15,'group2/M00/1B/02/wKgBWlQ7PRWAJpD6AARESzcg7LI004.jpg'),\
    Background(16,'group2/M00/1B/02/wKgBWlQ7PRWAHAqhAAbMiZ4pZDM138.jpg'),\
    Background(17,'group2/M00/1B/02/wKgBWlQ7PRWALW8IAARefMtgusc015.jpg'),\
    Background(18,'group2/M00/1B/02/wKgBWlQ7PRWANkfjAASQQ7wFIbI044.jpg')
]
'''

g_background_list = [\
    Background(1,'group2/M00/1C/A1/wKgBWVRXJMOAcImzAASnD5YVco4842.jpg'),\
    Background(2,'group2/M00/7C/22/wKgBWlRXJMOAJhsZAAYWcWw2j1k863.jpg'),\
    Background(3,'group2/M00/1C/A1/wKgBWVRXJMOARojyAAaVljqdz8k773.jpg'),\
    Background(4,'group2/M00/7C/22/wKgBWlRXJMOAVwS8AAPU2v2hL1g248.jpg'),\
    Background(5,'group2/M00/1C/A1/wKgBWVRXJMOAFVjFAAWURWG1Cr8533.jpg'),\
    Background(6,'group2/M00/7C/22/wKgBWlRXJMOABZoeAAP7xgYMwUE493.jpg'),\
    Background(7,'group2/M00/1C/A1/wKgBWVRXJMOANluKAAQl9OTQ4A4492.jpg'),\
    Background(8,'group2/M00/7C/22/wKgBWlRXJMOASdgIAAWNZR-257o633.jpg'),\
    Background(9,'group2/M00/1C/A1/wKgBWVRXJMOAfnXrAAJshdp4enM248.jpg'),\
    Background(10,'group2/M00/7C/22/wKgBWlRXJMOAB3CwAAN7QDQeQYU398.jpg'),\
    Background(11,'group2/M00/1C/A1/wKgBWVRXJMOAZJsTAAIUUSu_oI4424.jpg'),\
    Background(12,'group2/M00/7C/22/wKgBWlRXJMOAFso7AAKsulMXeiw884.jpg'),\
    Background(13,'group2/M00/1C/A2/wKgBWVRXJMOAewg0AAMZ6UH0bmQ365.jpg'),\
    Background(14,'group2/M00/7C/22/wKgBWlRXJMSAeGD5AAKp66IwjpI125.jpg'),\
    Background(15,'group2/M00/1C/A2/wKgBWVRXJMSAd7aEAAHn2g8LHJM520.jpg'),\
    Background(16,'group2/M00/7C/22/wKgBWlRXJMSAeF89AAKCVbsPtgw508.jpg'),\
    Background(17,'group2/M00/1C/A2/wKgBWVRXJMSAADCPAAIxKonUESo785.jpg'),\
    Background(18,'group2/M00/7C/22/wKgBWlRXJMSANGNQAAJI7LoNoGw001.jpg')
]

#class Background(Base):
#    __tablename__ = 'background'
#    id = Column(Integer, primary_key=True, autoincrement=True)
#    status = Column(Integer)
#    width = Column(Integer)
#    height = Column(Integer)
#    name = Column(VARCHAR(256)) 
#    fdfs_name = Column(VARCHAR(256))

@timer
def get_background(id):
    rv = None
    sess = new_session()
    try:
        #res = sess.query(Background)\
        #         .filter(Background.id == id)\
        #         .first()
        #sess.commit()
        if id > 0 and id < len(g_background_list) + 1: 
            rv = g_background_list[id-1]
    except Exception, e:
        print Exception, ':', e
        sess.rollback()
    finally:
        sess.close()
    return rv

@timer
def get_background_list(offset, limit):
    sess = new_session()
    rv = list()
    try:
        #res = sess.query(Background)\
        #          .filter(Background.status == 1)\
        #          .offset(offset)\
        #          .limit(limit)
        #sess.commit()
        #rv = res
        nBg = len(g_background_list)
        if offset < nBg and (offset+limit) <= nBg:
            rv = g_background_list[offset:offset+limit]
        elif offset < nBg and (offset+limit) > nBg:
            rv = g_background_list[offset:nBg-offset]
    except Exception, e:
        print Exception, ':', e
        sess.rollback()
    finally:
        sess.close()
        return rv

@timer
def upload_background(path):
    rv = True
    return rv
