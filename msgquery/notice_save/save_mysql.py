#coding:utf-8
import eventlet
import MySQLdb
import murmur
import logging
import time
import datetime
import ujson
import sys
import zmqgreen as zmq
import traceback
#from eventlet.green import zmq
from eventlet import db_pool
from CDN import get_img_url, get_topic_url, get_drop_url
from hichao.util.content_util import rebuild_content

sys.path.append("..")
sys.path.append("../..")
#from hichao.base.lib.redis import redis, redis_key
from notice_num import  NOTICE_COUNT, NOTICE_COUNT_CN, notice_new, msg_all_new
import tomdb

cp_220 = db_pool.ConnectionPool(MySQLdb, max_size=200, host='192.168.1.166', user='release',
                                passwd='release', use_unicode=True, charset="utf8mb4")
# cp_170 = db_pool.ConnectionPool(MySQLdb, max_size=500, host='192.168.1.166', user='xuchuan',
#                                                         passwd='xuchuan', use_unicode=True, charset="utf8")
# cp_167 = db_pool.ConnectionPool(MySQLdb, max_size=500, host='192.168.1.166', user='release',
#                                                         passwd='release', use_unicode=True, charset="utf8")
cp_170 = cp_220
cp_167 = cp_220

context = zmq.Context()
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://localhost:3000")
pool = eventlet.GreenPool(2000)

