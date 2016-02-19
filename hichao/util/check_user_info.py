# -*- coding:utf-8 -*-

from hichao.base.config import WINNER_INFO_FORM, WINNER_SHOW_CELL
from hichao.winner_info.models.winner_list import get_winner_list
from hichao.winner_info.models.user_activity_info import get_user_activity_info
from hichao.winner_info.models.topic_winner_attachinfo import get_winner_attachinfo
import functools
import copy

def check_user_info(func):
    @functools.wraps(func)
    def _(topic_id, user_id, width, txt_with_margin, lite_thread, lite_action, support_webp, support_ec, use_cache = True):
        data = func(topic_id, user_id, width, txt_with_margin, lite_thread, lite_action, support_webp, support_ec, use_cache = use_cache)
        if data and data['is_activity']:
            user_info = None
            user_attachment = None
            if user_id > 0:
                user_info = get_user_activity_info(user_id)
                user_attachment = get_winner_attachinfo(topic_id, user_id)
            winner_form = copy.deepcopy(WINNER_INFO_FORM)
            if user_info:
                for item in winner_form['params']:
                    if item['key'] != 'attachment':
                        item['value'] = getattr(user_info, item['key'])
                    else:
                        if user_attachment:
                            item['value'] = user_attachment.attachment
            winner_form['typeId'] = str(topic_id)
            winner_form['type'] = 'topic'
            winner_form['trackValue'] = 'topic_{0}_dialog'.format(topic_id)
            if str(user_id) in get_winner_list(topic_id):
                first_row = copy.deepcopy(WINNER_SHOW_CELL)
                first_cell = first_row['cells'][0]
                first_cell['component']['action'] = winner_form
                prop = int(width)/320
                first_cell['height'] = str(first_cell['height'] * prop)
                first_cell['width'] = str(first_cell['width'] * prop)
                first_cell['x'] = str(first_cell['x'] * prop)
                first_cell['y'] = str(first_cell['y'] * prop)
                data['items'].insert(0, first_row)
            items = data['items']
            for item in items:
                cells = item['cells']
                for cell in cells:
                    if cell['component'].get('tag', '') == 'trial':
                        del(cell['component']['tag'])
                        cell['component']['action'] = winner_form
            del(data['is_activity'])
        return data
    return _

