#encoding:utf8

def get_test_topic():
    topic = {}
    topic["message"] = ""
    topic["data"] = get_test_topic_data()
    return topic

def get_test_topic_component():
    component = {}
    com = {}
    com['componentType'] = 'topic'
    com['day'] = '10'
    com['description'] = '测试专题'
    com['month'] = '05'
    com['picUrl'] = 'http://www.baidu.com/img/shouye_b5486898c692066bd2cbaeda86d74448.gif'
    com['title'] = '专题5000'
    com['topPicUrl'] = ''
    com['weekDay'] = '星期五'
    com['year'] = '2013'
    com['action'] = {}
    com['action']['actionType'] = 'topicDetail'
    com['action']['id'] = '5000'
    com['action']['title'] = '测试标题'
    component['component'] = com
    return component

def get_test_topic_data():
    data = {}
    data["nextTitle"] = ""
    data["prevTitle"] = ""
    data["appApi"] = ""
    data["nextId"] = ""
    data["prevId"] = ""
    data["sharePicUrl"] = ""
    data["title"] = "test"
    data["items"] = get_test_topic_data_items()
    return data

fixed_height = 80
fixed_cell_height = 100
fixed_width = 200

def get_common_cell_(cells):
    cells['x'] = "0"
    cells['y'] = "0"
    cell = {}
    cell['height'] = str(fixed_cell_height)
    cell['cells'] = []
    cell['cells'].append(cells)
    return cell

def get_test_topic_data_items():
    items = []
    items.append(get_common_cell_(get_cell(1)))
    items.append(get_common_cell_(get_video_cell(2)))
    items.append(get_common_cell_(get_word_cell(3)))
    items.append(get_common_cell_(get_price_decorated_cell(4)))
    items.append(get_common_cell_(get_calendar_cell(5)))
    items.append(get_common_cell_(get_hangtag_cell(6)))
    items.append(get_common_cell_(get_topic_cell(7)))
    items.append(get_common_cell_(get_link_decorated_cell(8)))
    items.append(get_common_cell_(get_water_fall_star_cell(9)))
    items.append(get_common_cell_(get_webview_cell(10)))
    items.append(get_common_cell_(get_search_cell(11)))
    items.append(get_common_cell_(get_search_star_cell(12)))
    items.append(get_common_cell_(get_item_cell(13)))
    items.append(get_common_cell_(get_comment_cell(14)))

    items.append(get_common_cell_(get_topic_detail_action(15)))
    items.append(get_common_cell_(get_star_detail_action(16)))
    items.append(get_common_cell_(get_item_detail_action(17)))
    items.append(get_common_cell_(get_search_word_action(18)))
    items.append(get_common_cell_(get_search_star_action(19)))
    items.append(get_common_cell_(get_webview_action(20)))
    items.append(get_common_cell_(get_toast_action(21)))
    items.append(get_common_cell_(get_dialog_action(22)))
    items.append(get_common_cell_(get_video_action(23)))
    items.append(get_common_cell_(get_show_big_pic_action(25)))

    items.append(get_common_cell_(get_weixin_share_text_action(24)))
    items.append(get_common_cell_(get_weixin_share_img_action(26)))
    items.append(get_common_cell_(get_weixin_share_appdata_action(27)))
    items.append(get_common_cell_(get_weixin_share_webpage_action(28)))

    items.append(get_common_cell_(get_webview_push_action(29)))
    items.append(get_common_cell_(get_webview_browser_action(30)))

    return items


