# -*- coding:utf-8 -*-

from hichao.base.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWD
import torndb

def main():
    conn_166 = torndb.Connection("{0}:{1}".format(MYSQL_HOST, MYSQL_PORT), "device", MYSQL_USER, MYSQL_PASSWD)
    conn_168 = torndb.Connection("{0}:{1}".format(MYSQL_HOST, MYSQL_PORT), "wodfan", MYSQL_USER, MYSQL_PASSWD)
    _offset = 0
    _limit = 1000
    sql = "select devicetoken from device where appname='mxyc_ip' and version = '2.3';"
    user_device_tokens = conn_166.query(sql)
    flag = True
    while flag:
        new_user_list = user_device_tokens[_offset: _offset + _limit]
        if len(new_user_list) < 1000:
            flag = False
        tks = ["'{0}'".format(user['devicetoken']) for user in new_user_list]
        users = ','.join(tks)
        update_sql = 'update user_udid set push_avaliable = 0 where devicetoken in (' + users + ');'
        conn_168.execute(update_sql)
        _offset = _offset + _limit
        print _offset, 'done.'

if __name__ == '__main__':
    main()

