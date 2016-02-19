#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import json
import traceback

ok = 0
while ok == 0:
    try:
        print '$' * 80, datetime.now()
        import hichao.base.config as cfg
        cfg.USE_LOCAL_CACHE = 0
        from hichao.publish.models.const import SUFFIX 
        from hichao.publish.models.editor_star import EditorStar, editor_publish_star_list, editor_publish_star_count, get_editor_star_by_star_id
        from hichao.publish.models.old_user import get_user_id_by_name, editor_user_dict 
        from hichao.publish.models.old_sku import get_sku_by_id
        from hichao.publish.models.old_wodfan_sku import get_wodfan_sku_by_id
        from hichao.sku.models.sku import add_sku, update_sku
        from hichao.star.models.star import add_star, get_last_publish_date
        from hichao.collect.models.collect import REDIS_STAR_PUBLISH_DAYS, REDIS_STAR_PUBLISH_HOURS
        from hichao.base.lib.timetool import day2days
        from hichao.star.models.star import get_star_by_star_id
        from hichao.util.object_builder import build_star_by_star_id
        from hichao.star.models.star_sku import add_star_sku, delete_star_sku_by_star_id
        from hichao.sku.models.sku import _get_sku_by_id as get_publish_sku_by_id
        ok = 1
    except Exception, ex:
        print Exception, ex
        print 'import error, try again in 5 seconds.'
        time.sleep(5)

def last_online_star_publish_date(review=1):
    return get_last_publish_date(review=review) 
    #return 1360397410

def online_star_list(ispublish=1, review=1):
    LIMIT=100
    offset = 0
    last_pulish_date = last_online_star_publish_date(review=review)
    print 'review=%s last_pulish_date=%s'%(review, last_pulish_date)
    count = editor_publish_star_count(last_pulish_date, ispublish=ispublish, review=review)
    print 'review=%s count=%s'%(review, count), '*/'*20

    while True:
        yield editor_publish_star_list(last_pulish_date, ispublish=ispublish, review=review, limit=LIMIT, offset=offset)
        if  offset >= count:
            break
        offset = offset + LIMIT

def publish_star(user_dict, star_list):
    #if star_list:
    #    star_id_list = map(lambda x: x.id, star_list) 
    #    date_list = map(lambda x:day2days(x.publish_date),  star_list) 

    #    star_days_dict = dict(zip(star_id_list, date_list))
    #    redis.hmset(REDIS_STAR_PUBLISH_DAYS,star_days_dict)

    for i in star_list:
        print 'star', i.id, i.review, '*'*10
        username = i.username.strip()
        if not username:
            username = "anony"
        if username:
            user_id = user_dict.get(username, 2)
            delete_star_sku_by_star_id(i.id)
            sku_count = 0
            for k, v in SUFFIX.iteritems():
                try:
                    suffix = getattr(i, 'recommend_%s'%k)
                    if suffix:
                        array_suffix = eval(suffix.replace('\n', ' '))
                        if array_suffix:
                            for _index, _suffix in enumerate(array_suffix):
                                for index, sku in enumerate(_suffix):
                                    try:
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
                                            height = width = 100
                                            url = sku['url']
                                            if _wodfan_sku:
                                                height = _wodfan_sku.height
                                                width = _wodfan_sku.width
                                                url = _wodfan_sku.url
                                            if publish_sku != None:
                                                print "enter if publish_sku"
                                                publish_sku.url = url
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
                                                add_sku(sku['id'], url, sku['price'], sku['title'], sku['sales'], sku['source'], sku['link'], sku['source_id'], height, width, _sku.is_recommend, 1, _sku.description, _sku.came_from, _sku.tags, sku.get('detail_url', sku['url']),sku.get('brand_id',0),sku.get('sku_type',0), sku.get('intro',''), b_color, sku.get('origin_price', 0.0))
                                            add_star_sku(i.id, sku['id'], v*(_index+1), index, v)
                                            sku_count = sku_count + 1
                                    except Exception, ex:
                                        print Exception, ex
                                        print i.id, sku['id']
                except Exception as ex:
                    traceback.print_exc()
                    print Exception, ex
                    print i.id, '没有%s'%k
            add_star(i.id, i.url, user_id, i.width, i.height, i.publish_date, i.score, i.description, i.video_url, i.title, i.style, i.star_name, i.review, i.nstyle, i.scene, i.shape, sku_count, i.is_selfie)
            ok = 0
            while ok == 0:
                try:
                    from hichao.base.lib.redis import redis, redis_key
                    redis.hset(REDIS_STAR_PUBLISH_DAYS, i.id, day2days(i.publish_date))
                    redis.hset(REDIS_STAR_PUBLISH_HOURS, i.id, i.publish_date)
                    ok = 1
                    print 'set REDIS_STAR_PUBLISH_DAYS/HOURS done.'
                except Exception, ex:
                    print 'redis operate error.'
                    print Exception, ex
                    print 'try again.'

def publish_online_star():
    user_dict = editor_user_dict()
    star_list = online_star_list(ispublish=1, review=1)
    topic_star_list = online_star_list(ispublish=0, review=2)
    #x = get_editor_star_by_star_id(69254)
    #publish_star(user_dict, [x,])

    while True:
        print 'star transport starting', '----'*20
        try:
            star_item = star_list.next()
            if star_item:
                publish_star(user_dict, star_item)
        except StopIteration, ex:
            traceback.print_exc()
            print StopIteration, ex
            break 

    while True:
        print 'topic_star transport starting', '----'*20
        try:
            topic_star_item = topic_star_list.next()
            if topic_star_item:
                publish_star(user_dict, topic_star_item)
        except StopIteration, ex:
            traceback.print_exc()
            print StopIteration, ex
            break 


def main():
    start = time.time()
    print 'start time',datetime.now(), '*/-'*20
    try:
        publish_online_star()
    except Exception, ex:
        print Exception, ex
    print 'end time', datetime.now(), '*/-'*20
    print time.time() - start
    print 'done ****'

if __name__ == "__main__":
    main()

