# -*- coding:utf-8 -*-

from icehole_client.promotion_client import PromotionClient
from hichao.tuangou.models.tuangouinfo import build_tuangou_by_tuangou_id
from hichao.sku.models.sku import get_sku_by_id
from hichao.base.config import COUPON_URL, BONUS_URL
from hichao.util.cps_util import get_title_style_by_link
import copy

JUMP_TYPE = ['tuanlist','worthylist','topiclist','starusers','jiaocheng','shoplist']
ITEM_TYPE = ['thread','star','sku','topic','user','groupsku', 'theme', 'region']
WEBVIEW_TYPE = ['coupon', 'bonus', 'webview']

def build_action(action_type, action_value):
    action = {}
    if action_type in JUMP_TYPE:
        act_type = 'item'
        if action_type == 'topiclist':
            act_type = 'thread'
        action={}
        action['type'] = act_type
        action['actionType'] = 'jump'
        action['child'] = action_type
    elif action_type in ITEM_TYPE:
        if action_type == 'sku':
            sku = get_sku_by_id(action_value)
            if sku:
                sku['support_ec'] = 1
                action = sku.to_lite_ui_action()
        else:
            act_type = 'detail'
            if action_type == 'groupsku':
                act_type = 'group'
                action_type = 'sku'
            action['actionType'] = act_type
            action['type'] = action_type
            action['id'] = action_value
    elif action_type == 'tuan':
        action={}
        if action_value:
            tuan_com = build_tuangou_by_tuangou_id(int(action_value),slide=True)
            if tuan_com:
                action = tuan_com['component']['action']
    elif action_type in WEBVIEW_TYPE:
        action = {}
        title_style = copy.deepcopy(get_title_style_by_link(''))
        web_url = ''
        if action_type == 'coupon':
            title_style['text'] = '领取优惠券'
            web_url = COUPON_URL.format(action_value)
        elif action_type == 'bonus':
            title_style['text'] = '领取红包'
            web_url = BONUS_URL.format(action_value)
        elif action_type == 'webview':
            title_style['text'] = '链接详情'
            web_url = action_value
        action['actionType'] = 'webview'
        action['webUrl'] = web_url
        action['means'] = 'push'
        action['titleStyle'] = title_style
    else:
        action={}
        action['actionType'] = action_type
        action['id'] = action_value
    return action

def build_cms_action(action_type_id, action_value):
    client = PromotionClient()
    action_type = client.get_action_type_by_id(int(action_type_id))
    if action_type:
        action_type = action_type.type_value
    return build_action(action_type, action_value)

