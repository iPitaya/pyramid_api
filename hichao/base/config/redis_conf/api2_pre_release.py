# -*- coding:utf-8 -*-
#############################################################################
# REDIS SECTION

USE_LOCAL_CACHE = 0

ips = [222]
ports = [9999]
db = 1

REDIS_CACHE_CONFIG_LIST = []

for ip in ips:
    for port in ports:
        host = '192.168.1.{0}'.format(ip)
        conf = {'host':host, 'port':port, 'db':db}
        REDIS_CACHE_CONFIG_LIST.append(conf)

