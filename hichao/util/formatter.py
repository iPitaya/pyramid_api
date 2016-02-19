# -*- coding:utf-8 -*-

from hichao.util.date_util import format_digital
def format_price(price):
    price = str(price)
    if '-' in str(price):
        price = price.split('-')[0]
    if '.' in str(price):
        #不直接格式float 防止字符串不是数字报错
        price = price[0:price.find('.')+3]
        price = str(price).rstrip('0').strip('.')
    return str(price)

def format_hour_minutes(hour, minute):
    return '{0}:{1}'.format(format_digital(hour), format_digital(minute))

