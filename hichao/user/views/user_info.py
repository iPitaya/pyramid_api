# -*- coding: utf-8 -*-
from pyramid.view import view_defaults
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from hichao.base.views.view_base import View
from hichao.base.lib.require import require, RequirementException
from hichao.user.models.user import (
    get_user_info,
    get_user_by_id,
    update_user_info,
    add_user_background,
    update_user_location,
)
from hichao.user.models.background import (
    get_background,
    get_background_list,
)
from hichao.user.models.authorized_user import get_authorized_user_ids
from hichao.util.pack_data import pack_data
from hichao.util.user_util import (
    get_user_score,
    get_user_level,
    get_need_score,
    user_is_admin,
)
from hichao.util.content_util import (
    filter_tag,
    content_has_sensitive_words,
)
from hichao.app.views.oauth2 import check_permission
from hichao.forum.models.banwu_tangzhu import user_is_tangzhu
from hichao.forum.models.star_user_type import get_star_user_type_img_url
from hichao.forum.models.star_user import (
    user_is_staruser,
    get_staruser_by_user_id,
)
from hichao.base.config import (
    TANGZHU_ICON,
    STARUSER_ICON,
    FALL_PER_PAGE_NUM,
    ROLE_USERINFO_STARUSER_ICON,
    ROLE_USERINFO_ADMIN_ICON,
    ROLE_FDFS_ADMIN_X2,
    ROLE_FDFS_TALENT_LIST,
)
from hichao.base.config import CDN_FAST_DFS_IMAGE_PREFIX
from hichao.feed.models.follow import Follow
from icehole_client.follow_client import FollowClient, FollowType
from random import randint
from hichao.util.statsd_client import statsd
from hichao.forum.models.star_user import get_business_id_and_name_by_user_id
#from icehole_client.goods_manager_client import Client as points_goods_client
#from icehole_client.points_manager_client import Client as points_manager_client
#from icehole_interface.points.base import ttypes as points_ttypes
import re
import string
from hichao.follow.models.follow import forum_following_count, forum_followed_count, get_user_follow_status
from hichao.collect.models.brand import (
    brand_count_by_user_id,
)
from hichao.util.image_url import build_star_user_icon

#g_result = points_ttypes.Result()
#g_activity = points_ttypes.Activity()
g_mobile_phone_regex = re.compile('(13|15|17|18)[0-9]{9}')


