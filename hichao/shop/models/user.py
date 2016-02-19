# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        DECIMAL,
        VARCHAR,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.shop.models.db import (
        dbsession_generator,
        Base,
        )
from hichao.member.config import MAX_RANK
from hichao.base.config import MEMBER_RANKS
from hichao.util.statsd_client import timeit

timer = timeit('hichao_backend.m_shop_user')

class User(Base):
    __tablename__ = 'ecs_users'
    id = Column('user_id', INTEGER, primary_key = True)
    user_id = Column('user_name', VARCHAR(60))
    user_rank = Column(TINYINT, nullable = False, default = 0)
    user_money = Column(DECIMAL(10, 2, asdecimal = False), nullable = False, default = 0)
    is_demotion = Column(TINYINT, nullable = False, default = 0)        # 0：未降过级，1：已降过级。

    def has_demoted(self):
        return 1 if self.is_demotion else 0

    def get_rank(self):
        return self.user_rank

    def get_next_rank(self):
        if self.user_rank < MAX_RANK:
            return self.user_rank + 1
        else:
            return MAX_RANK

    def get_component_ec_user_id(self):
        return self.id

    def get_component_user_id(self):
        return str(self.user_id)

    def get_component_user_rank(self):
        return 'v{0}'.format(self.user_rank)

    def get_component_user_money(self):
        if self.user_money < 0:
            self.user_money = 0
        return str(self.user_money) if self.user_money else '0'

    def get_component_user_next_rank(self):
        return 'v{0}'.format(self.get_next_rank())

    def get_component_user_rank_icon(self):
        return MEMBER_RANKS.get(self.get_rank(), '')

@timer
def get_ec_user_by_user_id(user_id):
    DBSession = dbsession_generator()
    user = DBSession.query(User).filter(User.user_id == str(user_id)).first()
    DBSession.close()
    return user

