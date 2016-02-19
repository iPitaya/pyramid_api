# -*- coding:utf-8 -*-

class BaseComponent(object):
    def __init__(self):
        pass

    def get_component_id(self):
        raise Exception('Object is NOT available.')

    def get_component_pic_url(self):
        raise Exception('Object is NOT available.')

    def get_component_content(self):
        raise Exception('Object is NOT available.')

    def get_component_price(self):
        raise Exception('Object is NOT available.')

    def get_component_year(self):
        raise Exception('Object is NOT available.')

    def get_component_month(self):
        raise Exception('Object is NOT available.')

    def get_component_day(self):
        raise Exception('Object is NOT available.')

    def get_component_week_day(self):
        raise Exception('Object is NOT available.')

    def get_component_show_time(self):
        raise Exception('Object is NOT available.')

    def get_component_color_all(self):
        raise Exception('Object is NOT available.')

    def get_component_color_time(self):
        raise Exception('Object is NOT available.')

    def get_component_title(self):
        raise Exception('Object is NOT available.')

    def get_component_description(self):
        raise Exception('Object is NOT available.')

    def get_component_top_pic_url(self):
        raise Exception('Object is NOT available.')

    def get_component_collection_count(self):
        raise Exception('Object is NOT available.')

    def get_component_web_url(self):
        raise Exception('Object is NOT available.')

    def get_component_word(self):
        raise Exception('Object is NOT available.')

    def get_component_user_avatar(self):
        raise Exception('Object is NOT available.')

    def get_conponent_user_name(self):
        raise Exception('Object is NOT available.')

    def get_component_publish_date(self):
        raise Exception('Object is NOT available.')

    def get_component_width(self):
        return '100'

    def get_component_height(self):
        return '100'

    def get_component_drop_width(self):
        return '100'

    def get_component_drop_height(self):
        return '150'

    def get_component_common_pic_url(self):
        raise Exception('Object is NOT available.')

    def to_component(self):
        raise Exception('Object is NOT available.')

    def to_ui_action(self):
        raise Exception('Object is NOT available.')

    def to_lite_ui_action(self):
        return {}

    def get_cache_key(self):
        raise Exception('Object is NOT available.')