def get_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "cell",
            "action": {},
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_video_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "videoCell",
            "action": {},
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_word_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "action": {},
            "content": "word cell 的测试"
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_price_decorated_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "priceDecoratedCell",
            "action": {
                "normalPicUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
                "originLink": "http://item.taobao.com/item.htm?id=17177986482",
                "description": "\u4e3b\u56fe\u6765\u6e90:\u5176\u4ed6\u5206\u9500\u56fe|\u8d27\u53f7:18E11LGRN|\u98ce\u683c:\u8857\u5934|\u8857\u5934:\u6b27\u7f8e|\u88d9\u957f:\u77ed\u88d9(76-90\u5398\u7c73)|\u8896\u957f:\u65e0\u8896/\u80cc\u5fc3\u88d9|\u5973\u88c5\u9886\u578b:\u5706\u9886|\u8170\u578b:\u9ad8\u8170|\u56fe\u6848:\u7eaf\u8272|\u54c1\u724c:MISS SELFRIDGE|\u989c\u8272\u5206\u7c7b:\u6d45\u7eff\u8272|\u5c3a\u7801:XS S M L XL XXL",
                "price": "685.00",
                "channelPicUrl": "http://img1.haobao.com/images/images/20130131/5e508696-c0e3-4924-a174-3c666fa0c00e.png",
                "link": "http://item.taobao.com/item.htm?id=17177986482",
                "actionType": "itemDetail",
                "id": "1542849"
            },
            "price": "685.00",
            "picUrl": "http://img2.haobao.com/images/navigate/dihu_1366774098241_navigate.jpg"
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_calendar_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "calendar",
            "action": {},
            "month": "05",
            "day": "11",
            "weekDay": "周五",
            "showTime": "11:00",
            "backgroundUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
            "monthColor": "100, 212, 0, 1",
            "dayColor": "100, 212, 0, 1",
            "weekDayColor": "100, 212, 0, 1",
            "weekDayBgUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
            "showTimeColor": "100, 212, 0, 1",
            "publishColor": "100, 212, 0, 1"
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_hangtag_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "hangtag",
            "action": {},
            "picUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
            "month": "05",
            "day": "11",
            "weekDay": "周五",
            "showTime": "11:00",
            "backgroundUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
            "monthColor": "100, 212, 0, 1",
            "dayColor": "100, 212, 0, 1",
            "weekDayColor": "100, 212, 0, 1",
            "weekDayBgUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
            "showTimeColor": "100, 212, 0, 1",
            "publishColor": "100, 212, 0, 1"
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_topic_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "topic",
            "action": {},
            "title": "test",
            "description": "test",
            "topPicUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
            "picUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
            "topPicUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
            "year": "2013",
            "month": "05",
            "day": "11",
            "weekDay": "星期五",
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_link_decorated_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "linkDecoratedCell",
            "action": {},
            "picUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_water_fall_star_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "waterfallStarCell",
            "action": {},
            "picUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
            "itemsCount": "4",
            "description": "waterfallStarCell",
            "collectionCount": "100",
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_webview_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "webview",
            "action": {},
            "webUrl": "http://www.baidu.com",
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_search_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "search",
            "action": {},
            "picUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
            "word": "搜索接口"
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_search_star_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "searchStar",
            "action": {},
            "picUrl": "http://img2.haobao.com/images/images/91/83/2/hmy_1366740780524_wnormal.jpg",
            "word": "赵雅芝",
            "starCount": "100",
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_item_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "item",
            "action": {},
            "picUrl": "http://img1.haobao.com/images/images/20130131/5e508696-c0e3-4924-a174-3c666fa0c00e.png",
            "price": "100.0",
            "description": "item cell",
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_comment_cell(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "comment",
            "action": {},
            "userAvatar": "http://img1.haobao.com/images/images/20130131/5e508696-c0e3-4924-a174-3c666fa0c00e.png",
            "userName": "赵雅芝",
            "floor": "18",
            "content": "comment cell",
            "picUrl": "http://img1.haobao.com/images/images/20130131/5e508696-c0e3-4924-a174-3c666fa0c00e.png",
            "publishDate": "3月10日",
        },
        "x": "9.0",
        "height": str(fixed_height)
    }
    return cell

