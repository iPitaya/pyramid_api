#coding:utf-8

"""Make list during (now-first time),store this list in the database."""

import time
import torndb
from hichao.base.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWD


def main(start, end):
    """Make list during end-start,store this list in the database.

    Keyword arguments:
    start -- the Unix timestamp
    end -- the Unix timestamp

    If count of stars' picture is zero,function will return False,and do nothing with database.

    """
    DROPTIME_START = start
    DROPTIME_END = end
    # connection databases
    MYSQL_HOST_STR = "{0}:{1}".format(MYSQL_HOST, MYSQL_PORT)
    db_star = torndb.Connection(MYSQL_HOST_STR, "star", MYSQL_USER, MYSQL_PASSWD)
    db_drop = torndb.Connection(MYSQL_HOST_STR, "droplist", MYSQL_USER, MYSQL_PASSWD)
    db_list = torndb.Connection(MYSQL_HOST_STR, "showlist", MYSQL_USER, MYSQL_PASSWD)
    # get STAR
    starListQuery = db_star.query("SELECT id, publish_date FROM star WHERE (publish_date>%s AND publish_date<=%s) AND review=1 ORDER BY publish_date",DROPTIME_START, DROPTIME_END)
    if len(starListQuery)==0:
        return False
    else:
        showList = [(i["id"], "star", None, i["publish_date"]) for i in starListQuery]
        # get DROP
        dropListQuery = db_drop.query("SELECT type_id, type, publish_date FROM droplist WHERE publish_date>%s AND publish_date<=%s ORDER BY publish_date",DROPTIME_START, DROPTIME_END)
        dropStarList = [(i["type_id"], "drop", None, int(i["publish_date"])) for i in dropListQuery if i["type"] == u"star"]
        dropTopicList = [(i["type_id"], "drop", None, int(i["publish_date"])) for i in dropListQuery if i["type"] == u"topic"]
        dropStarNum = len([i for i in dropListQuery if i["type"] == u'star'])
        dropTopicNum = len([i for i in dropListQuery if i["type"] == u'topic'])
        print "========LOADED COMPLETED========="
        # create list as the rules
        if dropStarNum == 0 and dropTopicNum == 0:
            showList.append((None, "time", None , DROPTIME_END))
        elif dropStarNum == 0 and dropTopicNum != 0:
            showList.append((None, "time", None , DROPTIME_END))
            if dropTopicNum == 1:
                showList.insert(-2, dropTopicList[0])
            elif dropTopicNum > 1:
                showList.insert(-2, dropTopicList.pop())
                for dropTopicItem in dropTopicList:
                    index = int(time.time()*1000000) % (len(showList) - 3)
                    showList.insert(index, dropTopicItem)
        elif dropStarNum != 0 and dropTopicNum == 0:
            if dropStarNum == 1:
                showList.append((dropStarList[0][0], "timedrop", None, dropStarList[0][3]))
            elif dropStarNum > 1:
                timedrop = dropStarList.pop()
                showList.append(timedrop[0], "timedrop", None, timedrop[3])
                for dropStarItem in dropStarList:
                    index = int(time.time()*1000000) % (len(showList) - 1)
                    showList.insert(index, dropStarItem)
        elif dropStarNum != 0 and dropTopicNum != 0:
            if dropStarNum == 1:
                showList.append((dropStarList[0][0], "timedrop", None, dropStarList[0][3]))
            elif dropStarNum > 1:
                timedrop = dropStarList.pop()
                showList.append(timedrop[0], "timedrop", None, timedrop[3])
                for dropStarItem in dropStarList:
                    index = int(time.time()*1000000) % (len(showList) - 1)
                    showList.insert(index, dropStarItem)
            if dropTopicNum == 1:
                showList.insert(-2, dropTopicList[0])
            elif dropTopicNum > 1:
                showList.insert(-2, dropTopicList.pop())
                for dropTopicItem in dropTopicList:
                    index = int(time.time()*1000000) % (len(showList) - 3)
                    showList.insert(index, dropTopicItem)
        # store list in database
        for item in showList:
            db_list.execute("INSERT INTO test2 VALUES (null, %s, %s, %s, %s)", *item)
            id = db_list.get("SELECT MAX(id) FROM test2")["MAX(id)"]
            # create power num
            db_list.execute("UPDATE test2 SET power = %s WHERE id=%s", id, id)
        return True

if __name__ == '__main__':
    # old data time
    timeStart = 1340798400
    # 2013-5-13 20:00:00
    # timeStart = 1368446400
    while  timeStart < time.time():
        timeChunk = [36000, 7200, 7200, 7200, 7200, 7200, 7200, 7200]
        for i in timeChunk:
            timeEnd = timeStart+i
            result = main(timeStart, timeEnd)
            timeStart = timeEnd
    print "ALL DONE"
