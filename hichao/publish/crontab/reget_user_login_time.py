# -*- coding:utf-8 -*-

from hichao.user.models.device import user_identify_last_login_by_offset
from hichao.base.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWD
import torndb

def main(days):
    conn = torndb.Connection("{0}:{1}".format(MYSQL_HOST, MYSQL_PORT), 'device', MYSQL_USER, MYSQL_PASSWD)
    _offset = 0
    _limit = 100
    user_list = user_identify_last_login_by_offset('mxyc_lite_ip', 'iphone', '1.0', offset = _offset, limit = _limit)
    while user_list:
        sql = 'update device set timelog = case open_uuid'
        dts = []
        for u in user_list:
            sql = sql + " when '" + u[0] + "' then from_unixtime(" + str(u[1]) + ")"
            dts.append("'{0}'".format(u[0]))
        sql = sql + ' end where open_uuid in (' + ','.join(dts) + ');'
        #print sql
        conn.execute(sql)
        _offset = _offset + _limit
        print _offset
        user_list = user_identify_last_login_by_offset('mxyc_lite_ip', 'iphone', '1.0', offset = _offset, limit = _limit)
        #user_list = False


if __name__ == '__main__':
    main(1)