logger = logging.getLogger()
handler = logging.FileHandler("notice.log")
formatter = logging.Formatter("%(levelname)s %(asctime)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)

#def _execute(host, sql_dict):
#    num = 0
#    while num < 5:
#        try:
#            db = host.get()
#        except Exception, e:
#            num += 1
#            print e
#        else:
#            num1 = 0
#            while num1 < 3:
#                try:
#                    db.autocommit(True)
#                    cursor = db.cursor()
#                    print sql_dict
#                    if sql_dict['value']:
#                        cursor.execute(sql_dict['sql'], sql_dict['value'])
#                        print 'value'
#                    else:
#                        cursor.execute(sql_dict['sql'])
#                        print 'no value'
#                except Exception, ex:
#                    print ex
#                    num1 += 1
#                else:
#                    host.put(db)
#                    return cursor
#            break

#def _query(host, sql_dict):
#    try:
#        cursor = _execute(host, sql_dict)
#    except Exception, e:
#        print e
#    else:
#        result = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor]
#        del cursor
#        return result
def get_db():
    DB = tomdb.Connection('192.168.1.18', 'wodfan', 'api2', 'CXxY1KMSm5ewYBnfIqxnOtrMy', use_charset="utf8mb4")
    return DB

def _execute(host, sql_dict):
    DB = get_db()
    try:
        DB.execute(sql_dict['sql'], *sql_dict['value'])
    except Exception, e:
        raise e
    else:
        pass
    finally:
        DB.close()

def _query(host, sql_dict):
    DB = get_db()
    try:
        result = DB.query(sql_dict['sql'], sql_dict['value'])
    except Exception, e:
        raise e
    else:
        return result
    finally:
        DB.close()

def _get_component():
    component = {'component':{'componentType':'thumbnailDecoratedMessageCell','actions':[\
                      {'actionType':'space', 'userId':'', 'userAvatar':'', 'userName':''},{}],\
                        'picUrl':'','userAvatar':'','userName':'','description':'','dateTime':''}}
    return component

def _get_db_num(uid):
    return murmur.string_hash(str(uid)) % 100

def _get_user_info(uid):
    user_query = _query(cp_170, {'sql':'SELECT username, avatar FROM wodfan.user WHERE user_id=%s',\
                                                              'value':uid})
    user_name = user_query[0]['username']
    query_avatar = user_query[0]['avatar']
    if query_avatar:
        user_avatar = get_img_url(query_avatar)
    else:
        user_avatar = ''
    return user_name, user_avatar

def _initialize_component(from_uid):
    component = _get_component()
    save_time = time.time()
    from_user_name, from_user_avatar = _get_user_info(from_uid)
    component['component']['userName'] = from_user_name
    component['component']['userAvatar'] = from_user_avatar
    component['component']['dateTime'] = time.strftime("%Y.%m.%d %H:%M",time.localtime(save_time))
    component['component']['actions'][0]['userId'] = str(from_uid)
    component['component']['actions'][0]['userName'] = from_user_name
    component['component']['actions'][0]['userAvatar'] = from_user_avatar
    return component, save_time

def _get_comment(comment_id, comment_type):
    comment_query = _query(cp_220, {'sql':'SELECT {0}_id, content, comment_id FROM comment.{0}_comment \
                                                             WHERE id=%s'.format(comment_type.split('_')[0]), 'value':comment_id})
    main_id = int(comment_query[0]['{0}_id'.format(comment_type.split('_')[0])])
    comment_text = '”' + comment_query[0]['content'][:150] + '”'
    if comment_type == "thread_comment":
    #if not comment_query[0]['comment_id']:
        return main_id, comment_text, None
    else:
         up_comment_id = int(comment_query[0]['comment_id'])
         up_comment_query = _query(cp_220, {'sql':'SELECT content FROM comment.{0}_comment WHERE id=%s'\
                                                                        .format(comment_type.split('_')[0]), 'value':up_comment_id})
         up_comment_text = '“' + up_comment_query[0]['content'][:20] + '”'
         return main_id, comment_text, up_comment_text

def _get_upload_img(img_id):
    img_query = _query(cp_220, {'sql':'SELECT url, height, width FROM upload.image WHERE id=%s',\
                                                                    'value':img_id})
    return img_query

def _thread_action(thread_id):
    thread_query = _query(cp_220, {'sql':'SELECT user_id, img_id, content, ts FROM forum.threads WHERE id=%s',\
                                                         'value':thread_id})
    thread_user_id = thread_query[0]['user_id']
    thread_img_id = thread_query[0]['img_id']
    thread_user_name, thread_user_avatar =_get_user_info(thread_user_id)
    thread_img_query = _get_upload_img(thread_img_id)
    thread_img_url = thread_img_query[0]['url']
    thread_action = dict(id=str(thread_id),
                                    actionType = 'subjectDetail',
                                    userName=thread_user_name,
                                    userId=str(thread_user_id),
                                    userPicUrl=thread_user_avatar,
                                    normalPicUrl=thread_img_query[0]['url'],
                                    width=str(thread_img_query[0]['width']),
                                    height=str(thread_img_query[0]['height']),
                                    dateTime=datetime.datetime.strftime(thread_query[0]['ts'], "%Y.%m.%d %H:%M"),
                                    #description=[{'component':{'componentType':'msgText',
                                    #    'text':thread_query[0]['content']}}],
                                    description = rebuild_content(thread_query[0]['content'])
    )
    return thread_action, thread_img_url

def _get_itemPicUrlList(star_sku_query):
    tab_index = {i['tab_index'] for i in star_sku_query}
    tab_index_list = list(tab_index)
    tab_index_list.sort()
    itemPicUrlList = []
    for tab_index_id in tab_index_list:
        tab_position_list = [i['tab_position'] for i in star_sku_query if i['tab_index']==tab_index_id]
        tab_position_id = min(tab_position_list)
        sku_id = [i['sku_id'] for i in star_sku_query if i['tab_index']==tab_index_id and i['tab_position']==tab_position_id][0]
        sku_query = _query(cp_220, {'sql':'SELECT url FROM sku.sku WHERE sku_id=%s', 'value':sku_id})
        sku_url = get_img_url(sku_query[0]['url'])
        itemPicUrlList.append({'picUrl':sku_url})
    return itemPicUrlList

def _star_action(star_id):
    star_query = _query(cp_170, {'sql':'SELECT url, description, user_id, height, width, video_url, publish_date \
                                                    FROM star.star WHERE star_id=%s', 'value':star_id})
    star_user_id = star_query[0]['user_id']
    star_ts = time.localtime(float(star_query[0]['publish_date']))
    star_user_name, star_user_avatar =_get_user_info(star_user_id)
    star_img_url = get_img_url(star_query[0]['url'])
    star_sku_query = _query(cp_220, {'sql':'SELECT sku_id, tab_index, tab_position FROM star.star_sku WHERE\
                                                                    star_id=%s', 'value':star_id})
    itemPicUrlList = _get_itemPicUrlList(star_sku_query)
    star_action = dict(actionType = 'starDetail',
                                id=str(star_id),
                                userName=star_user_name,
                                userId=str(star_user_id),
                                userPicUrl=star_user_avatar,
                                normalPicUrl=star_img_url,
                                width=str(star_query[0]['width']),
                                height=str(star_query[0]['height']),
                                dateTime='{0}月{1}日{2}点'.format(star_ts.tm_mon, star_ts.tm_mday, star_ts.tm_hour),
                                description=star_query[0]['description'],
                                itemPicUrlList=itemPicUrlList
    )
    if star_query[0]['video_url']:
        star_action['videoUrl'] = star_query[0]['video_url']
    return star_action, star_img_url

def _topic_action(topic_id):
    topic_query = _query(cp_170, {'sql':'SELECT title, url, drop_image FROM wodfan.navigator WHERE navigator_id=%s',
                                                      'value':topic_id})
    topic_title = topic_query[0]['title']
    drop_image = topic_query[0]['drop_image']
    topic_url = topic_query[0]['url']
    if drop_image.startswith('http'):
        topic_img_url = get_drop_url(drop_image)
    else:
        topic_img_url = get_topic_url(topic_url)
    topic_action = dict(actionType='topicDetail',
                                  id=str(topic_id),
                                  title=topic_title,
    )
    return topic_action, topic_img_url


def _get_description(content_id, notice_type):
    if notice_type.split("_")[-1] == 'comment':
        main_id, comment_text, up_comment_text = _get_comment(content_id, notice_type)
        if up_comment_text:
            description = [{'component':{'componentType':'msgText','text':'对您的评论 '}},
                                  {'component':{'componentType':'msgText','text':up_comment_text}},
                                  {'component':{'componentType':'msgText','text':' 进行了回复：'}},
                                  {'component':{'componentType':'msgText','text':comment_text}}]
        else:
            description = [{'component':{'componentType':'msgText','text':'评论了您的图片：'}},
                                   {'component':{'componentType':'msgText','text':comment_text}}]
    elif notice_type.split("_")[-1] == 'like':
        main_id = content_id
        description = [{'component':{'componentType':'msgText','text':'喜欢了您的图片。'}}]
    elif notice_type == 'thread_2star_msg':
        main_id = content_id
        description = [{'component':{'componentType':'msgText','text':'恭喜您,您的帖子已发布为明星图。'}}]
    return description, main_id

def build_component(api_recv):
    from_uid = int(api_recv['from_uid'])
    content_id = int(api_recv['content_id'])
    notice_type = api_recv['type']
    component, save_time = _initialize_component(from_uid)
    description, main_id = _get_description(content_id, notice_type)
    component['component']['description'] = description
    action, pic_url= eval("_{0}_action(main_id)".format(notice_type.split("_")[0]))
    component['component']['actions'][1] = action
    component['component']['picUrl'] = pic_url
    component['content_id'] = content_id
    return component, save_time

def insert_notice(data, to_uid, ts, notice_type):
    db_num = _get_db_num(to_uid)
    tab = notice_type.split("_")[-1]
    sql_dict = {'sql':'INSERT INTO msgcenter.notice{0} (to_uid, tab, type, content, ts) VALUES \
                       (%s,%s,%s,%s,FROM_UNIXTIME(%s))'.format(db_num), 'value':(to_uid, tab, notice_type, data, ts)}
    _execute(cp_167, sql_dict)
    notice_new(to_uid,tab)

def _get_to_uid(api_recv):
    content_id = int(api_recv['content_id'])
    notice_type = api_recv['type']
    if notice_type == 'thread_comment':
        comment_query = _query(cp_220, {'sql':'SELECT thread_id FROM comment.{0}_comment \
                                                                WHERE id=%s'.format(notice_type.split('_')[0]), 'value':content_id})
        thread_query = _query(cp_220, {'sql':'SELECT user_id FROM forum.threads WHERE id=%s', 'value': comment_query[0]['thread_id']})
        to_uid = thread_query[0]['user_id']
    elif notice_type.split("_")[-1] == 'comment':
        comment_query = _query(cp_220, {'sql':'SELECT to_uid FROM comment.{0}_comment \
                                                                WHERE id=%s'.format(notice_type.split('_')[0]), 'value':content_id})
        to_uid = comment_query[0]['to_uid']
    else:
        thread_query = _query(cp_220, {'sql':'SELECT user_id FROM forum.threads WHERE id=%s',\
                                                             'value':content_id})
        to_uid = thread_query[0]['user_id']
    return to_uid

def _mid_like(api_recv):
    if api_recv['type'] == 'thread_like':
        like_info = '{0}_{1}'.format(api_recv['from_uid'], api_recv['content_id'])
        like_query = _query(cp_220, {'sql':'SELECT id FROM msgcenter.like_log WHERE like_info=%s', 'value':'like_info'})
        if not like_query:
            sql_dict = {'sql':'INSERT INTO msgcenter.like_log (like_info) VALUES (%s)', 'value':(like_info)}
            return True
    else:
        return True

def save_notice(api_recv):
    if _mid_like(api_recv):
        notice_type = api_recv['type']
        to_uid = _get_to_uid(api_recv)
        if int(to_uid) != int(api_recv['from_uid']):
            component, save_time = build_component(api_recv)
            data = ujson.dumps(component)
            insert_notice(data, to_uid, save_time, notice_type)

def run(recv):
    try:
        api_recv = ujson.loads(recv)
        if api_recv.get('token') == '4B21D298EF307D04':
            save_notice(api_recv)
            if api_recv['type'] == 'thread_2_comment':
                api_recv['type'] = 'thread_comment'
                save_notice(api_recv)
    except Exception, ex:
        logger.error(str(ex)+traceback.format_exc())

if __name__ == '__main__':
    print "ready"
    while True:
        recv = receiver.recv()
        pool.spawn_n(run, recv)
