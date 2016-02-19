# -*- coding:utf-8 -*-

class COMMENT_STATUS():
    class TYPE():
        NORMAL = 1          # 正常
        DELETED = 0         # 已删除
        CENSORING = 2       # 审核中
        UNAPPROVED = 3      # 未通过审核
        REFUSED = 4         # 评论被拒绝
        TOO_FAST = 5        # 评论过频
        HAS_URL = 6         # 不是达人，但评论包含链接。
        EMPTY_CONTENT = 7   # 内容为空

    MSG = {
        TYPE.DELETED : u'该评论已被删除。',
        TYPE.CENSORING : u'该评论正在审核中。',
        TYPE.UNAPPROVED : u'您发布的内容含有违规词语，请修改后发布！',
        TYPE.REFUSED : u'您因违规已经被流放到无人岛！请耐心等待刑满释放吧~',
        TYPE.TOO_FAST : u'不要刷屏太快哦，休息一会儿吧~',
        TYPE.HAS_URL : u'您还不是达人哟，暂时不可以发链接。',
        TYPE.EMPTY_CONTENT : u'内容不能为空哦~',
        }

FLOOR = {
        0:u'楼主',
        1:u'沙发',
        2:u'板凳',
        3:u'地板',
        }

