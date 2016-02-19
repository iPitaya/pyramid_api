# -*- coding:utf8 -*-


from icehole_client.tuangou_client import (
        get_buying_info,
        get_buying_sku_info,
        get_buying_id_with_sku_id,
        )

from icehole_client.files_client  import  get_image_filename

from hichao.util.cps_util import *
from hichao.util.image_url import (
        build_image_url,
        get_item_normal_path,
        )

from hichao.util.cps_util import (
        get_cps_url,
        )

from hichao.tuangou.models.image_url import (
        build_tuan_sku_image_url,
        )

from hichao.util.date_util import (
        MINUTE,
        FIVE_MINUTES,
        HOUR,
        DAY,
        WEEK,
        )

from hichao.cache.cache import (
        deco_cache,
        )

from hichao.tuangou.models.attend_util import (
        build_attend_count,
        build_attend_count_lite,
        )
from hichao.util.statsd_client import timeit

from hichao.sku.models.sku  import get_sku_id_by_source_sourceid

from hichao.base.config import (
        TUANGOU_SKU_FDFS_REMAI_ICON,
        TUANGOU_SKU_FDFS_TUIJIAN_ICON,
        TUANGOU_SKU_FDFS_YESHI_ICON,
        )    

import time
from  datetime import datetime
from sqlalchemy import (
        Column,
        VARCHAR,
        DECIMAL,
        INTEGER,
        DateTime,
        )

from hichao.tuangou.models.db import (
        slave_dbsession_generator,
        Base,
        )

from hichao.tuangou.config import (
        NO_TUANGOU,
        TUANGOU_NORMAL,
        TUANGOU_ABNORMAL
        )
timer = timeit('hichao_backend.m_tuangou_tuangousku')

class TuanGou(Base):
    __tablename__="tuangou"

    id = Column(INTEGER, primary_key = True)
    title = Column(VARCHAR(128), nullable=False)
    publish_date = Column(DateTime, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date= Column(DateTime, nullable=False)
    hangtag_img_url = Column(VARCHAR(255), nullable=False)
    detail_img_url = Column(VARCHAR(255), nullable=False)
    scroll_img_url =Column(VARCHAR(255), nullable=False)
    web_img_url = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(1024), nullable=False)
    review = Column(INTEGER, nullable=False)
    discount = Column(VARCHAR(128), nullable=False)
    category = Column(VARCHAR(32), nullable=False)
    user_id = Column(INTEGER, nullable=False, default=0)
    user_name = Column(VARCHAR(32), nullable=False)
    pos = Column(INTEGER, nullable=False)
    is_drop = Column(INTEGER, nullable=False)
    showtime = Column(DateTime, nullable=False)


class TuanGouSku(Base):
    __tablename__="tuangou_sku"

    id = Column(INTEGER, primary_key=True)
    source_id = Column(VARCHAR(128), nullable=False)
    color = Column(VARCHAR(32), nullable=False)
    discount_price = Column(DECIMAL(20,2), nullable=False)
    title = Column(VARCHAR(255), nullable=False)
    publish_date = Column(DateTime, nullable=False)
    description = Column(VARCHAR(1024), nullable=False)
    discount = Column(VARCHAR(128), nullable=False)
    category = Column(VARCHAR(32), nullable=False)
    review = Column(INTEGER, nullable=False)
    original_price = Column(DECIMAL(20,2), nullable=False)
    user_id = Column(INTEGER, nullable=False)
    source = Column(VARCHAR(45), nullable=False)
    img_url = Column(VARCHAR(2048), nullable=False)
    url = Column(VARCHAR(2048), nullable=False)
    sku_id = Column(INTEGER)

class TuanGouSkuRela(Base):
    __tablename__="tuangou_to_sku"

    id = Column(INTEGER, primary_key=True)
    tuangou_id = Column(INTEGER, nullable=False)
    tuangou_sku_id = Column(INTEGER, nullable=False)
    pos = Column(INTEGER, nullable=False)


@timer
def get_buying_sku_datablock(item_id):
    data = build_tuangou_sku_by_id(item_id)
    return data

