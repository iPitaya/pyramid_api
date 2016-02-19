# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        DECIMAL,
        VARCHAR,
        TEXT,
        func,
        )
from hichao.sku.models.db import (
        Base,
        rdbsession_generator,
        )
from hichao.base.config import (
        CHANNEL_TAOBAO,
        CHANNEL_TMALL,
        CHANNEL_DICT,
        )
from hichao.base.models.base_component import BaseComponent
from hichao.util.formatter import format_price
from hichao.base.config.ui_action_type import SKU_DETAIL
from hichao.base.config.ui_component_type import SKU_CELL
from sqlalchemy.dialects.mysql import TINYINT
import json

class SpiderSku(Base, BaseComponent):
    __tablename__ = 'spider_sku'
    sku_id = Column('spider_sku_id', INTEGER, primary_key = True)
    url = Column(VARCHAR(2048))
    curr_price = Column(DECIMAL(20,2))
    title = Column(VARCHAR(1024))
    sales = Column(INTEGER, default = 0)
    link = Column(VARCHAR(1024))
    source = Column(VARCHAR(127))
    source_id = Column(VARCHAR(127))
    description = Column(TEXT)
    favor = Column(INTEGER, default = 0)
    info = Column(VARCHAR(128))
    brand_id = Column(INTEGER)
    sku_type = Column(TINYINT)
    intro = Column(VARCHAR(255))

    def __getitem__(self, key):
        return getattr(self, key)

    def get_component_id(self):
        return str(self.sku_id)

    def get_component_pic_url(self):
        return self.get_normal_pic_url()

    def get_component_price(self):
        return format_price(self.curr_price)

    def get_component_width(self):
        return '3'

    def get_component_height(self):
        return '4'

    def get_normal_pic_url(self):
        return self.url

    def get_component_description(self):
        return self.description

    def get_component_info(self):
        if not self.info: return None
        return json.loads(self.info)

    def get_collection_id(self):
        return self.sku_id

    def get_collection_type(self):
        return 'sku'

    def get_channel_url(self):
        return CHANNEL_DICT[self.get_channel()]['CHANNEL_PIC_URL']

    def get_channel_name(self):
        return CHANNEL_DICT[self.get_channel()]['CHANNEL_NAME']

    def get_channel(self):
        if 'taobao.com' in self.link:
            return CHANNEL_TAOBAO
        elif 'tmall.com' in self.link:
            return CHANNEL_TMALL

    def get_taobaoke_url(self):
        return self.link

    def to_ui_action(self):
        action = {}
        action['actionType'] = SKU_DETAIL
        action['price'] = self.get_component_price()
        action['originLink'] = self.link
        action['link'] = self.get_taobaoke_url()
        action['id'] = str(self.sku_id)
        action['normalPicUrl'] = self.get_normal_pic_url()
        action['description'] = self.description
        action['channelPicUrl'] = self.get_channel_url()
        return action

def get_spider_sku_by_id(sku_id):
    DBSession = rdbsession_generator()
    sku = DBSession.query(SpiderSku).filter(SpiderSku.sku_id == sku_id).first()
    DBSession.close()
    return sku

def get_spider_sku_by_source_source_id(source, source_id):
    DBSession = rdbsession_generator()
    spider_sku = DBSession.query(SpiderSku).filter(SpiderSku.source == source).filter(SpiderSku.source_id ==
            str(source_id)).first()
    DBSession.close()
    return spider_sku

def get_info_from_sku_source_source_id(source, source_id):
    sku = get_spider_sku_by_source_source_id(source, source_id)
    if not sku and source == 'taobao':
        sku = get_spider_sku_by_source_source_id('tmall', source_id)
    else: return None
    return sku.get_component_info()

