from sqlalchemy import (
        func,
        Column,
        INTEGER,
        VARCHAR,
        DECIMAL,
        BIGINT,
        )
from hichao.banner.models.db import (
        rdbsession_generator,
        Base,
        )
from sqlalchemy.dialects.mysql import TINYINT
from hichao.base.models.base_component import BaseComponent
from hichao.topic.models.topic import (
        get_topic_by_id,
        get_last_topic_ids,
        )
from hichao.cache.cache import deco_cache
from hichao.util.date_util import FIVE_MINUTES
from hichao.util.statsd_client import timeit
import time

timer = timeit('hichao_backend.m_banner')

class BannerPositionBase(object):
    id = Column(INTEGER, primary_key = True, autoincrement = True)
    type_id = Column(INTEGER, nullable = False)
    _type = Column('type', VARCHAR(64), nullable = False)
    position = Column(INTEGER, nullable = False)
    review = Column(TINYINT, nullable = False, default = 0)
    start_time = Column(BIGINT, nullable = False)
    end_time = Column(BIGINT, nullable = False)
    img_url = Column(VARCHAR(2048), nullable = True, default = '')

class BannerPosition(Base, BannerPositionBase):
    __tablename__ = 'banner_position'

class ItemBannerPosition(Base, BannerPositionBase):
    __tablename__ = 'item_banner_position'

@timer
@deco_cache(prefix = 'last_banner_ids', recycle = FIVE_MINUTES)
def get_last_banner_ids(support_tuan = 0, support_thread = 0, support_worthy = 0, support_group_sku = 0, ts = '', use_cache = True):
    DBSession = rdbsession_generator()
    if ts:
        now = int(float(ts))
    else:
        now = int(time.time())
    bps = DBSession.query(BannerPosition.position, BannerPosition.type_id,
            BannerPosition._type, BannerPosition.img_url, BannerPosition.id).filter(BannerPosition.review == 1).filter(BannerPosition.start_time <=
                    now).filter(BannerPosition.end_time >= now).order_by(BannerPosition.position.desc()).order_by(BannerPosition.id).all()
    DBSession.close()
    len_ids = len(bps)
    bps = [(int(bp[0]), int(bp[1]), str(bp[2]), str(bp[3]), int(bp[4])) for bp in bps]
    _bps = [(int(bp[1]), str(bp[2])) for bp in bps]
    if ts:
        bps.reverse()
        return bps
    if len_ids >= 6:
        ids = bps[0:6]
        ids.reverse()
    else:
        ids = get_last_topic_ids()
        _ids = []
        for i, id in enumerate(ids):
            _ids.append((int(id), 'topic'))
        ids = [None] * 6
        _ids = [id for id in _ids if id not in _bps]
        _ids = [(0, int(id[0]), str(id[1]), '', 0) for id in _ids]
        for bp in bps:
            if bp[0] > 6: continue
            if bp[2] == 'topic':
                ids[bp[0] - 1] = bp
                continue
            elif bp[2] == 'thread' and support_thread:
                ids[bp[0] - 1] = bp
                continue
            elif bp[2] == 'tuan' and support_tuan:
                ids[bp[0] - 1] = bp
                continue
            elif bp[2] == 'tuanlist' and support_tuan:
                ids[bp[0] - 1] = bp
                continue
            elif bp[2] == 'worthylist' and support_worthy:
                ids[bp[0] - 1] = bp
                continue
            elif bp[2] == 'groupsku' and support_group_sku:
                ids[bp[0] - 1] = bp
                continue
        for idx, item in enumerate(ids):
            if not item:
                item = _ids.pop(0)
                ids[idx] = item
    return ids[0:6]

@deco_cache(prefix = 'last_banners', recycle = FIVE_MINUTES)
def get_last_banners_by_type(_type, limit = 3):
    cls = get_cls_by_type(_type)
    DBSession = rdbsession_generator()
    now = int(time.time())
    bns = DBSession.query(cls.position, cls.type_id, cls._type, cls.img_url, cls.id).filter(cls.review == 1).filter(cls.start_time <=
        now).filter(cls.end_time >= now).order_by(cls.position).order_by(cls.id).limit(limit)
    DBSession.close()
    bns = [(int(bn[0]), int(bn[1]), str(bn[2]), str(bn[3]), str(bn[4])) for bn in bns]
    return bns

def get_cls_by_type(_type):
    if _type == 'item':
        return ItemBannerPosition

if __name__ == '__main__':
    pass

