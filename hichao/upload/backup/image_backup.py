#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time 
import datetime
import envoy
from hichao.upload.config import QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_NAME

#QINIU IMAGE INCREMENT BACKUP  by  Yuanye Ge

def today_keys():
    dt = datetime.datetime.today()
    dt = dt.strftime('%Y-%m-%d-')
    return dt 

def generate_qrsb_conf(keys):
    TEMPLATE = """
    {
        "access_key": "%(access_key)",
        "secret_key": "%(secret_key)",
        "bucket": "%(bucket_name)",
        "start_time": 0,
        "max_size": 0,
        "encode_fname": 0,
        "rs_host": "http://rs.qbox.me",
        "rsf_host": "http://rsf.qbox.me",
        "prefix": "%(prefix_keys)"
    }
        """
    conf = TEMPLATE%{'access_key':QINIU_ACCESS_KEY, 'secret_key':QINIU_SECRET_KEY,\
                         'bucket_name':QINIU_BUCKET_NAME, 'prefix_keys':keys}

    with open(join(dirname(__file__), 'qrsb.conf'), 'w') as f:
        tmp = f.write(conf)

def backup_image(keys):
    CMD_MV('/home/release/qrsb /home/release/image')
    r = envoy.run(CMD_MV)
    print r.std_out
    print r.std_err        
    with open(join(dirname(__file__), 'error.log'), 'w') as f:
        tmp = f.write(r.std_err)
        tmp = f.write(c.std_err)


if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
    # 确保 顺序执行? 线程
    keys =  today_keys()
    generate_qrsb_conf(keys)
    backup_image(keys)