@timer
def build_component_tuangou_sku(item):
    discount = item.discount
    if discount.find('.')<0:
        discount +='折'
    else:
        discount = discount[0:discount.find('.')+2]+'折'
    item_id = get_sku_id_by_source_sourceid(item.source, item.source_id)
    action={}
    action['actionType'] = 'webview'
    action['title'] = '单品详情'
    action['titleStyle'] = cps_title_styles_dict[get_cps_key(item.source, item.url)]
    action['means'] = 'push'
    action['webUrl'] = get_cps_url(item.source, item.source_id)
    if not action['webUrl']:
        action['webUrl'] = item.url
    action['trackValue']= str(item_id)
    payload = {}
    payload['eventname'] = 'detail_c'
    payload['source']=item.source
    payload['source_id']=str(item.source_id)
    payload['sku_id']=str(item_id)
    action['payload'] = payload
    com={}
    com['type']='tuangou_sku'
    com['tag']=str(item.review)
    com['action']=action
    com['componentType']="tuanItemCell"
    com['picUrl']=build_tuan_sku_image_url(item.img_url)
    com['title']=item.title
    com['id']=str(item.id)
    com['price']=str(item.discount_price)
    com['priceOrig']=str(item.original_price)
    com['description']=item.title
    com['discount']=discount
    com['peopleCount']=""
    com['publish_date'] = item.publish_date
    data={}
    data['component']=com

    return data

@timer
def build_component_tuangou_sku_lite(item):
    discount = item.discount
    discount = format((float(item.discount_price)/float(item.original_price))*10,'.1f')
    if float(discount) >= 10.0:
        discount = '不打折'
    elif discount.find('.')<0:
        discount +='折'
    else:
        discount = discount[0:discount.find('.')+2]+'折'
    action={}
    item_id = get_sku_id_by_source_sourceid(item.source, item.source_id)
    action['actionType']='detail'
    action['id']=str(item_id)
    action['source']=item.source
    action['sourceId']=str(item.source_id)
    action['type'] = 'sku'
    action['trackValue']= str(item_id)
    payload = {}
    payload['source']=item.source
    payload['source_id']=str(item.source_id)
    payload['eventname'] = 'detail_c'
    payload['sku_id']=str(item_id)
    action['payload'] = payload
    image_width = '100'
    image_height = '100'
    image_size = get_image_filename('tuangou',item.img_url)
    if str(image_size.width) != '0' and str(image_size.height) != '0':
        image_width = str(image_size.width)
        image_height = str(image_size.height)
    action['width'] = image_width
    action['height'] = image_height
    com={}
    com['type']='tuangou_sku'
    com['action']=action
    com['componentType']="tuanItemCell"
    com['picUrl']=build_tuan_sku_image_url(item.img_url)
    com['title']=item.title
    com['id']=str(item.id)
    com['price']=str(item.discount_price)
    com['priceOrig']=str(item.original_price)
    com['description']=item.title
    com['discount']=discount
    com['peopleCount']=""
    com['publish_date'] = item.publish_date
    com['tag']=str(item.review)
    if com['tag'] == '1':
        com['picIcon']=TUANGOU_SKU_FDFS_REMAI_ICON
    elif com['tag'] == '2':
        com['picIcon']=TUANGOU_SKU_FDFS_TUIJIAN_ICON
    elif com['tag'] == '6':
        com['picIcon']=TUANGOU_SKU_FDFS_YESHI_ICON
    else:
        com['picIcon']=''
    data={}
    data['component']=com

    return data


@timer
@build_attend_count()
@deco_cache(prefix="component_tuangou_sku", recycle = MINUTE)
def build_tuangou_sku_by_id(item_id, res=None, use_cache=True):
    if not res:
        res = get_buying_sku_info(item_id)
    buying_id = get_buying_id_with_sku_id(item_id)
    if buying_id!=0:
        buying_info = get_buying_info(buying_id)
    else:
        buying_info = None
    start_time =  buying_info.start_date if buying_info and buying_info.id!=-1 else 0
    end_time = buying_info.end_date if buying_info and buying_info.id!=-1 else 0
    res = build_component_tuangou_sku(res)
    res['component']['startTime']= str(int(start_time))
    res['component']['endTime']= str(int(end_time))
    res['component']['tuanId']= str(buying_info.id)
    res['component']['action']['tuanId']= str(buying_info.id)
    return res

