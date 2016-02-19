#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hichao.base.lib.timetool import today_days, ONE_DAY_SECOND
from hichao.feed import ACTIVITY_STATUS_DIGIT
from hichao.base.lib.redis import redis, redis_key, redis_slave
from hichao.base.celery.db import celery
from hichao.points.models.point_activity import point_activity_new
from hichao.user.models.user import get_user_item_by_user_id, get_user_city_by_user_id
from hichao.util.statsd_client import timeit

REDIS_POINTS_BY_USER_ID = redis_key.PointsByUserId()  # hset
REDIS_POINTS_DAILY_BY_USER_ID = redis_key.PointsDailyByUserId("%s-%s")
#set expire 3 day
REDIS_POINTS_COLLECT_DAILY_BY_USER_ID = redis_key.PointsCollectDailyByUserId(
    "%s-%s")
REDIS_POINTS_POST_THREAD_DAILY_BY_USER_ID = redis_key.PointsPostThreadDailyByUserId(
    "%s-%s")

#REDIS_POINTS_STAR_COMMENT_DAILY_BY_USER_ID= redis_key.PointsStarCommentDailyByUserId("%s")
#REDIS_POINTS_SKU_COMMENT_DAILY_BY_USER_ID= redis_key.PointsSkuCommentDailyByUserId("%s")
#REDIS_POINTS_TOPIC_COMMENT_DAILY_BY_USER_ID = redis_key.PointsTopicCommentByUserId("%s")
#REDIS_POINTS_THREAD_COMMENT_DAILY_BY_USER_ID = redis_key.PointsThreadCommentDailyByUserId("%s")
# merge comment count for limit
REDIS_POINTS_COMMENT_DAILY_BY_USER_ID = redis_key.PointsCommentDailyByUserId(
    "%s-%s")
REDIS_POINTS_SHARE_DAILY_BY_USER_ID = redis_key.PointsShareDailyByUserId(
    "%s-%s")
REDIS_POINTS_LOGIN_DAILY_BY_USER_ID = redis_key.PointsLoginDailyByUserId(
    "%s-%s")
#hset
REDIS_POINTS_CONTINUOUS_LOGIN_BY_USER_ID = redis_key.PointsContinuousLoginByUserId(
)
REDIS_POINTS_CONTINUOUS_LOGIN_DAILY_CHECK_BY_USER_ID = redis_key.PointsContinuousLoginDailyCheckByUserId(
    "%s-%s")

POINT_DALIY_MAX = 300
POINT_COLLECT_DAILY_MAX = 10
POINT_POST_THREAD_MAX = 50
POINT_COMMENT_MAX = 20

timer = timeit('hichao_backend.m_points')

def point_daily(func):
    def _(user_id, method):
        key = REDIS_POINTS_DAILY_BY_USER_ID % (today_days(), user_id)
        score = redis.get(key)
        if score and int(score) >= POINT_COLLECT_DAILY_MAX:
            return 0
        return func(user_id, method)
    return _


@timer
def point_daily_max_incrby(user_id, score):
    key = REDIS_POINTS_DAILY_BY_USER_ID % (today_days(), user_id)
    p = redis.pipeline(transaction=False)
    p.incrby(key, score)
    p.expire(key, 3 * ONE_DAY_SECOND)
    p.hincrby(REDIS_POINTS_BY_USER_ID, user_id, score)
    return p.execute()


@timer
def point_decrby(user_id, score):
    key = REDIS_POINTS_BY_USER_ID
    point = redis_slave.hget(key, user_id)
    if point:
        if int(point) >= score:
            redis.hincrby(key, user_id, -score)
        else:
            redis.hset(key, user_id, 0)
        return score
    return 0


@timer
@point_daily
def point_collect(user_id, method=None):
    # 不需要判断是否收藏，因为也要删除积分的。
    point = 1
    if method != "rm":
        score = redis.get(REDIS_POINTS_COLLECT_DAILY_BY_USER_ID%(today_days(), user_id)) 
        if not score or int(score) < POINT_COLLECT_DAILY_MAX: 
            point_daily_max_incrby(user_id, point)
            return point
        return 0 
    else:
        point_decrby(user_id, point)
        return point


@timer
@point_daily
def point_post_thread(user_id, method=None):
    point = 5
    if method != "rm":
        score = redis.get(
            REDIS_POINTS_POST_THREAD_DAILY_BY_USER_ID % (today_days(), user_id))
        if not socre or int(score) < POINT_POST_THREAD_MAX:
            key = REDIS_POINTS_POST_THREAD_DAILY_BY_USER_ID % (
                today_days(), user_id)
            p = redis.pipeline(transaction=False)
            p.incrby(key, point)
            p.expire(key, 3 * ONE_DAY_SECOND)
            p.execute()
            point_daily_max_incrby(user_id, point)
            return point 
        return 0
    else:
        point_decrby(user_id, point)
        return point


