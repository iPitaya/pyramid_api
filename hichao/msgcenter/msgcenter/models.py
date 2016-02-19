import MySQLdb
import murmur
import time
from db import *

def get_notices(to_uid,category,flag_n,page_size):
    id=murmur.string_hash(to_uid) % 100

    print id

    conn=MySQLdb.connect(host=MYSQL_HOST,user=MYSQL_USER,passwd=MYSQL_PASSWD,db="msgcenter",port=MYSQL_PORT,charset="utf8")
    cursor = conn.cursor()
    
    notices=None

    if flag_n==0:
        sql="select UNIX_TIMESTAMP(ts),content from notice%d where to_uid=%s and tab='%s' order by id desc limit %d" % (id,to_uid,category,page_size)
        print sql,id
        cursor.execute(sql)
        ret=cursor.fetchall()
    else:
        sql="select UNIX_TIMESTAMP(ts),content from notice%d where to_uid=%s and tab='%s' order by id desc limit %d offset %d" % (id,to_uid,category,page_size,flag_n*page_size)
        print sql
        cursor.execute(sql)
        ret=cursor.fetchall()

    if len(ret)==0:
        ret=[]
    else:
        ret=[r for r in ret]

    last_ts=0
    if len(ret)>0:
        last_ts=ret[-1][0]

    time_now=time.time()
    if flag_n>0:
        time_now=ret[0][0]

    if category=='msg':
        if flag_n>0:
            sql="select UNIX_TIMESTAMP(ts),content from notice_all where ts>FROM_UNIXTIME(%s) and ts<FROM_UNIXTIME(%s) order by id desc" % (last_ts,time_now)
        else:
            sql="select UNIX_TIMESTAMP(ts),content from notice_all where ts>FROM_UNIXTIME(%s) order by id desc" % (last_ts)
        print sql
        cursor.execute(sql)
        ret1=cursor.fetchall()   
        print len(ret1)
        ret.extend(ret1)
        print len(ret)
        ret.sort(lambda x1,x2:cmp(x2[0],x1[0]))
        print len(ret)
    ret=[x[1] for x in ret]
    print len(ret)

    cursor.execute("commit")
    return ret,time_now

def get_star_comment_count(id):
    conn=MySQLdb.connect(host=MYSQL_HOST,user=MYSQL_USER,passwd=MYSQL_PASSWD,db="comment",port=MYSQL_PORT,charset="utf8")
    cursor = conn.cursor()

    sql="select count(*) from comment.star_comment where id=%d" % (int(id))
    cursor.execute(sql)
    ret=cursor.fetchall()[0][0]
    cursor.execute("commit")
    return ret

def get_thread_comment_count(id):
    conn=MySQLdb.connect(host=MYSQL_HOST,user=MYSQL_USER,passwd=MYSQL_PASSWD,db="comment",port=MYSQL_PORT,charset="utf8")
    cursor = conn.cursor()

    sql="select count(*) from comment.thread_comment where thread_id=%d" % (int(id))
    ret=cursor.execute(sql)
    ret=cursor.fetchall()[0][0]
    cursor.execute("commit")
    return ret
