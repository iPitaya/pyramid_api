# -*- coding:utf-8 -*-
#############################################################################
# REDIS SECTION

USE_LOCAL_CACHE = 1

ips = [29, 53, 54, 55, 18, 19, 5, 6]
ports = [30001, 30002, 30003, 30004, 30005, 30006, 30007, 30008]

REDIS_CACHE_CONFIG_LIST = []

for ip in ips:
    for port in ports:
        host = '192.168.1.{0}'.format(ip)
        conf = {'host':host, 'port':port}
        REDIS_CACHE_CONFIG_LIST.append(conf)

