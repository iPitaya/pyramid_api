#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
from datetime import datetime
from hichao.publish.models.const import SUFFIX 
from hichao.star.models.star import get_star_by_star_id, update_star, add_star, get_all_stars
from hichao.publish.models.old_sku import get_sku_by_id
from hichao.publish.models.old_wodfan_sku import get_wodfan_sku_by_id
from hichao.publish.models.editor_star import get_editor_star_by_star_id 
from hichao.star.models.star_sku import add_star_sku, delete_star_sku_by_star_id
from hichao.util.object_builder import build_star_by_star_id, build_star_skus_by_star_id
from hichao.sku.models.sku import add_sku, update_sku
from hichao.sku.models.sku import _get_sku_by_id as get_publish_sku_by_id
from hichao.publish.models.old_user import editor_user_dict 
import transaction
import traceback
import json
user_dict = editor_user_dict()

def update_star_sku(star_id_list):
    for star_id in star_id_list:
        star = get_star_by_star_id(star_id, use_cache=False)
        delete_star_sku_by_star_id(star_id)
        i = get_editor_star_by_star_id(star_id)
        if not star:
            continue
        sku_count = 0
        for k, v in SUFFIX.iteritems():
            try:
                suffix = getattr(i, 'recommend_%s'%k)
                if suffix:
                    array_suffix = eval(suffix.replace('\n', ' '))
                    if len(array_suffix) > 0:
                        for _index, _suffix in enumerate(array_suffix):
                            for index, sku in enumerate(_suffix):
                                print sku['id']
                                _sku = get_sku_by_id(sku['id'])
                                _wodfan_sku = get_wodfan_sku_by_id(sku['id'])
                                b_color = ""
                                #try:
                                #    b_color = get_background("http://img.haobao.com/images/images" + sku["url"])
                                #    i_b_color = [int(bb) for bb in b_color]
                                #    b_color = str(i_b_color).replace(",", " ")
                                #except:
                                #    print "b_color thrift api is failed..."
                                if _sku:
                                    print i.id, k, sku['id'], index
                                    publish_sku = get_publish_sku_by_id(int(sku['id']))
                                    url = sku['url']
                                    width = height = 100
                                    if _wodfan_sku:
                                        url = _wodfan_sku.url
                                        width = _wodfan_sku.width
                                        height = _wodfan_sku.height
                                    if publish_sku != None:
                                        print "enter if publish_sku"
                                        publish_sku.url = url
                                        publish_sku.curr_price = sku['price']
                                        publish_sku.detail_url = sku.get('detail_url', sku['url'])
                                        publish_sku.price = sku['price']
                                        publish_sku.title = sku['title']
                                        publish_sku.sales = sku['sales']
                                        publish_sku.source = sku['source']
                                        publish_sku.link = sku['link']
                                        publish_sku.source_id = sku['source_id']
                                        publish_sku.is_recommend = _sku.is_recommend
                                        publish_sku.came_from = _sku.came_from
                                        publish_sku.description = _sku.description
                                        publish_sku.tags = _sku.tags
                                        publish_sku.height = height
                                        publish_sku.width = width
                                        publish_sku.brand_id = sku.get('brand_id',0)
                                        publish_sku.sku_type = sku.get('sku_type',0)
                                        publish_sku.intro = sku.get('intro','')
                                        publish_sku.origin_price = sku.get('origin_price',0.0)
                                        publish_sku.b_color = b_color
                                        update_sku(publish_sku)
                                    else:
                                        print "enter else if publish_sku"
                                        add_sku(sku['id'], url, sku['price'], sku['title'], sku['sales'], sku['source'], sku['link'], sku['source_id'], height, width, _sku.is_recommend, 1, _sku.description, _sku.came_from, _sku.tags, sku.get('detail_url', sku['url']),sku.get('brand_id',0),sku.get('sku_type',0),sku.get('intro',''), b_color, sku.get('origin_price', 0.0))
                                    print "exit else if publish_sku"
                                    add_star_sku(i.id, sku['id'], v*(_index+1), index, v)
                                    sku_count = sku_count + 1
            except Exception as ex:
                transaction.abort()
                traceback.print_exc()
                print Exception, ex
                print i.id, '没有%s'%k
        star.url = i.url
        star.review = i.review
        star.style = i.style
        star.description = i.description
        star.nstyle = i.nstyle
        star.scene = i.scene
        star.shape = i.shape
        star.star_name = i.star_name
        star.sku_count = sku_count
        update_star(star)

    return star_id_list

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
    #star_ids = get_all_stars()
    star_ids = [264]
    update_star_sku(star_ids)	