@timer
@point_daily
def point_comment(user_id, method=None):
    point = 2
    if method != "rm":
        key = REDIS_POINTS_COMMENT_DAILY_BY_USER_ID % (today_days(), user_id)
        socre = redis.get(key)
        if not socre  or int(socre) < POINT_COMMENT_MAX:
            p = redis.pipeline(transaction=False)
            p.inrcby(key, point)
            p.expire(key, 3 * ONE_DAY_SECOND)
            p.execute()
            point_daily_max_incrby(user_id, point)
            return point 
        return 0
    else:
        point_decrby(user_id, point)
        return point


# 不受point_daily限制
@timer
def point_daily_login(user_id):
    point = 10
    point_continuous_login(user_id)
    key = REDIS_POINTS_LOGIN_DAILY_BY_USER_ID % (today_days, user_id)
    socre = redis.get(key)
    if not score:
        redis.setex(key, 1, 2 * ONE_DAY_SECOND)
        point_daily_max_incrby(user_id, point)
        return point
    return 0


@timer
def point_continuous_login(user_id, method=None):
    continuous = 5
    points = 5
    continuous_key = REDIS_POINTS_CONTINUOUS_LOGIN_BY_USER_ID
    if not redis.get(REDIS_POINTS_LOGIN_DAILY_BY_USER_ID % (today_days() - 1, user_id)):
        redis.hset(continuous_key, user_id, 1)
        return 1

    # 检查连续登录是否设置过
    continuous_check = REDIS_POINTS_CONTINUOUS_LOGIN_DAILY_CHECK_BY_USER_ID % user_id
    if not redis.get(continuous_check % (today_days(), user_id)):
        redis.setex(continuous_check %
                    (today_days(), user_id), 1, ONE_DAY_SECOND)
        # 5天一个循环
        _continuous = redis_slave.hget(continuous_check, user_id)
        if _continuous:
            if int(_continuous) < 5:
                point_daily_max_incrby(user_id, points)
                redis.hincrby(continuous_key % user_id)
            elif int(_continuous) == 5:
                redis.hset(continuous_key, user_id, 1)
    return 0


# 以下应不受point_daily影响
@timer
def point_improve_personal_nickname(user_id, method=None):
    # 获取user_id对应的nickname，未修改状态为''
    user_nickname = get_user_item_by_user_id(user_id, "nickname")
    if user_nickname:
        point_daily_max_incrby(user_id, 20)
        return 20
    else:
        return 0


@timer
def point_improve_personal_avatar(user_id, method=None):
    # 判断是否为第三方头像，是否已经修改
    # 获取user_id对应的avatar_img_id，未修改状态为0
    user_avatar_img_id = get_user_item_by_user_id(user_id, "avatar_img_id")
    if user_avatar_img_id:
        point_daily_max_incrby(user_id, 20)
        return 20
    else:
        return 0


@timer
def point_improve_personal_email(user_id, method=None):
    # 获取user_id对应的email，未修改状态为''
    user_email = get_user_item_by_user_id(user_id, "email")
    if user_email:
        point_daily_max_incrby(user_id, 20)
        return 20
    else:
        return 0

@timer
def point_improve_personal_city(user_id, method=None):
    # 获取user_id对应的city，在user_location表中，未修改状态为''
    user_city = get_user_city_by_user_id(user_id)
    if user_city:
        point_daily_max_incrby(user_id, 20)
        return 20
    else:
        return 0

@timer
def point_improve_personal_connect(user_id, method=None):
    # 获取user_id对应的connect，联系方式为QQ或者手机号。未修改状态为''
    user_connect = get_user_item_by_user_id(user_id, "connect")
    if user_connect:
        point_daily_max_incrby(user_id, 30)
        return 30
    else:
        return 0

@timer
def point_share(user_id, method=None):
    pass

POINTS_ADD = {
    "star_collect": point_collect,
    "sku_collect": point_collect,
    "topic_collect": point_collect,
    "thread_collect": point_collect,
    "star_comment": point_comment,
    "sku_comment": point_comment,
    "topic_comment": point_comment,
    "thread_comment": point_comment,
    "post_thread": point_post_thread,
    "daily_login": point_daily_login,
    "improve_personal_nickname": point_improve_personal_nickname,
    "improve_personal_avatar": point_improve_personal_avatar,
    "improve_personal_email": point_improve_personal_email,
    "improve_personal_city": point_improve_personal_city,
    "improve_personal_connect": point_improve_personal_connect,
    "share": point_share,
}


@celery.task
def point_change(user_id, activity, item_id, ts, method=None):
    activity_id = ACTIVITY_STATUS_DIGIT[activity]

    r = POINTS_ADD[activity](user_id, method)
    
    if r:
        point_activity_new(user_id, activity_id, item_id, ts, method)

@timer
def point_by_user_id(user_id):
    return redis_slave.hget(REDIS_POINTS_BY_USER_ID, user_id)

if __name__ == "__main__":
    print point_by_user_id(242178)
    pass
