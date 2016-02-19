# -*- coding:utf-8 -*-

from pyramid.view import (
    view_defaults,
    view_config,
)
from hichao.forum.models.thread import (
    get_none_top_thread_ids,
    get_thread_by_id,
    get_elite_thread_ids,
    get_top_thread_ids,
)

from hichao.forum.models.forum import (
    get_forum_name_by_cat_id,
)
from hichao.forum.models.star_user import(
    get_user_ids_by_cat_id,    
)

from hichao.forum.models.recommend_tags import(
    get_forum_navigator,
    get_navigator_by_nav_id,
)
from hichao.forum.models.tag import get_tag_by_id
from hichao.follow.models.follow import get_following_user_ids_by_user_id
from hichao.post.models.post import get_post_ids_by_user_ids
from hichao.base.views.view_base import View
from hichao.base.config import (
    MYSQL_MAX_TIMESTAMP,
    FALL_PER_PAGE_NUM,
    COMMENT_TYPE_THREAD,
    REDIS_CONFIG,
    THREAD_OWNER_ICON,
)
from hichao.util.pack_data import (
    pack_data,
    version_ge,
    version_eq,
)
from hichao.util.object_builder import (
    build_lite_thread_by_id,
    build_lite_top_thread_by_id,
    build_lite_subthread_with_user_id,
    build_topic_list_item_by_id,
    build_main_subthread_by_id,
    build_choiceness_thread_by_item,
    build_topic_list_item_by_theme_id,
    build_lite_post_by_id,
    build_forum_tag_by_tag_id,
)

from hichao.comment.models.sub_thread import (
    get_subthread_ids,
    get_filter_subthread_ids,
    get_subthread_ids_for_thread,
)
from hichao.comment.models.comment import (
    get_comment_count,
    get_comment_count_for_thread,
)
from hichao.collect.models.thread import thread_user_count
from hichao.app.views.oauth2 import check_permission
from hichao.forum.models.online import set_online_user
from hichao.forum.models.uv import thread_uv_incr
from hichao.forum.models.pv import thread_pv_incr
from hichao.timeline.models.hot_threads import get_hot_thread_ids
from hichao.forum.models.thread_recommend import (
    get_recommend_thread_ids,
    get_home_recommend_thread_ids_by_nav_id,
)
from hichao.util.statsd_client import statsd
from hichao.util.component_builder import rebuild_focus_user_components_by_component
from icehole_client.message_client import ThreadClient
from hichao.forum.models.thread_choiceness import (
    get_thread_choiceness_items,
    get_thread_choiceness_ids,
    get_choiceness_thread_by_id,
)

from hichao.banner.models.banner_CMS import get_banner_components_by_flags_key_cache
from hichao.new_forum.config import TAB_NAME_BANNER_DICT
import datetime
import redis
client = redis.Redis(**REDIS_CONFIG)

from icehole_client.coflex_agent_client import CoflexAgentClient


def get_hot_thread_ids_by_forum_id(forum_id, offset, limit):
    key = '{0}_hot_thread'.format(forum_id)
    return client.lrange(key, offset, offset + limit)