@view_defaults(route_name='update_info')
class UpdateUserInfoView(View):

    def __init__(self, request):
        super(UpdateUserInfoView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_update_info.get')
    @check_permission
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        uid = self.user_id
        data = {}
        if uid == -1:
            return '', {}
        else:
            data = get_user_info(uid)
        return '', data

    @statsd.timer('hichao_backend.r_update_info.put')
    @check_permission
    @view_config(request_method='PUT', renderer='json')
    @pack_data
    def put(self):
        uid = self.user_id

        if uid == -1:
            self.error['error'] = 'Token missed'
            self.error['errorCode'] = '21324'
            return '', {}
        elif uid == -2:
            self.error['error'] = 'User info expired.'
            self.error['errorCode'] = '20002'
            return '', {}

        nickname = self.request.params.get('nickname', '').strip()
        nickname = nickname.replace('\n', '')
        if not nickname:
            self.error['error'] = 'Arguments error.'
            self.error['errorCode'] = '10001'
            return '昵称不能为空。', {}
        gender = self.request.params.get('gender', '')
        constellation = self.request.params.get('constellation', '')
        location = self.request.params.get('location', '')
        common_email = self.request.params.get('common_email', '')
        birthday = self.request.params.get('birthday', '')
        connect = self.request.params.get('connect', '')
        nation = self.request.params.get('nation', '')
        province = self.request.params.get('province', '')
        city = self.request.params.get('city', '')
        longitude = self.request.params.get('lon', '')
        latitude = self.request.params.get('lat', '')
        nickname = filter_tag(nickname)

        if gender == "":
            gender = '男'
        gender = 1 if gender == '男' else 0
        if longitude == "":
            longitude = 0.0
        if latitude == "":
            latitude = 0.0

        #res_filter = self.filter_mobile_number(connect)
        # if res_filter:
        #    res_reward = points_manager_client().RewardImprove(uid)
        #    if res_reward != g_result.Successful:
        #        self.error['error']='Invalid phone number'
        #        self.err['errorCode'] = '33301'
        #        return '', {}

        info_code = update_user_info(uid, nickname, gender, constellation, common_email, birthday, connect, nation, province, city, longitude, latitude)
        #location_code = update_user_location(uid, nation, province, city, longitude, latitude)

        if info_code == 0:
            self.error['error'] = 'Update info operation failed'
            self.error['errorCode'] = '30001'
        # 重新生成缓存
        get_user_by_id(uid, use_cache=False)
        return '', {}

    def filter_mobile_number(self, number):
        if not number:
            return False
        tmp = ''
        for i in number:
            if i in '0123456789':
                tmp += i
            elif i == ' ':
                pass
            else:
                return False
        if g_mobile_phone_regex.match(tmp):
            return True


@view_defaults(route_name='user_info')
class UserInfoView(View):

    def __init__(self, request):
        super(UserInfoView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_user_info.get')
    @check_permission
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        '''get user id'''
        my_user_id = self.user_id if self.user_id else 0
        others_user_id = self.request.params.get('user_id', '')
        others_user_id = int(others_user_id) if others_user_id else 0
        user_id = my_user_id if others_user_id < 1 else others_user_id
        if user_id == -2:
            View.message(self, '20002', 'User info expired.')
            return '', {}
        if user_id < 1:
            View.message(self, '10001', 'Arguments error.')
            return '', {}
        user = get_user_by_id(user_id)
        if not user:
            return '', {}
        # user.test()

        '''get user base information'''
        data = {}
        data['userId'] = str(user_id)
        data['userName'] = user.get_component_user_name()
        data['userAvatar'] = user.get_component_user_avatar()
        level = get_user_level(user_id)
        data['userLevel'] = str(level)
        data['score'] = str(get_user_score(user_id))
        data['needScore'] = str(get_need_score(level))
        data['userRankIcon'] = user.get_component_user_rank_icon()

        ''' 添加 business_id 和 商家名 '''
        business_info = get_business_id_and_name_by_user_id(user_id)
        if business_info:
            data['businessId'] = str(business_info['business_id'])
            data['businessName'] = business_info['business_name']
            data['businessLogo'] = business_info['brand_logo']

        '''get role icon list'''
        role_icon_list = list()
        data['banwuIcon'] = TANGZHU_ICON if user_is_tangzhu(user_id) else ''
        res_staruser = get_staruser_by_user_id(user_id)

        data['starUserIcon'] = ''
        # 红人 类型
        data['userTypeName'] = ''
        if res_staruser:
            data['description'] = res_staruser.user_desc
            userType = res_staruser.get_staruser_type(False)
            userTypeName = ''
            # 产品需求：只有红人，明星，设计师时才显示大图标
            if userType and userType['userTypeName'] in ['红人', '明星', '设计师']:
                userTypeName = userType['userTypeName']
            data['userTypeName'] = userTypeName

            data['starUserIcon'] = STARUSER_ICON
            if userType and userType['imgUrl']:
                role_icon_list.append(build_star_user_icon(userType['imgUrl']))
#             else:
#                 role_icon_list.append(ROLE_USERINFO_STARUSER_ICON)
        is_admin = user_is_admin(user_id)
        if is_admin:
            # role_icon_list.append(ROLE_USERINFO_ADMIN_ICON)
            role_icon_list.append(ROLE_FDFS_ADMIN_X2)
        if len(role_icon_list) > 0:
            data['roleIcons'] = role_icon_list

        '''get following and followed'''
        follow_client = FollowClient()
        if my_user_id > 0:
            #my_follow = Follow(my_user_id)
            res = follow_client.has_follow(my_user_id, user_id, FollowType.USER)
            data['iFollowed'] = '1' if res else '0'
        #user_follow = Follow(user_id)
        #user_followed_num = user_follow.followers_stats()
        user_followed_num = follow_client.followers_stats(user_id, FollowType.USER)
        user_followed_num = user_followed_num if user_followed_num else 0
        data['followedNum'] = str(user_followed_num)
        user_following_num = follow_client.following_stats(user_id, FollowType.USER)
        user_following_num = user_following_num if user_following_num else 0
        data['followingNum'] = str(user_following_num)
        # 红人 设计师 明星
        data['userFansNum'] = str(forum_followed_count(user_id))
        data['userFollowNum'] = str(forum_following_count(user_id))
        data['isFollow'] = 0
        data['brandNum'] = str(brand_count_by_user_id(user_id))
        if my_user_id != others_user_id:
            data['isFollow'] = str(get_user_follow_status(my_user_id, others_user_id))
        data['followType'] = ''

        #'''get candy points'''
        #points = points_manager_client().GetPoints(user_id)
        # data['reputation'] = str(int(points))#float to int, int to string

        '''get background'''
        if user.background_img_id < 1:
            user.background_img_id = 11
        background = get_background(user.background_img_id)
        if background and background.id and background.id > 0:
            make_image_url = lambda x:\
                CDN_FAST_DFS_IMAGE_PREFIX() + \
                x.fdfs_name
            data['background'] = make_image_url(background)
            data['background_id'] = str(user.background_img_id)
        return '', data


@view_defaults(route_name='background')
class BackgroundView(View):

    def __init__(self, request):
        super(BackgroundView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.background.get')
    @check_permission
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        data = dict()
        flag = self.request.params.get('flag', '')
        flag = int(flag) if len(flag) > 0 else 0
        res = get_background_list(flag, FALL_PER_PAGE_NUM)

        make_image_url =\
            lambda x:\
            CDN_FAST_DFS_IMAGE_PREFIX() +\
            x.fdfs_name

        make_image_thumbnail_url =\
            lambda x:\
            CDN_FAST_DFS_IMAGE_PREFIX() +\
            x.fdfs_name +\
            '?imageMogr2/thumbnail/!50p/quality/70'

        data['backgrounds'] =\
            map(lambda x:
                {'id': x.id,
                 'url': make_image_url(x),
                 'thumbnailUrl': make_image_thumbnail_url(x)},
                res)
        return '', data

    @statsd.timer('hichao_backend.background.post')
    @check_permission
    @view_config(request_method='POST', renderer='json')
    @pack_data
    def post(self):
        data = dict()

        if self.user_id == -1:
            View.message(self, '2134', 'Token missed.')
            return '', data
        elif self.user_id == -2:
            View.message(self, '20002', 'User info expired.')
            return '', data

        background_id = string.atoi(self.request.params.get('id', '0'))
        if background_id == 0:
            View.message(self, '33302', 'Background id is not in params.')
            return '', data

        res = add_user_background(self.user_id, background_id)
        if res == 0:
            View.message(self, '33303',
                         'Failed to set background(background_id:%d, user_id: %d).' %
                         (background_id, self.user_id))
            return '', data
        get_user_by_id(self.user_id, use_cache=False)
        return '', data

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')
