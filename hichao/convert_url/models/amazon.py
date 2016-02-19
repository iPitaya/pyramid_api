# -*- coding:utf-8 -*-

def get_amazon_url(source_id, info = {}):
    if info and info.has_key('m'):
        return "http://www.amazon.cn/gp/product/{0}/ref=as_li_tf_tl?ie=UTF8&camp=536&creative=3200&creativeASIN={1}&linkCode=as2&tag=mxyc-23&m={2}".format(source_id, source_id, info['m'])
    else:
        return "http://www.amazon.cn/gp/product/{0}/ref=as_li_tf_tl?ie=UTF8&camp=536&creative=3200&creativeASIN={1}&linkCode=as2&tag=mxyc-23".format(source_id, source_id)

