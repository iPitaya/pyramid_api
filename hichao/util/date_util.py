# -*- coding:utf-8 -*-

import time

ZHOU_DICT = {
        0:'周一',
        1:'周二',
        2:'周三',
        3:'周四',
        4:'周五',
        5:'周六',
        6:'周日',
        }

WEEK_DICT = {
        0:'星期一',
        1:'星期二',
        2:'星期三',
        3:'星期四',
        4:'星期五',
        5:'星期六',
        6:'星期日',
        }

SECOND = 1
FIVE_SECONDS = 5
TEN_SECONDS = 10
HALF_MINUTE = 30
MINUTE = 60
FIVE_MINUTES = 300
TEN_MINUTES = 600
QUARTER = 900
HALF_HOUR = 1800
HOUR = 3600
TWO_HOUR = 7200
FOUR_HOUR = 14400
HALF_DAY = 43200
DAY = 86400
WEEK = 604800
HALF_MONTH = 1209600
MONTH = 2592000
HALF_YEAR = 15768000
YEAR = 31536000
FOREVER = 0

SEASON_ONE = [1, 2, 3]
SEASON_TWO = [4, 5, 6]
SEASON_THREE = [7, 8, 9]
SEASON_FOUR = [10, 11, 12]

SEASONS = [SEASON_ONE, SEASON_TWO, SEASON_THREE, SEASON_FOUR]

def format_star_publish_date(timestamp):
    tm = time.localtime(float(timestamp))
    now = time.localtime()
    if tm.tm_year == now.tm_year:
        tm_str = '{0}月{1}日{2}点'.format(tm.tm_mon, tm.tm_mday, tm.tm_hour)
    else:
        tm_str = '{0}年{1}月{2}日{3}点'.format(tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour)
    return tm_str

def get_date_attr(timestamp, attr):
    tm = time.localtime(float(timestamp))
    return getattr(tm, attr)

def format_digital(digital):
    if digital > 9:
        return str(digital)
    else:
        return '0{0}'.format(digital)

def get_rough_time(ts):
    ts = float(ts)
    now = time.time()
    interval = now - ts
    if interval > YEAR:
        years = int(interval / YEAR)
        return u'{0}年前'.format(years)
    if interval > MONTH:
        months = int(interval / MONTH)
        return u'{0}个月前'.format(months)
    if interval > WEEK:
        weeks = int(interval / WEEK)
        if weeks == 4:
            return u'1个月前'
        return u'{0}周前'.format(weeks)
    if interval > DAY:
        days = int(interval / DAY)
        return u'{0}天前'.format(days)
    if interval > HOUR:
        hours = int(interval / HOUR)
        return u'{0}小时前'.format(hours)
    if interval > FIVE_MINUTES:
        minutes = int(interval / MINUTE)
        return u'{0}分钟前'.format(minutes)
    return u'刚刚'

