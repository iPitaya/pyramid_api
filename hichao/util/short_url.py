# -*- coding:utf-8 -*-

import redis
from hashlib import md5
from rfc3987 import parse
from hichao.base.config import SHORTY_HOST
from hichao.base.config import SHORTY_REDIS_CONF as REDIS_CONFIG
from hichao.util.date_util import DAY as ONE_DAY_SECOND

URL_SALT = 'hichaobdg'
REDIS_SHORT_URL = 'SU-%s'

rds_client = redis.Redis(**REDIS_CONFIG)
chars = [ 
        "a" , "b" , "c" , "d" , "e" , "f" , "g" , "h" ,   
        "i" , "j" , "k" , "l" , "m" , "n" , "o" , "p" ,   
        "q" , "r" , "s" , "t" , "u" , "v" , "w" , "x" ,   
        "y" , "z" , "0" , "1" , "2" , "3" , "4" , "5" ,   
        "6" , "7" , "8" , "9" , "A" , "B" , "C" , "D" ,   
        "E" , "F" , "G" , "H" , "I" , "J" , "K" , "L" ,   
        "M" , "N" , "O" , "P" , "Q" , "R" , "S" , "T" ,   
        "U" , "V" , "W" , "X" , "Y" , "Z" 
        ]

def shorten(url, offset = 0):
    result = []
    s = md5(URL_SALT + url).hexdigest()

    for i in range(0, offset + 3):
        hexint = int(s[i * 8 : (i + 1) * 8], 16) & 0x3fffffff
        outChars = ""
        for j in range(0, 10):
            index = hexint & 0x0000003D
            outChars += chars[index]
            hexint = hexint >> 3
        result.append(outChars)
    return result[offset]

def url_by_short_url(short_url):
    r = rds_client.get(REDIS_SHORT_URL % short_url)
    return r

def short_url_new(long_url, index = 0):
    short_url = shorten(long_url, offset = index)
    _long_url = url_by_short_url(short_url)

    if _long_url and _long_url != long_url:
        index += 1
        short_url_new(long_url, index = index)
    else:
        r = rds_client.set(REDIS_SHORT_URL % short_url, long_url)
    return short_url

def generate_short_url(url):
    try:
        short_url = 'http://%s/%s' % (SHORTY_HOST, short_url_new(url))
    except:
        short_url = url
    return short_url

