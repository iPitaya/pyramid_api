# -*- coding:utf-8 -*-
import os,sys
import time
import ujson
from notice_num import notice_rm,notice_count,msg_all_ts_by_uid_new,thread_user_count

#sys.path.append("/hichao_backend/")

from pyramid.view import view_defaults,view_config
from models import get_notices,get_star_comment_count,get_thread_comment_count

from hichao.util.pack_data import pack_data
from hichao.base.views.view_base import View
from hichao.topic.models.topic import get_topic_by_id
from hichao.util.component_builder import build_component_banner_item
from hichao.app.views.oauth2 import check_permission

@view_defaults(route_name = 'msgcenter')
class MsgCenter(View):
    def __init__(self, request):
        super(MsgCenter, self).__init__()
        self.request = request

    @check_permission
    @view_config(request_method = 'GET', renderer = 'json')
    @pack_data
    def get(self):
        to_uid=self.user_id
        print to_uid
        category=self.request.params.get('category', '')
        print category
        flag=self.request.params.get('flag', '0')
        try:
            flag_n=int(flag)
        except:
            flag_n=0

        #last_ts=int(self.request.params.get('last_ts','0'))

        print "flag_n=",flag_n
        notices,time_now = get_notices(str(to_uid),category,flag_n,20)
        print "notices size:",len(notices)
        data = {}
        data['items'] = []

        for notice in notices:
            t=ujson.loads(notice)

            try:
                for action in t['component']['actions']:
                    if action['actionType'] == 'subjectDetail':
                        action['title']=''
            except:
                pass

            action=t['component']['actions'][1]
            action_type=action['actionType']
            try:
                id=action['id']
                print "id:",id
            except Exception,e:
                print "id:",e
                id=0

            try:
                print "collectcount:",category
                action['collectionCount']=str(thread_user_count(id))
            except Exception,e:
                print "collectionCount:",e
                action['collectionCount']='0'
            try :
                action['commentCount']=str(get_thread_comment_count(id))
                print "commentCount:",get_thread_comment_count(id)
            except Exception,e:
                print "commentCount:",e
                action['commentCount']='0'

            data['items'].append(t)
        if len(notices)>=20:
            data['flag']=str(flag_n+1)

        data['ts']=time_now
        
        print "notice rm",to_uid,category
        try:
            notice_rm(to_uid,category)
            msg_all_ts_by_uid_new(to_uid,time_now)
        except Exception,e:
            print e
            pass

        return '', data
