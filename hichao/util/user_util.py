from hichao.points.models.points import point_by_user_id
from hichao.cache.cache import deco_cache
from hichao.util.date_util import DAY
from icehole_client.throne_client import ThroneClient
from hichao.util.statsd_client import timeit

scores = (0, 500, 1000, 3000, 6000, 10000, 18000, 30000, 50000, 100000)
levels = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

score_level_dict = dict(zip(scores, levels))
level_score_dict = dict(zip(levels, scores))

timer = timeit('hichao_backend.util_userutil')

def is_deletable(user_id, com):
    uid = int(com['component'].get('userId', 0))
    return int(user_id) == uid and True or False

def is_owner(user_id, com):
    return is_deletable(user_id, com)

@timer
def get_level(score):
    level = 1
    if not score: score = 0
    for need_score in scores:
        if int(score) >= need_score:
            level = score_level_dict[need_score]
    return level

def get_need_score(level):
    return level_score_dict[level + 1]

@timer
def get_user_score(user_id):
    score = point_by_user_id(user_id)
    if not score: score = 0
    return score

@timer
def get_user_level(user_id):
    return get_level(point_by_user_id(user_id))

@deco_cache(prefix = 'user_is_admin', recycle = DAY)
def user_is_admin(user_id, use_cache = True):
    client = ThroneClient()
    try:
        admin = client.is_user_in_group(int(user_id), 'forum_admin')
        if admin:
            status = admin.status
            if status:
                return 1
            else:
                return 0
        else:
            return 0
    except:
        return 0

@deco_cache(prefix = 'user_is_custom', recycle = DAY)
def user_is_custom(user_id, use_cache = True):
    client = ThroneClient()
    try:
        admin = client.is_user_in_group(int(user_id), 'forum_custom')
        if admin:
            status = admin.status
            if status:
                return 1
            else:
                return 0
        else:
            return 0
    except:
        return 0

def user_change_password(user_id, password):
    client = ThroneClient()
    try:
        change_result_info = client.user_our_change_passwd(user_id, password)
    except Exception,e:
        print e

