# -*- coding:utf-8 -*-
class ACTIVITY_STATUS:
    class STAR_COLLECT:
        STATUS = 'star_collect'
        CODE = '10'

    class SKU_COLLECT:
        STATUS = 'sku_collect'
        CODE = '20'

    class TOPIC_COLLECT:
        STATUS = 'topic_collect'
        CODE = '25'

    class THREAD_COLLECT:
        STATUS = 'thread_collect'
        CODE = '30'

    class POST_NEW_THREAD:
        STATUS = 'post_new_thread'
        CODE = '40'

    class STAR_COMMIT:
        STATUS = 'star_commit'
        CODE = '50'

    class SKU_COMMIT:
        STATUS = 'sku_commit'
        CODE = '51'

    class TOPIC_COMMIT:
        STATUS = 'topic_commit'
        CODE = '52'

    class THREAD_COMMIT:
        STATUS = 'thread_commit'
        CODE = '53'

    class DAILY_LOGIN:
        STATUS = 'daily_login'
        CODE = '60'

    class CONTINUOUS_LOGIN:
        STATUS = 'continuous_login'
        CODE = '61'

    class IMPROVE_PERSONAL_NICKNAME:
        STATUS = 'improve_personal_nickname'
        CODE = '70'

    class IMPROVE_PERSONAL_AVATAR:
        STATUS = 'improve_personal_avatar'
        CODE = '71'

    class IMPROVE_PERSONAL_EMAIL:
        STATUS = 'improve_personal_email'
        CODE = '72'

    class IMPROVE_PERSONAL_CITY:
        STATUS = 'improve_personal_city'
        CODE = '73'

    class IMPROVE_PERSONAL_CONNECT:
        STATUS = 'improve_personal_connect'
        CODE = '74'

    class SHARE:
        STATUS = 'share'
        CODE = '80'


    ITEMS = [
        STAR_COLLECT,
        SKU_COLLECT,
        TOPIC_COLLECT,
        THREAD_COLLECT,
        POST_NEW_THREAD,
        STAR_COLLECT,
        SKU_COMMIT,
        TOPIC_COMMIT,
        THREAD_COMMIT,
        DAILY_LOGIN,
        CONTINUOUS_LOGIN,
        IMPROVE_PERSONAL_NICKNAME,
        IMPROVE_PERSONAL_AVATAR,
        IMPROVE_PERSONAL_EMAIL,
        IMPROVE_PERSONAL_CITY,
        IMPROVE_PERSONAL_CONNECT,
        SHARE,
        ]

ACTIVITY_STATUS_DIGIT = {ITEM.STATUS:ITEM.CODE for ITEM in ACTIVITY_STATUS.ITEMS}