@timer
@build_attend_count_lite()
@deco_cache(prefix="component_tuangou_sku_lite", recycle = MINUTE)
def build_tuangou_sku_by_id_lite(item_id, res=None, use_cache=True):
    if not res:
        res = get_buying_sku_info(item_id)
    buying_id = get_buying_id_with_sku_id(item_id)
    if buying_id!=0:
        buying_info = get_buying_info(buying_id)
    else:
        buying_info = None
    if not buying_info:
        return None
    start_time =  buying_info.start_date if buying_info and buying_info.id!=-1 else 0
    end_time = buying_info.end_date if buying_info and buying_info.id!=-1 else 0
    res = build_component_tuangou_sku_lite(res)
    res['component']['startTime']= str(int(start_time))
    res['component']['endTime']= str(int(end_time))
    res['component']['tuanId']= str(buying_info.id)
    return res

#根据source_ids判断是否团购,是否有效
@timer
def get_if_tuangou(source_ids):
    DBSession = slave_dbsession_generator()
    res = {str(source_id):NO_TUANGOU for source_id in source_ids}
    now = datetime.now()
    source_id_tuangou_ids = DBSession.query(TuanGouSku.source_id, TuanGouSkuRela.tuangou_id).join(TuanGouSkuRela,TuanGouSku.id==TuanGouSkuRela.tuangou_sku_id).filter(TuanGouSku.source_id.in_(source_ids)).all()
    tuangou_ids_origin = list(set(st[1] for st in source_id_tuangou_ids))
    if not tuangou_ids_origin:
        return res
    tuangou_ids_query_raw =  DBSession.query(TuanGou.id).filter(TuanGou.id.in_(tuangou_ids_origin)).filter(TuanGou.start_date<=now).filter(TuanGou.end_date>=now).filter(TuanGou.review==2).all()
    DBSession.close()
    tuangou_ids_query = [tuan_id[0] for tuan_id in tuangou_ids_query_raw]
    for st in source_id_tuangou_ids:
        if st[1] in tuangou_ids_query:
            res[str(st[0])]=TUANGOU_NORMAL
    return res

#根据source_ids判断是否团购,是否有效 单个接口
@timer
#@deco_cache(prefix = 'tuangou_sku_id_by_source_id', recycle = WEEK)
def get_tuangou_sku_id_by_source_id(source_id, use_cache=True):
    DBSession = slave_dbsession_generator()
    tuangou_sku_ids = DBSession.query(TuanGouSku.id).filter(TuanGouSku.source_id==source_id).all()
    DBSession.close()
    tuangou_sku_ids = [tuangou_sku_id[0] for tuangou_sku_id in tuangou_sku_ids]
    return tuangou_sku_ids

@timer
#@deco_cache(prefix = 'tuangou_id_by_tuangou_sku_id', recycle = HOUR)
def get_tuangou_id_by_tuangou_sku_id(tuangou_sku_id, use_cache=True):
    DBSession = slave_dbsession_generator()
    tuangou_id = DBSession.query(TuanGouSkuRela.tuangou_id).filter(TuanGouSkuRela.tuangou_sku_id==tuangou_sku_id).first()
    DBSession.close()
    return tuangou_id[0]


@timer
#@deco_cache(prefix = 'tuangou_id_exsit_by_tuangou__id', recycle = HOUR)
def get_tuangou_info_by_tuangou_id(tuangou_id, use_cache=True):
    DBSession = slave_dbsession_generator()
    now = datetime.now()
    tuangou_id = DBSession.query(TuanGou.id).filter(TuanGou.id==tuangou_id).filter(TuanGou.start_date<=now).filter(TuanGou.end_date>=now).filter(TuanGou.review==2).first()
    DBSession.close()
    if tuangou_id:
        return tuangou_id[0]
    else:
        return ''
