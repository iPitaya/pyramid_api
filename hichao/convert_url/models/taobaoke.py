# -*- coding:utf-8 -*-

from sqlalchemy import (
        Column,
        INTEGER,
        VARCHAR,
        )
from hichao.convert_url.models.db import (
        Base,
        dbsession_generator,
        )
from hichao.convert_url import CpsType
from hichao.base.models.base_component import BaseComponent
from hichao.cache.cache import deco_cache
from hichao.util.date_util import MONTH
import md5
import urllib2
import urllib
import json
import socket
import time

ttids = {
        None:'400000_12629922@xmxcy_{0}_3.0&sche=mxyc',
        '':'400000_12629922@xmxcy_{0}_3.0&sche=mxyc',
        '32602059':'400000_12629922@xmxcy_{0}_3.0&sche=mxyc',
        '31240926':'400000_12629922@xmxcy_{0}_3.0&sche=mxyc',
        '45661536':'400000_21558078@mxyc4mobile_{0}_2.2&sche=mxyc',
        '45671017':'400000_21558078@mxyc4mobile_{0}_3.0&sche=mxyc',
        '45662325':'400000_21558078@mxyc4mobile_{0}_2.5&sche=mxyc',
        }

def get_pid():
    #pids = ['31240926','32602059','45661536','45662325','31240926','45671017','31240926','32602059','45661536','45662325','31240926','45671017','31240926','45662325','31240926','45671017','31240926','32602059','31240926','45661536',]
    pids = ['31240926','31240926']
    cnt = len(pids)
    index = 0
    while True:
        yield pids[index]
        index = index + 1
        index = index % cnt

next_pid = get_pid().next

class Taobaoke(Base, BaseComponent):
    __tablename__ = 'taobaoke'
    id = Column('taobaoke_id', INTEGER, primary_key = True)
    source_id = Column('source_id', VARCHAR(32))
    source_type = Column('source_type', VARCHAR(32))
    is_web = Column('is_web', INTEGER)
    device_type = Column('device_type', VARCHAR(32))
    taobaoke_url = Column('taobaoke_url', VARCHAR(1024))
    publish_date = Column('publish_date', VARCHAR(32))
    pid = Column('pid', VARCHAR(32))

def get_taobaoke_url(source_id, device_type = CpsType.IPHONE, source_type = 'tmall'):
    DBSession = dbsession_generator()
    url = DBSession.query(Taobaoke.taobaoke_url, Taobaoke.pid).filter(Taobaoke.device_type == device_type).filter(Taobaoke.source_type
            == source_type).filter(Taobaoke.source_id == str(source_id)).first()
    DBSession.close()
    return url


@deco_cache(prefix = 'taobaoke', recycle = MONTH)
def getTaobaoURL(source_id, imei, imsi, device_type = CpsType.IPHONE, use_cache = True):
    #首先在taobaoke数据库里面去取taobaokeurl
    clicked_url = get_taobaoke_url(source_id, device_type)
    if clicked_url:
        if clicked_url[1]:
            clicked_url = clicked_url[0] + '&ttid=' + ttids.get(clicked_url[1], ttids[None]).format(device_type)
        else:
            clicked_url = clicked_url[0] + '&ttid=' + ttids[None].format(device_type)
    #comment 访问taobaoke的逻辑
    else:
        pid = next_pid()
        clicked_url = None
        print "access taobaoke server..."
        requestURLHeader = "http://gw.api.taobao.com"
        requestRouter = "/router/rest?"
        ts = getFormatedDate()
        if device_type == CpsType.IPAD:
            app_key = '12629922'
        else:
            app_key = '21558078'
        params = "app_key={0}&fields=click_url&format=json&method=taobao.tbk.mobile.items.convert&num_iids={1}&outer_code=default&partner_id=top-apitools&pid={2}&sign_method=md5&timestamp={3}&v=2.0".format(app_key, source_id, pid, ts)
        sign = createSign(params)

        params = "sign={0}&{1}".format(sign, params)
        params = urllib.quote(params, "[=&,:]")
        finalURL = "{0}{1}{2}".format(requestURLHeader, requestRouter, params)
        jsonResponse = getURLContent(finalURL)
        clicked_url = mobileUnpack(jsonResponse, source_id, imei, imsi, device_type, pid)
        if not clicked_url:
            clicked_url = handleProductURL(None, source_id, imei, imsi, device_type, pid)
    return clicked_url.replace('&unid=default', '')

def mobileUnpack(jsonResponse, source_id, imei, imsi, device_type, pid):
    if jsonResponse.has_key("tbk_mobile_items_convert_response"):
        ticr = jsonResponse['tbk_mobile_items_convert_response']
        if ticr.has_key('tbk_items'):
            url_array = ticr['tbk_items']
            if url_array and url_array.has_key('tbk_item'):
                clicked_url = url_array['tbk_item'][0]['click_url']
                if clicked_url:
                    clicked_url = handleProductURL(clicked_url, 0, imei, imsi, device_type, pid)
                else:
                    clicked_url = handleProductURL(clicked_url, source_id, imei, imsi, device_type, pid)
                return clicked_url
    return ''

def handleProductURL(url, source_id, imei, imsi, device_type, pid):
    ttid = ttids[pid].format(device_type)
    if source_id:
        url = "http://item.taobao.com/item.html?id={0}".format(source_id)
    sid = "t{0}".format(imei)
    suffixObj = {}
    #suffixObj["ttid"] = ttid
    suffixObj["imei"] = imei
    suffixObj["imsi"] = imsi
    suffixObj["sid"] = sid
    suffix = urllib.urlencode(suffixObj)
    #return "{0}&ttid={1}&imei={2}&imsi={3}&sid={4}".format(url, ttid, imei, imsi, sid)
    return "{0}&{1}&{2}".format(url, suffix, ttid)

def getURLContent(url):
    socket.setdefaulttimeout(2)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    jsonResponse = json.loads(response.read())
    return jsonResponse

def createSign(params):
    secretKey = "61b3ae96898f22770a4e898dafde958b"
    nparams = "{0}{1}{2}".format(secretKey, params, secretKey)
    nparams = nparams.replace("=", "").replace("&", "")
    m = md5.new()
    m.update(nparams)
    #md5转换成大写
    return m.hexdigest().upper()

def getFormatedDate():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