def get_topic_detail_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"去专题",
            "action": {
                "actionType": "topicDetail",
                "id": "330",
                "title": "detail action",
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_star_detail_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"去明星图",
            "action": {
                "userName": "\u84dd\u8272\u6ef4\u6c14\u6ce1",
                "normalPicUrl": "http://mxyc.qiniudn.com/images/images/38/41/35/ngmp_1366466119072_star_wnormal.jpg",
                "videoUrl": "",
                "description": "\u5434\u5343\u8bed\uff0c\u51fa\u5e2d\u67d0\u6d3b\u52a8\uff0cChlo\u00c9 \u8377\u53f6\u9886\u65e0\u8896\u8fde\u8863\u88d9+\u767d\u8272\u5c16\u5934\u4e00\u5b57\u5e26\u4e2d\u8ddf\u978b+\u649e\u8272\u624b\u62ff\u5305",
                "title": "",
                "userId": "12",
                "height": "890",
                "width": "559",
                "actionType": "starDetail",
                "itemPicUrlList": [{
                        "picUrl": "http://img2.haobao.com/images/images/42/4/54/uds_1366282684131_normal.jpg"
                    }, {
                        "picUrl": "http://img1.haobao.com/images/images/85/96/99/orw_1366705318600_normal.jpg"
                    }, {
                        "picUrl": "http://img2.haobao.com/images/images/84/87/1/pvw_1366705315517_normal.jpg"
                    }
                ],
                "userPicUrl": "http://img2.haobao.com/images/images/60/45/19/cga_133699423394_avatar.jpg",
                "dateTime": "4\u670827\u65e516\u70b9",
                "id": "30815",
                "collectionCount": "0"
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_item_detail_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"去单品",
            "action": {
                "normalPicUrl": "http://mxyc.qiniudn.com/images/images/98/30/26/gaw_1352399499954_wnormal.jpg",
                "originLink": "http://detail.tmall.com/item.htm?id=13600958058",
                "description": "\u4e3b\u56fe\u6765\u6e90:\u81ea\u4e3b\u5b9e\u62cd\u56fe|\u54c1\u724c:Fashion Line|\u8d27\u53f7:Y9645|\u677f\u578b:\u76f4\u7b52\u578b|\u98ce\u683c:\u8857\u5934|\u8857\u5934:\u6b27\u7f8e|\u8863\u957f:\u4e2d\u957f\u6b3e(65cm<\u8863\u957f\u226480cm)|\u8896\u957f:\u957f\u8896|\u9886\u5b50:\u7ffb\u9886/POLO\u9886|\u8896\u578b:\u5e38\u89c4\u8896|\u8863\u95e8\u895f:\u53cc\u6392\u6263|\u56fe\u6848:\u7eaf\u8272|\u6d41\u884c\u5143\u7d20/\u5de5\u827a:\u53e3\u888b \u80a9\u7ae0 \u7ebd\u6263|\u9762\u6599\u6750\u8d28:\u5176\u5b83|\u9762\u6599\u4e3b\u6750\u8d28\u542b\u91cf:51%-70%|\u91cc\u6599\u56fe\u6848:\u7eaf\u8272|\u91cc\u6599\u6750\u8d28:\u6da4\u7eb6|\u9002\u5408\u4eba\u7fa4\u5e74\u9f84\u6bb5:18-24\u5c81|\u5973\u88c5\u4ef7\u683c\u533a\u95f4:151-300|\u5e74\u4efd:2012\u51ac\u5b63|\u989c\u8272\u5206\u7c7b:\u519b\u7eff\u8272 \u5de7\u514b\u529b\u8272 \u6d45\u9ec4\u8272 \u7ea2\u8272 \u84dd\u8272 \u9152\u7ea2\u8272 \u9ed1\u8272|\u5c3a\u7801:\u5747\u7801 XS S M L XL XXS XXXL XXL",
                "price": "213.00",
                "channelPicUrl": "http://img1.haobao.com/images/images/20130131/69a49c3f-1ceb-4364-80f0-98ba30fed65c.png",
                "link": "http://detail.tmall.com/item.htm?id=13600958058",
                "actionType": "itemDetail",
                "id": "1067858",
                "collectionCount": "45"
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_search_word_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"去搜索热词",
            "action": {
                "actionType": "searchWord",
                "query": "连衣裙"
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_search_star_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"去搜索明星",
            "action": {
                "actionType": "searchStar",
                "query": "赵雅芝"
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_webview_action(row):
    '''
    means = pop, push, browser
    '''
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"pop webview",
            "action": {
                "actionType": "webview",
                "webUrl": "http://www.baidu.com",
                "title": "webveiw action",
                "means": "pop",
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_webview_push_action(row):
    '''
    means = pop, push, browser
    '''
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"push webview",
            "action": {
                "actionType": "webview",
                "webUrl": "http://www.baidu.com",
                "title": "webveiw action",
                "means": "push",
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_webview_browser_action(row):
    '''
    means = pop, push, browser
    '''
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"browser webview",
            "action": {
                "actionType": "webview",
                "webUrl": "http://www.baidu.com",
                "title": "webveiw action",
                "means": "browser",
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_toast_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"弹出toast",
            "action": {
                "actionType": "toast",
                "message": "这是什么toast动作"
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_dialog_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"弹出dialog",
            "action": {
                "actionType": "dialog",
                "callbackUrl": "http://hichao.com",
                "title": "dialog action",
                "params": [
                    {
                        'name': '显示在左侧栏的文字',
                        'value': '回写在input中的文字',
                        'key': 'post提交时的key',
                    },
                ],
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_video_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"打开视频",
            "action": {
                "actionType": "video",
                "videoUrl": "http://img2.haobao.com/images/video/20130313/44053985-8bbf-4b8e-ad5c-ee8129944362.mp4",
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_weixin_share_text_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"微信分享",
            "action": {
                "actionType": "share",
                'typeId':'text_share',
                'type':'test_topic',
                'trackValue':'test_topic_text_share',
                "share":{
                    "shareType": "text",
                    "title":"微信的文本分析",
                    "description":"微信的文本分析",
                }
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_weixin_share_text_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"微信分享text",
            "action": {
                "actionType": "share",
                'typeId':'text_action',
                'type':'test_topic',
                'trackValue':'test_topic_text_action',
                "share":{
                    "shareType": "text",
                    "title":"微信的文本分析",
                    "description":"微信的文本分析",
                },
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_weixin_share_img_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"微信分享img",
            "action": {
                "actionType": "share",
                'typeId':'img_action',
                'type':'test_topic',
                'trackValue':'test_topic_img_action',
                "share": {
                    "shareType": "img",
                    "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
                },
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_weixin_share_appdata_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"微信分享appdata",
            "action": {
                "actionType": "share",
                'typeId':'app_share',
                'type':'test_topic',
                'trackValue':'test_topic_app_share',
                "share": {
                    "shareType": "appdata",
                    "title": "微信分享appdata",
                    "description": "微信分享appdata",
                    "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg",
                    "params": '{"actionType": "topicDetail", "id": "384", "title": "\\\\u300a\\\\u4e2d\\\\u56fd\\\\u5408\\\\u4f19\\\\u4eba\\\\u300b\\\\u89c1\\\\u8bc1\\\\u540a\\\\u4e1d\\\\u9006\\\\u88ad"}',
                },
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

def get_weixin_share_webpage_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"微信分享webpage",
            "action": {
                "actionType": "share",
                'typeId':'webpage_action',
                'type':'test_topic',
                'trackValue':'test_topic_webpage_action',
                "share": {
                    "shareType": "webpage",
                    "title": "微信分享webpage",
                    "description": "微信分享webpage",
                    "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg",
                    "detailUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg",
                },
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell
def get_show_big_pic_action(row):
    row -= 1
    cell = {
        "y": str(row * fixed_height),
        "width": str(fixed_width),
        "component": {
            "componentType": "word",
            "content":u"看大图",
            "action": {
                "actionType": "showBigPic",
                "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg",
                "noSaveButton": "1",
            },
            "picUrl": "http://img2.haobao.com/images/navigate/fvae_1366796095474_navigate.jpg"
        },
        "x": "0.0",
        "height": str(fixed_height)
    }
    return cell

