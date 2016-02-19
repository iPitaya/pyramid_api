# -*- coding:utf-8 -*-

from sqlalchemy import (
    Column,
    INTEGER,
    VARCHAR,
    )
from sqlalchemy.dialects.mysql import TINYINT

from hichao.event.models.db import (
    Base,
    dbsession_generator_write,
    dbsession_generator,
    )

class SuperGirlsCode(Base):
    __tablename__ = 'sg_mgtv_code'
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    code = Column(VARCHAR(255), unique = True, nullable = False, index = True)
    used = Column(TINYINT, nullable = False, default = 0)

