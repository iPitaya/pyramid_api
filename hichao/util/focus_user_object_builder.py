# -*- coding:utf-8 -*
from hichao.banner.models.banner_CMS import get_banner_components_by_flags_key_cache
from hichao.follow.models.follow import (
    get_user_follow_status,
    forum_followed_count,
)

from hichao.forum.models.star_user import(
    user_is_staruser,
    get_staruser_by_user_id,
)


def rebuild_focus_user_components_by_component(com, user_id=''):
    if com:
        component = com['component']
        following_id = component['action']['id']
        com['component']['action']['userId'] = component['action']['id']
        com['component']['action'].pop('id')
        com['component']['action']['userAvatar'] = component['picUrl']
        com['component']['action']['userName'] = component['action']['title']
        com['component']['action'].pop('title')
        if user_id:
            com['isfocus'] = str(get_user_follow_status(user_id, following_id))
        else:
            com['isfocus'] = '0'
        com['description'] = ''
        com['userTypeName'] = ''
        com['followType'] = ''
        com['id'] = following_id
        if user_is_staruser(following_id):
            staruser = get_staruser_by_user_id(following_id)
            com['description'] = staruser.user_desc
            _type = staruser.get_staruser_type()
            com['userTypeName'] = _type.get('userTypeName')
            com['followType'] = _type.get('followType')
        com['focusCount'] = str(forum_followed_count(following_id))
        return com
    else:
        return {}

def build_focus_user_components_by_component_by_nav_name(nav_name, nav_id, user_id='', com_type='cell'):
    coms = get_banner_components_by_flags_key_cache(nav_name, com_type)
    com_items = []
    ui = {}
    com_user = {}
    for com in coms:
        re_com = rebuild_focus_user_components_by_component(com, user_id)
        if re_com:
            com_items.append(re_com)
    com_user['componentType'] = 'ForumFocusUserCell'
    com_user['id'] = str(nav_id)
    com_user['focus_users'] = com_items
    ui['component'] = com_user
    return ui