@view_defaults(route_name='new_forum_thread')
class ThreadView(View):

    def __init__(self, request):
        super(ThreadView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_new_forum_thread.get')
    @check_permission
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        thread_id = self.request.params.get('thread_id', '')
        if not thread_id:
            self.error['error'] = 'Arguments missing.'
            self.error['errorCode'] = '10002'
            return '', {}

        # add thread uv, pv
        gi = self.request.params.get('gi', '')
        if gi:
            thread_uv_incr(gi, thread_id)
        thread_pv_incr(thread_id)

        # state 用来标记用户操作，0:第一次进来，取下一页数据，这次请求需要返回主帖内容，1:取下一页，2:取上一页。
        state = self.request.params.get('state', '')
        state = int(state) if state else 0
        # 是否只看楼主，0:查看所有，1:只看楼主。
        only_owner = self.request.params.get('only_owner', '')
        only_owner = 1 if only_owner else 0
        # 是否只看图片，0:查看所有，1:只看图片。
        only_img = self.request.params.get('only_img', '')
        only_img = 1 if only_img else 0
        # 分页标记
        flag = self.request.params.get('flag', '')
        flag = int(flag) if flag else 0

        # 正序排还是倒序排，1:正序，0:倒序。
        asc = self.request.params.get('asc', '')
        asc = 1 if not asc else int(asc)

        # 倒序排时flag需要做不同处理。
        num_floor = get_comment_count_for_thread(COMMENT_TYPE_THREAD, thread_id)
        # 获取实际的楼层数
        if not asc:     # 如果是倒序（asc为正序，所以是not asc）
            # 只看楼主和只看图片是按offset+limit做的分页，所以最后以flag为负数作为没有下一页标记。
            # 如果这里flag为一个负数，则说明已经没有下一页了，直接返回。
            if only_img or only_owner:
                if flag < 0:
                    return u'', {'flag': '-1', 'items': []}
            else:
                # 如果是倒序排而且没有给flag值，说明是第一页，flag默认用当前最大楼层。
                if not flag:
                    flag = num_floor
                    flag = flag if flag else 0
                # 已经是倒序排了（查看全部时），flag还小于1，说明肯定没有下一页了，直接返回空数据。
                # 因为正序排的时候，flag是递增的，倒序时是递减的，所以只在倒序排的时候做这个判断。
                if flag < 1 and state != 0:
                    return u'', {'flag': '-1', 'items': []}

        thread = get_thread_by_id(thread_id)
        if not thread:
            self.error['error'] = 'Operation failed.'
            self.error['errorCode'] = '30001'
            return u'该帖子不存在。', {}

        # 设置用户在该帖子所在版块为在线状态，用于显示在线人数。
        set_online_user(gi, thread.get_component_forum_id())

        user_id = self.user_id
        owner_id = 0
        if only_owner:
            owner_id = int(thread.get_component_user_id())
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        # 用户发的链接转成单品后，前端显示时单品和文本内容是否要分开显示。0为不分开，1为分开。
        split_items = 0
        # 是否支持应用内部跳转，0:不支持，1:支持。
        #   比如帖子内容里有一个我们自己的帖子链接，为0时跳转到webview打开网页，为1时应用内跳转到该帖子详情。
        inner_redirect = 0
        # 是否支持webp格式的图片，0：不支持，1：支持。
        support_webp = 0
        # 是否支持 品牌店铺 0：不支持，1：支持
        support_brandstore = 0
        # 这些平台标记之后的版本支持单品和内容分开显示及内部跳转。
        if gf == 'iphone':
            if version_ge(gv, '5.2'):
                split_items = 1
                inner_redirect = 1
            if version_ge(gv, '6.0'):
                support_webp = 1
            if version_ge(gv, '6.3.0'):
                support_brandstore = 1
        elif gf == 'android':
            if version_ge(gv, '60'):
                split_items = 1
                inner_redirect = 1
            if version_ge(gv, '630'):
                support_brandstore = 1
        elif gf == 'ipad':
            if version_ge(gv, '5.0'):
                split_items = 1
                inner_redirect = 1

        data = {}
        data['items'] = []
        if asc:  # 正序时
            if state <= 1:  # 正序时第一次或者取下一页
                offset = flag
                limit = FALL_PER_PAGE_NUM
            else:  # 正序时取上一页
                offset_raw = flag - FALL_PER_PAGE_NUM + 1
                if offset_raw > 0:
                    offset = offset_raw
                    limit = FALL_PER_PAGE_NUM
                else:
                    offset = 0
                    limit = flag + 1  # 防止重复
        else:  # 倒序时
            if state <= 1:
                offset_raw = flag - FALL_PER_PAGE_NUM
                if offset_raw > 0:
                    offset = offset_raw
                    limit = FALL_PER_PAGE_NUM
                else:
                    offset = 0
                    limit = flag  # 防止重复
            else:
                offset = flag
                limit = FALL_PER_PAGE_NUM
        # 正序排取下一页数据时  与   倒序排取上一页数据时  楼层计算方式是相同的。
        # if (state <= 1 and asc) or (state == 2 and not asc):
            #offset = flag
            # sfloor = flag                           # 数字靠前的楼层 small floor
            # bfloor = flag + FALL_PER_PAGE_NUM       # 数字靠后的楼层 big floor
        # else:
            #sfloor = flag - FALL_PER_PAGE_NUM
            #bfloor = flag
        ids = []
        if only_owner or only_img:
            # 只看楼主和只看图片不支持跳转到楼层然后查看上一页。
            ids = get_filter_subthread_ids(thread_id, flag, FALL_PER_PAGE_NUM, owner_id, only_img, asc)
        else:        # 如果算出来的较大的楼层仍小于1，说明已经没有内容了，所以只考虑bfloor>0的情况。
            ids = get_subthread_ids_for_thread(thread_id, offset, limit, asc)
        #_bfloor = 0
        for id in ids:
            com = build_lite_subthread_with_user_id(id, split_items, user_id, inner_redirect, support_webp, support_brandstore)
            if com:
                if str(com['component']['userId']) == str(thread.get_component_user_id()):
                    # 如果是楼主的回复，设置楼主图标。
                    if com['component'].has_key('roleIcons'):
                        com['component']['roleIcons'].insert(0, THREAD_OWNER_ICON)
                    else:
                        com['component']['roleIcons'] = [THREAD_OWNER_ICON, ]
                # 记录最后的楼层。
                # 因为上边计算出来的楼层与数据库取出来的楼层个数可能不一致，比如这次分页需要取10-20楼的数据，可能只到15楼，
                #   在最后返回分页标记的时候需要把15返回，前端获取下一页的时候会再把15传回来，如果返回20，会取不到数据。
                #   其实这时候已经没有下一页了，但如果不返回flag，前端会提示已经没有内容了，其他用户新的回复就无法显示，
                #   比如现在是15楼，有用户回复后是16楼，flag返回是15，然后前端取下一页时会取16到26楼，但flag返回20时就取不到16楼了。
                #   所以最后需要返回flag=15。
                # 倒序时因为不牵扯到下一页可能还有用户新发回复的问题，所以不用处理，最后计算flag时只需要sfloor就够了，
                #   所以这里只在正序情况下进行处理。
                # if asc:
                    #bfloor = com['flag']
                # else:
                    # if not _bfloor:
                        #bfloor = com['flag']
                        #_bfloor = 1
                # del(com['flag'])
                data['items'].append(com)

        # 用于标记是否需要显示主楼内容
        need_main_subthread = 0
        curr_num = len(ids)
        if only_img or only_owner:      # 只看图片和只看楼主
            # 正序请求第一页数据时，需要显示主楼内容。
            if asc and state == 0:
                need_main_subthread = 1
            if not asc:
                # 倒序，如果取出来的一页内容不足一页，说明已经没有下一页了，需要显示主楼内容。
                if curr_num < FALL_PER_PAGE_NUM:
                    need_main_subthread = 1
        else:
            # 当正序取到第一页数据时  和  倒序取到最后一页数据时（正倒序都是以sfloor是否小于1来判断），需要把主楼也显示出来。
            # 当较小的楼层不大于1时，说明肯定是第一页了（或倒序的最后一页）。
            # 计算出来的sfloor值可能会小于0，所以此处判断使用<=。
            if not asc:  # 倒序
                if (state == 0 and curr_num < FALL_PER_PAGE_NUM) or (state == 1 and curr_num < FALL_PER_PAGE_NUM):
                    need_main_subthread = 1
            else:  # 正序
                if state == 0:
                    if flag < 1:
                        need_main_subthread = 1
                if state == 2:
                    if curr_num < FALL_PER_PAGE_NUM:
                        need_main_subthread = 1

        if only_img and not thread.has_image():
            need_main_subthread = 0

        if need_main_subthread:
            com = build_main_subthread_by_id(thread_id, split_items, inner_redirect, support_webp, support_brandstore)
            if com:
                com['component']['isMain'] = '1'
                com['component']['id'] = ''
                # 正序时，主楼放到列表的最前；倒序时，主楼放到列表的最后。
                if asc:
                    data['items'].insert(0, com)
                else:
                    data['items'].append(com)
        # 第一次请求时，需要返回帖子标题、版块等内容，因为不是在回复列表显示，所以单独拿出来拼装数据。
        if state == 0:
            data['viewCount'] = thread.get_component_pv()
            comment_count = get_comment_count_for_thread(COMMENT_TYPE_THREAD, thread_id)
            if not comment_count:
                comment_count = 0
            data['commentCount'] = str(comment_count)
            coll_count = thread_user_count(thread_id, ts=1)
            if not coll_count:
                coll_count = 0
            data['collectionCount'] = str(coll_count)
            data['title'] = thread.get_component_title()
            data['icons'] = thread.get_component_icon()
            data['forum'] = thread.get_component_category()
            data['categoryId'] = thread.get_component_forum_id()
            data['id'] = str(thread_id)
            data['shareAction'] = thread.get_share_image()
            data['forbidComment'] = thread.get_component_forbid_comment()
            # 当request参数clear_msg_num不为空时（用户从消息列表跳转过来时会传入此参数），当前用户当前帖子的消息置为已读。
            clear_msg_num = self.request.params.get('clear_msg_num', '')
            if clear_msg_num and user_id > 0:
                client = ThreadClient()
                client.thread_msg_list(user_id, int(thread_id))
        if only_owner or only_img:
            num = len(ids)
            if asc:
                flag = flag + num
                data['flag'] = str(flag)
            else:
                if num < FALL_PER_PAGE_NUM:
                    data['flag'] = '-1'
                else:
                    flag = flag - num
                    data['flag'] = str(flag)
        else:
            num = len(ids)
            if asc:             # 正序
                if state == 0:                              # 第一次请求
                    if flag > 0:                          # 计算上标界
                        data['flagPre'] = str(flag - 1)
                    else:
                        data['flagPre'] = ''
                    if num > 0:
                        data['flag'] = str(flag + num)
                    else:
                        data['flag'] = str(flag)
                elif state == 1:                            # 取下一页内容，上标界前端会保存，只返回下标界
                    if num > 0:
                        data['flag'] = str(flag + num)
                    else:
                        data['flag'] = str(flag)
                elif state == 2:                            # 取上一页内容，下标界前端会保存，只返回上标界
                    if flag - FALL_PER_PAGE_NUM > 0:
                        data['flagPre'] = str(flag - num)
                    else:
                        data['flagPre'] = ''
                        # ios5.1版前端bug，取上一页操作，没有上一页时，刷新页面前端会直接取自己记录的下标记作为flag取下一页内容，
                        #   而不是取第一页的内容。这里当没有上一页时，返回一个下标界覆盖前端自己保存的下标界。
                        # if gf == 'iphone' and version_eq(gv, 5.1):
                        #data['flag'] = str(bfloor + 1)
            else:               # 倒序
                if state == 0 and num > 0:
                    data['flagPre'] = str(flag + 1)
                if state == 1 or state == 0:
                    if num >= FALL_PER_PAGE_NUM:
                        data['flag'] = str(flag - num)
                    else:
                        data['flag'] = '-1'
                elif state == 2:
                    if num >= FALL_PER_PAGE_NUM:
                        data['flagPre'] = str(flag + num)
                    else:
                        data['flagPre'] = '-1'
        return '', data


@view_defaults(route_name='new_forum_threads')
class ThreadsView(View):

    def __init__(self, request):
        super(ThreadsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_new_forum_threads.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        forum_id = self.request.params.get('category_id', '')
        if not forum_id:
            return self.get_forum_all()
        else:
            return self.get_forum(forum_id)

    def get_forum_all(self):
        flag = self.request.params.get('flag', '')
        is_top = False
        if flag == '':
            is_top = True
            flag = 0
        elif flag == 't':
            flag = 0
        elif flag.startswith('t'):
            is_top = True
            flag = int(flag[1:])
        data = {}
        top_threads = []
        items = []
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        #if gv: gv = gv_float(gv)
        support_topic = 0
        support_webp = 0
        support_pic = 0
        with_top_icon = 0
        without_icon = 1
        if gf == 'iphone':
            if version_ge(gv, '5.3'):
                support_topic = 1
            if version_ge(gv, '6.0'):
                support_webp = 1
        elif gf == 'android':
            if version_ge(gv, 61):
                support_topic = 1
        elif gf == 'ipad':
            if version_ge(gv, '5.0'):
                support_topic = 1
        _top_ids = []
        num = 0
        if is_top:
            top_ids = get_recommend_thread_ids(flag)
            num = len(top_ids)
            _top_ids = [int(id[1]) for id in top_ids if id[0] == 'thread']
            for id in top_ids:
                _type, _id = id
                com = {}
                if _type == 'topic' and support_topic:
                    com = build_topic_list_item_by_id(_id, support_webp, support_pic)
                elif _type == 'theme':
                    com = build_topic_list_item_by_theme_id(_id, support_pic)
                else:
                    com = build_lite_thread_by_id(_id, with_top_icon, without_icon, support_webp)
                if com:
                    items.append(com)
        else:
            ids = get_hot_thread_ids(flag, FALL_PER_PAGE_NUM)
            num = len(ids)
            for id in ids:
                _id, _type = id.get_type_id(), id.get_type()
                # if int(_id) in _top_ids: continue
                com = {}
                if _type == 'topic' and support_topic:
                    com = build_topic_list_item_by_id(_id, support_webp, support_pic)
                elif _type == 'theme':
                    com = build_topic_list_item_by_theme_id(_id, support_pic)
                elif _type == 'thread':
                    com = build_lite_thread_by_id(_id, with_top_icon, without_icon, support_webp)
                    if com:
                        com['component']['showIcon'] = 'forum'
                if com:
                    items.append(com)
        flag = int(flag) if flag else 0
        #num = len(items)
        if num >= FALL_PER_PAGE_NUM:
            if is_top:
                data['flag'] = 't' + str(flag + FALL_PER_PAGE_NUM)
            else:
                data['flag'] = str(ids[-1].get_id())
        else:
            if is_top:
                data['flag'] = 't'
        data['topThreads'] = top_threads
        data['items'] = items
        return '', data

    def get_forum(self, forum_id):
        gf = self.request.params.get('gf', '')
        gv = self.request.params.get('gv', '')
        support_webp = 0
        if (version_ge(gv, '6.0') and gf == 'iphone'):
            support_webp = 1
        if forum_id:
            gi = self.request.params.get('gi', '')
            set_online_user(gi, forum_id)

        tp = self.request.params.get('type', 'latest')
        if not tp:
            tp = 'latest'
        flag = self.request.params.get('flag', '')
        # if tp == 'latest' or tp == 'elite':
        if tp == 'elite':
            flag = flag if flag else MYSQL_MAX_TIMESTAMP
        else:
            flag = int(flag) if flag else 0

        data = {}
        data['topThreads'] = []
        items = []
        ids = []
        top_ids = []
        with_top_icon = 0
        without_icon = 0
        total_in_search = 0
        if tp == 'latest':
            with_top_icon = 1
            try:
                name = get_forum_name_by_cat_id(forum_id)
                if name:
                    result = CoflexAgentClient().search_forum(query=name, offset=flag, limit=FALL_PER_PAGE_NUM, search_tags=True)
                    for it in result['items']:
                        if it['type'] == 'threads':
                            ids.append(it['id'])
                    total_in_search = result['total']
            except Exception as e:
                print 'get_forum latest exception:', e
#             if flag == MYSQL_MAX_TIMESTAMP:
#                 top_ids = get_top_thread_ids(forum_id)
#             ids = get_none_top_thread_ids(flag, FALL_PER_PAGE_NUM, forum_id)
        elif tp == 'hot':
            ids = get_hot_thread_ids_by_forum_id(forum_id, flag, FALL_PER_PAGE_NUM)
        elif tp == 'elite':
            ids = get_elite_thread_ids(forum_id, flag, FALL_PER_PAGE_NUM)
        for _id in top_ids:
            com = build_lite_thread_by_id(_id, with_top_icon, without_icon, support_webp)
            if com:
                del(com['uts'])
                items.append(com)
        with_top_icon = 0
        for _id in ids:
            com = build_lite_thread_by_id(_id, with_top_icon, without_icon, support_webp)
            if com:
                com['component']['showIcon'] = 'user'
                # if tp == 'latest' or tp == 'elite':
                if tp == 'elite':
                    flag = com['uts']
                del(com['uts'])
                items.append(com)
        if tp == 'latest' and int(flag) + FALL_PER_PAGE_NUM < total_in_search:
            data['flag'] = str(int(flag) + FALL_PER_PAGE_NUM)
        elif tp == 'elite':
            data['flag'] = str(flag)
        else:
            num = len(ids)
            if num >= FALL_PER_PAGE_NUM:
                data['flag'] = str(flag + num)
        data['items'] = items
        return '', data

# 每日精选 帖子


@view_defaults(route_name='choiceness_threads')
class ChoicenessThreadsView(View):

    def __init__(self, request):
        super(ChoicenessThreadsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_new_forum_threads.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        if not flag:
            flag = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        thread_ids = get_thread_choiceness_ids(flag, FALL_PER_PAGE_NUM * 2)
        data = {}
        data['items'] = []
        for id in thread_ids:
            com = build_choiceness_thread_by_item(id)
            if not com:
                continue
            flag = com['component']['flag']
            del(com['component']['flag'])
            if com:
                data['items'].append(com)
        # if len(thread_ids) >= FALL_PER_PAGE_NUM:
        #    data['flag'] = flag
        return '', data


# 6.4.0 社区首页热门,关注，设计师，明星等tab接口
@view_defaults(route_name='new_forum_hots')
class NewForumHotsView(View):

    def __init__(self, request):
        super(NewForumHotsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_new_forum_hots.get')
    @check_permission
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        flag = self.request.params.get('flag', '')
        user_id = self.user_id
        nav_id = self.request.params.get('nav_id', '')
        nav_name = self.request.params.get('nav_name', '热门')
        is_top = False
        is_search = False
        if flag == '':
            is_top = True
            flag = 0
        elif flag == 't':
            flag = 0
        elif flag.startswith('t'):
            is_top = True
            flag = int(flag[1:])
        elif flag.startswith('s'):
            is_search = True
            flag = int(flag[1:])
        data = {}
        items = []
        with_top_icon = 0
        without_icon = 1
        support_topic = 1
        support_webp = 1
        support_pic = 1
        _top_ids = []
        top_ids = []
        ids = []
        post_ids = []
        com_type = 'cell'
        flag = int(flag) if flag else 0
        if nav_name == '热门':
            if is_top:
                top_ids = get_recommend_thread_ids(flag)
                num = len(top_ids)
                if num >= FALL_PER_PAGE_NUM:
                    data['flag'] = 't' + str(flag + FALL_PER_PAGE_NUM)
            else:
                ids = get_hot_thread_ids(flag, FALL_PER_PAGE_NUM)
                num = len(ids)
                if num >= FALL_PER_PAGE_NUM:
                    data['flag'] = str(ids[-1].get_id())
        elif nav_name == '关注':
            if is_top:
                coms = get_banner_components_by_flags_key_cache(TAB_NAME_BANNER_DICT.get(nav_name), com_type)
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
            following_user_ids = []
            if user_id:
                following_user_ids = get_following_user_ids_by_user_id(user_id)
            if following_user_ids:
                following_user_ids.append(user_id)
                post_ids = get_post_ids_by_user_ids(following_user_ids, flag)
                if not post_ids:
                    items.append(ui)
                    top_ids = get_home_recommend_thread_ids_by_nav_id(nav_id, flag)
                    if len(top_ids) >= FALL_PER_PAGE_NUM:
                        data['flag'] = str(int(flag) + FALL_PER_PAGE_NUM)
                else:
                    if len(post_ids) >= FALL_PER_PAGE_NUM:
                        data['flag'] = str(int(flag) + FALL_PER_PAGE_NUM)
            else:
                items.append(ui)
                top_ids = get_home_recommend_thread_ids_by_nav_id(nav_id, flag)
                if len(top_ids) >= FALL_PER_PAGE_NUM:
                    data['flag'] = str(int(flag) + FALL_PER_PAGE_NUM) 
        else:
            if TAB_NAME_BANNER_DICT.get(nav_name) and is_top:
                coms = get_banner_components_by_flags_key_cache(TAB_NAME_BANNER_DICT.get(nav_name), com_type)
                com_items = []
                ui = {}
                com_user = {}
                for com in coms:
                    re_com = rebuild_focus_user_components_by_component(com, user_id)
                    if re_com:
                        com_items.append(re_com)
                com_user['componentType'] = 'ForumStarUserCell'
                com_user['focus_users'] = com_items
                com_user['id'] = str(nav_id)
                ui['component'] = com_user
                items.append(ui)
            not_top = True
            if is_top:
                top_ids = get_home_recommend_thread_ids_by_nav_id(nav_id, flag)
                limit = FALL_PER_PAGE_NUM
                if len(top_ids) >= FALL_PER_PAGE_NUM:
                    data['flag'] = 't' + str(int(flag) + FALL_PER_PAGE_NUM)
                    not_top = Flase
                else:
                    if (limit - len(top_ids)) < FALL_PER_PAGE_NUM/2:
                        limit = limit - len(top_ids)
                    data['flag'] = '0'
            if not_top:
                navigator = get_navigator_by_nav_id(nav_id)
                if navigator is None:
                    return '', {}
                limit = FALL_PER_PAGE_NUM
                not_search = True
                if not is_search:
                    if navigator.category_id:
                        user_ids =  get_user_ids_by_cat_id(navigator.category_id)
                        post_ids = get_post_ids_by_user_ids(user_ids,int(flag))
                        if len(post_ids) >= FALL_PER_PAGE_NUM:
                            data['flag'] = str(int(flag) + FALL_PER_PAGE_NUM)
                            not_search = False
                        else:
                            if (limit - len(post_ids)) < FALL_PER_PAGE_NUM/2:
                                limit = limit - len(post_ids)
                            data['flag'] = 's0'
                if not_search:
                    tag = get_tag_by_id(navigator.tag_id)
                    if tag:
                        name = tag.tag
                        if name:
                            result = CoflexAgentClient().search_forum(query=name, offset=flag, limit=limit, search_tags=True)
                            for item in result['items']:
                                if item['type'] == 'threads':
                                    post_ids.append(item['id'])
                            total_threads = result['total']
                            if (int(flag) + FALL_PER_PAGE_NUM) < total_threads:
                                data['flag'] = 's' + str(flag + FALL_PER_PAGE_NUM)
        if top_ids:
            for id in top_ids:
                _type, _id = id
                com = {}
                if _type == 'topic':
                    com = build_topic_list_item_by_id(_id, support_webp, support_pic)
                elif _type == 'theme':
                    com = build_topic_list_item_by_theme_id(_id, support_pic)
                elif _type == 'thread':
                    com = build_lite_post_by_id(_id, user_id, with_top_icon, without_icon, support_webp)
                if com:
                    items.append(com)
        if ids:
            for id in ids:
                _id, _type = id.get_type_id(), id.get_type()
                com = {}
                if _type == 'topic':
                    com = build_topic_list_item_by_id(_id, support_webp,support_pic)
                elif _type == 'theme':
                    com = build_topic_list_item_by_theme_id(_id,support_pic)
                elif _type == 'thread':
                    com = build_lite_post_by_id(_id, user_id, with_top_icon, without_icon, support_webp)
                    if com:
                        com['component']['showIcon'] = 'forum'
                if com:
                    items.append(com)
        if post_ids:
            for post_id in post_ids:
                com = {}
                com = build_lite_post_by_id(post_id, user_id, with_top_icon, without_icon, support_webp)
                if com:
                    com['component']['showIcon'] = 'forum'
                if com:
                    items.append(com)

        data['items'] = items
        return '', data


# v6.4.0获取社区首页导航接口
@view_defaults(route_name='new_forum_navigator')
class NewForumNavigatorView(View):

    def __init__(self, request):
        super(NewForumNavigatorView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_new_forum_navigator.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):
        limit = 10
        data = {}
        data['items'] = get_forum_navigator(limit)
        return '', data


# 标签详情页接口
@view_defaults(route_name='new_forum_tag_threads')
class TagThreadsView(View):

    def __init__(self, request):
        super(TagThreadsView, self).__init__()
        self.request = request

    @statsd.timer('hichao_backend.r_new_forum_tag_threads.get')
    @view_config(request_method='GET', renderer='json')
    @pack_data
    def get(self):

        tag_id = self.request.params.get('tag_id', '')
        flag = self.request.params.get('flag', '')
        need_head = 0
        if flag == '':
            need_head = 1
            flag = 0
        data = {}
        ids = []
        items = []
        total_threads = 0
        with_top_icon = 1
        without_icon = 0
        support_webp = 1
        if need_head:
            data['tagHead'] = build_forum_tag_by_tag_id(tag_id)
            if not data:
                return '', data
        try:
            tag = get_tag_by_id(tag_id)
            if not tag:
                self.error['error'] = 'Arguments missing.'
                self.error['errorCode'] = '10002'
                return u'标签不存在！', {}
            name = tag.tag
            if name:
                result = CoflexAgentClient().search_forum(query=name, offset=flag, limit=FALL_PER_PAGE_NUM + 1, search_tags=True)
                for item in result['items']:
                    if item['type'] == 'threads':
                        ids.append(item['id'])
                total_threads = result['total']
        except Exception as e:
            print 'get_forum latest exception:', e
        for _id in ids:
            com = build_lite_post_by_id(_id, with_top_icon, without_icon, support_webp)
            if com:
                com['component']['showIcon'] = 'forum'
                if com:
                    items.append(com)

        data['items'] = items
        if len(items) >= FALL_PER_PAGE_NUM:
            data['flag'] = str(int(flag) + FALL_PER_PAGE_NUM)
        return '', data
