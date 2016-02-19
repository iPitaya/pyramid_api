# -*- coding:utf-8 -*-

from hichao.sku.models.sku import Sku

def rebuild_sku(sku, more_items = '', lite_action = 0, support_webp = 0, support_ec = 1):
    if not sku: return sku
    sku['f'] = 1
    if more_items: sku['more_items'] = 1
    sku['lite_action'] = lite_action
    sku['support_webp'] = support_webp
    sku['support_ec'] = support_ec
    _sku = Sku()
    _sku.update(sku)
    return _sku

