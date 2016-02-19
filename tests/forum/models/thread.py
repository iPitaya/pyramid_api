#-*- coding:utf-8 -*-
import mock

#class TestSession(object):
#    def __init__(self):
#        self._params = [1,2,3,4,5,6]
#
#    def first(self):
#        return self._params[0]
#
#    def all(self):
#        return self._params
#
#    def update(self,index,value):
#        self._params[index] = value

from sqlalchemy.orm.session import Session
from sqlalchemy.orm.query import Query

patcher_session = mock.patch.object(Session,'delete')
patcher_query_delete = mock.patch.object(Query,'delete')
patcher_query_update = mock.patch.object(Query,'update')

_session = patcher_session.start()
_query_delete = patcher_query_delete.start()
_query_update = patcher_query_update.start()

_session.return_value = 1
_query_delete.return_value = 1
_query_update.return_value = 1

t = Session()
q1 = t.query()
#print t.first()
#print t.all()
print t.delete(1,21)
print q1.delete(1,21)
print q1.update(1,21)
#print t.all()
patcher_session.stop()
patcher_query_delete.stop()
patcher_query_update.stop()




