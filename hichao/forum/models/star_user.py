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
from hichao.util.date_util import TEN_MINUTES, DAY, HOUR,MINUTE
from hichao.cache.cache import deco_cache
from hichao.user.models.user import get_user_by_id
from hichao.util.statsd_client import timeit
from hichao.base.models.base_component import BaseComponent
from hichao.base.config import (
    ROLE_FDFS_TALENT_LIST,
    ROLE_USERINFO_STARUSER_ICON,
)
from hichao.mall.models.ecshop_goods import get_brand_info_by_business_id
from hichao.forum.models import star_user_type


timer = timeit('hichao_backend.m_forum_staruser')


class StarUser(Base, BaseComponent):
    __tablename__ = 'staruser'
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(INTEGER(unsigned=True), nullable=False)
    user_desc = Column(VARCHAR(255))
    is_top = Column(INTEGER, default=0)
    editor_id = Column(INTEGER(unsigned=True))
    review = Column(TINYINT, nullable=False, default=0)
    create_ts = Column(TIMESTAMP)
    last_update_ts = Column(TIMESTAMP)
    category_id = Column(INTEGER, default=1)
    business_id = Column(INTEGER, default=0)

    def __init__(self, user_id, user_desc, is_top, editor_id, review, create_ts, last_update_ts, category_id, business_id):
        self.user_id = user_id
        self.user_desc = user_desc
        self.is_top = is_top
        self.editor_id = editor_id
        self.review = review
        self.create_ts = create_ts
        self.last_update_ts = last_update_ts
        self.category_id = category_id
        self.business_id = business_id

    def get_bind_user(self):
        return get_user_by_id(self.user_id)

    def get_component_user_name(self):
        user = self.get_bind_user()
        if not user:
            return ''
        return user.get_component_user_name()

    def get_component_user_avatar(self):
        user = self.get_bind_user()
        if not user:
            return ''
        return user.get_component_user_avatar()

    def get_component_user_description(self):
        return self.user_desc

    def get_staruser_type(self, filte_category=True):
        star_user = star_user_type.get_user_type_name(self.category_id)
        if star_user:
            if filte_category and star_user.name not in ['红人', '明星', '设计师']:
                return {}
            return {'userTypeName': star_user.name, 'followType': star_user.follow_type, 'imgUrl': star_user.img_url}
        return {}

    def get_component_user_id(self):
        return str(self.user_id)

    def get_component_staruser_roleIcons(self):
        return get_star_user_icon_by_user_id(self.user_id)

    def to_ui_action(self):
        action = {}
        action['actionType'] = 'detail'
        action['type'] = 'user'
        action['id'] = self.get_component_user_id()
        return action

    def to_lite_ui_action(self):
        return self.to_ui_action()


@timer
@deco_cache(prefix='staruser_ids', recycle=TEN_MINUTES)
def get_staruser_ids(flag, limit, use_cache=True):
    DBSession = rdbsession_generator()
    ids = DBSession.query(StarUser.id).filter(StarUser.is_top > 0).filter(StarUser.review == 1).order_by(StarUser.is_top.desc(),
                                                                                                         StarUser.last_update_ts.desc()).offset(flag).limit(limit).all()
    ids = [id[0] for id in ids]
    DBSession.close()
    return ids


@timer
@deco_cache(prefix='staruser_by_id', recycle=TEN_MINUTES)
def get_staruser_by_id(staruser_id, use_cache=True):
    DBSession = rdbsession_generator()
    staruser = DBSession.query(StarUser).filter(StarUser.id == staruser_id).first()
    DBSession.close()
    return staruser


@timer
@deco_cache(prefix='staruser_by_user_id', recycle=TEN_MINUTES)
def get_staruser_by_user_id(user_id, use_cache=True):
    DBSession = rdbsession_generator()
    res = DBSession.query(StarUser).filter(StarUser.user_id == user_id).filter(StarUser.review == 1).first()
    DBSession.close()
    return res


@timer
@deco_cache(prefix='user_is_staruser', recycle=DAY)
def user_is_staruser(user_id):
    res = 0
    DBSession = rdbsession_generator()
    usr = DBSession.query(StarUser.id).filter(StarUser.user_id == int(user_id)).filter(StarUser.review == 1).first()
    if usr:
        res = 1
    DBSession.close()
    return res


@timer
@deco_cache(prefix='staruser_business_id', recycle=TEN_MINUTES)
def get_staruser_business_id(staruser_id, use_cache=True):
    DBSession = rdbsession_generator()
    business_id = DBSession.query(StarUser.business_id).filter(StarUser.user_id == int(staruser_id)).first()
    DBSession.close()
    return business_id


@timer
def get_business_id_and_name_by_user_id(user_id):
    date = {}
    business_id = get_staruser_business_id(user_id)
    if not business_id:
        return {}
    if not business_id.business_id:
        return {}
    else:
        date['business_id'] = business_id.business_id
    brand_info = get_brand_info_by_business_id(business_id.business_id)
    if not brand_info:
        return {}
    else:
        date['business_name'] = brand_info.brand_name
        date['brand_logo'] = 'http://s.pimg.cn/' + brand_info.brand_logo
    return date


@timer
@deco_cache(prefix='star_user_icon_by_user_id', recycle=TEN_MINUTES)
def get_star_user_icon_by_user_id(user_id):
    role_icon_list = list()
    res_staruser = get_staruser_by_user_id(user_id)
    if res_staruser:
        star_user_icon = ROLE_FDFS_TALENT_LIST[int(res_staruser.category_id) - 1]
        if star_user_icon:
            role_icon_list.append(star_user_icon)
        else:
            role_icon_list.append(ROLE_USERINFO_STARUSER_ICON)
    return role_icon_list


@timer
@deco_cache(prefix='user_id_by_id', recycle=TEN_MINUTES)
def get_user_id_by_id(StarUser_id, use_cache=True):
    DBSession = rdbsession_generator()
    user_id = DBSession.query(StarUser.user_id).filter(StarUser.id == int(StarUser_id)).filter(StarUser.review == 1).first()
    DBSession.close()
    return user_id

@timer
@deco_cache(prefix='staruser_ids_by_cid', recycle = MINUTE)
def get_user_ids_by_cat_id(cat_id):
    DBSession = rdbsession_generator()
    user_ids = DBSession.query(StarUser.user_id).filter(StarUser.category_id == int(cat_id)).filter(StarUser.review == 1).all()
    user_ids = [_id[0] for _id in user_ids]
    DBSession.close()
    return user_ids

def main():
    res = get_user_id_by_id(11)
    print res

if __name__ == "__main__":
    main()
