# -*- coding:utf-8 -*-

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
    rdbsession_generator,
)
from hichao.util.date_util import HOUR,MINUTE
from hichao.cache.cache import deco_cache
from hichao.user.models.user import get_user_by_id
from hichao.forum.models.star_user import get_staruser_by_id,get_user_id_by_id
from hichao.upload.models.image import get_image_by_id
from hichao.util.statsd_client import timeit
from hichao.base.models.base_component import BaseComponent
timer = timeit('hichao_backend.m_forum_hotstaruser')
import time
from datetime import datetime
from hichao.follow.models.follow import get_user_follow_status

class HotStarUser(Base, BaseComponent):
    __tablename__ = 'hot_staruser'
    id = Column(INTEGER, nullable=False, primary_key=True, autoincrement=True)
    staruser_id = Column(INTEGER, nullable=False)
    thread_ids = Column(VARCHAR(32), nullable=False)
    img_ids = Column(VARCHAR(32), nullable=False)
    create_ts = Column('ts', TIMESTAMP)
    review = Column(TINYINT)
    type = Column(INTEGER)

    def get_bind_user(self):
        return get_staruser_by_id(self.staruser_id)
    
    def get_component_user_id(self):
        user_id = get_user_id_by_id(self.staruser_id)
        user_id = user_id[0] if user_id else 0
        return str(user_id)

    def get_component_user_name(self):
        user = self.get_bind_user()
        if user:
            name = user.get_component_user_name()
            if name:
                return str(name)
        else:
            return ''

    def get_bind_imgs_to_thread_id(self):
        if not self.img_ids:
            return {}
        img_ids = self.img_ids.split(',')
        thread_ids = self.thread_ids.split(',')
        zip_list = zip(thread_ids,img_ids)
        res = {}
        for item in zip_list:
            img = get_image_by_id(item[1])
            if img:
            #需要判断image是否为None
                thread_id = item[0]
                res[thread_id] = img
        return res
    
    def get_component_pic_url(self):
        img_com= []
        img_dict = self.get_bind_imgs_to_thread_id()
        if len(img_dict) == 0:
            return img_com
        else:
            for key,value in img_dict.items():
                if value:
                    _img = value.get_component_pic_fall_url(crop = True)
                    ui = {}
                    component = {}
                    component['componentType'] = 'cell'
                    action = {
                            'actionType':'detail',
                            'type':'thread',
                            'id':key,
                             }
                    component['action'] = action
                    component['picUrl'] = _img
                    ui['width'] = '100'
                    ui['height'] = '100'
                    ui['component'] = component
                    img_com.append(ui)
            return img_com

    def get_component_user_avatar(self):
        user = self.get_bind_user()
        user_avatar = user.get_component_user_avatar()
        if user_avatar:
            return user_avatar
        else:
            return ''
    
    def get_component_user_description(self):
        staruser = self.get_bind_user()
        user_des =  staruser.get_component_user_description()
        if user_des:
            return user_des
        else:
            return ''
   
    def get_component_icon(self):
        user = self.get_bind_user()
        user_icon = user.get_component_staruser_roleIcons()
        return user_icon if user_icon else ''
        '''
        role_icon_list = []
        res_staruser = self.get_bind_user()
        if res_staruser:
            #star_user_icon = get_star_user_icon(int(res_staruser.category_id))
            star_user_icon = ROLE_FDFS_TALENT_LIST[int(res_staruser.category_id)-1]
            staruser_icon_item = STARUSER_ICON
            if star_user_icon:
                role_icon_list.append(staruser_icon_item)
            else:
                role_icon_list.append(ROLE_USERINFO_STARUSER_ICON)
        if len(role_icon_list) > 0:
            return role_icon_list        
        else:
            return ''
        '''
    def get_component_flag(self):
        return self.create_ts.strftime('%Y-%m-%d %H:%M:%S')

    def to_ui_action(self):
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'user'
        action['id'] = self.get_component_user_id()
        action['userName'] = self.get_component_user_name()
        action['userAvatar'] = self.get_component_user_avatar()
        return action

    # 判断用户是否关注这个用户
    def check_user_follow_status(self,app_user_id):
        result = 0
        if app_user_id > 0:
            result = get_user_follow_status(app_user_id,self.staruser_id)
        return result

@timer
@deco_cache(prefix='staruser_ids', recycle= MINUTE)
def get_staruser_ids(use_cache=True):
    DBSession = rdbsession_generator()
    staruser_ids = DBSession.query(
        HotStarUser.staruser_id).filter(HotStarUser.review > 0).order_by(HotStarUser.create_ts.desc()).all()
    DBSession.close()
    staruser_ids = [id[0] for id in staruser_ids]
    return staruser_ids

@timer
@deco_cache(prefix='threas_ids_by_staruser_id', recycle=HOUR)
def get_thread_ids_by_staruser_id(staruser_id, use_cache=True):
    DBSession = rdbsession_generator()
    thread_ids = DBSession.query(
        HotStarUser.thread_ids).filter(
        HotStarUser.staruser_id == int(staruser_id)).first()
    DBSession.close()
    return thread_ids


@timer
@deco_cache(prefix='hot_staruser_ids', recycle=HOUR)
def get_hot_staruser_ids(flag, num=20, use_cache=True):
    DBSession = rdbsession_generator()
    staruser_ids = DBSession.query(
        HotStarUser.staruser_id).filter(
            #HotStarUser.create_ts < flag).filter(
            HotStarUser.review > 0).order_by(
            HotStarUser.review.asc()).order_by(
            HotStarUser.create_ts.desc()).offset(flag).limit(num).all()
    DBSession.close()
    staruser_ids = [id[0] for id in staruser_ids]
    return staruser_ids

@timer
@deco_cache(prefix='hot_staruser_ids_by_type_id', recycle=HOUR)
def get_hot_staruser_ids_by_type_id(type_id, flag, num=20, use_cache=True):
    DBSession = rdbsession_generator()
    staruser_ids = DBSession.query(
        HotStarUser.staruser_id).filter(
            HotStarUser.type == type_id).filter(
            HotStarUser.review > 0).order_by(
            HotStarUser.review.asc()).order_by(
            HotStarUser.create_ts.desc()).offset(flag).limit(num).all()
    DBSession.close()
    staruser_ids = [id[0] for id in staruser_ids]
    return staruser_ids


def get_hot_staruser_by_id(hot_staruser_id, use_cache=True):
    DBSession = rdbsession_generator()
    hot_staruser = DBSession.query(HotStarUser).filter(
        HotStarUser.staruser_id == hot_staruser_id).first()
    DBSession.close()
    return hot_staruser

def main():
    res = get_hot_staruser_ids(0,18)
    print res
    for id in res:
        hot_staruser = get_hot_staruser_by_id(id)
        print "################"
        print hot_staruser.get_component_pic_url()

 
if __name__ == '__main__':
    main()
